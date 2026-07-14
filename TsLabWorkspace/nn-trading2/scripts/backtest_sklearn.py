"""Fast backtest with sklearn models only (no neural networks)."""
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import json, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from features import compute_all_features, make_label, auto_select_features


def train_sklearn_model(model, X_train, y_train, X_val, y_val):
    model.fit(X_train, y_train)
    train_acc = accuracy_score(y_train, model.predict(X_train))
    val_acc = accuracy_score(y_val, model.predict(X_val))
    return model, train_acc, val_acc


def backtest_instrument(sym, name, n_folds=3):
    # Find data file
    candidates = [
        f"data/{sym}_1h.csv",
        f"data/{sym}_1d.csv",
    ]

    df = None
    for path in candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            break

    if df is None:
        print(f"  No data found for {sym}")
        return None

    # Compute features
    df = compute_all_features(df)
    df["label"] = make_label(df, horizon=5, threshold=0.001).values
    df = df.dropna()

    # Select features
    feature_cols = auto_select_features(df, df["label"], max_features=20)
    print(f"  Using {len(feature_cols)} features")

    # Prepare data
    X = df[feature_cols].values
    y = df["label"].values

    # Walk-forward
    total = len(X)
    test_size = total // (n_folds + 1)
    min_train = total // (n_folds + 1)
    embargo = 7

    equity = [1.0]
    trades = []
    all_preds = []

    for fold in range(n_folds):
        train_end = min_train + fold * test_size
        test_start = train_end + embargo
        test_end = min(test_start + test_size, total)
        if test_end <= test_start:
            break

        X_train, y_train = X[:train_end], y[:train_end]
        X_test, y_test = X[test_start:test_end], y[test_start:test_end]

        # Scale
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train models
        models = [
            ("RF", RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=1)),
            ("GB", GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)),
        ]

        predictions = []
        for model_name, model in models:
            model, train_acc, val_acc = train_sklearn_model(
                model, X_train_scaled, y_train, X_test_scaled, y_test
            )
            preds = model.predict(X_test_scaled)
            predictions.append(preds)
            print(f"    {model_name}: train_acc={train_acc:.3f} val_acc={val_acc:.3f}")

        # Ensemble prediction (majority vote)
        ensemble_preds = np.round(np.mean(predictions, axis=0)).astype(int)

        # Calculate returns
        test_prices = df["close"].values[test_start:test_end]
        returns = np.diff(test_prices) / test_prices[:-1]
        signals = ensemble_preds[:-1] * 2 - 1  # 0->-1, 1->1

        strategy_returns = signals * returns
        for r in strategy_returns:
            equity.append(equity[-1] * (1 + r * 0.02))  # 2% position size

        # Count trades
        n_trades = np.sum(signals != 0)
        win_trades = np.sum(strategy_returns[signals != 0] > 0)
        win_rate = win_trades / n_trades * 100 if n_trades > 0 else 0

        fold_return = (equity[-1] / equity[-len(strategy_returns)-1] - 1) * 100
        print(f"    Fold {fold+1}: {fold_return:+.2f}% | trades={n_trades} | win={win_rate:.0f}%")

    equity = np.array(equity)
    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100

    # Sharpe
    returns = np.diff(equity) / equity[:-1]
    sharpe = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(365 * 24)

    return {
        "instrument": name,
        "total_return": round(total_return, 2),
        "max_drawdown": round(max_dd, 2),
        "sharpe": round(sharpe, 2),
        "equity_curve": equity.tolist(),
    }


def main():
    instruments = [
        ("BTC_USDT", "BTC"),
        ("ETH_USDT", "ETH"),
    ]

    print("=" * 70)
    print("SKLEARN BACKTEST (RF + GB Ensemble)")
    print("=" * 70)

    all_results = []
    for sym, name in instruments:
        print(f"\n  {name}")
        try:
            result = backtest_instrument(sym, name, n_folds=3)
            if result:
                all_results.append(result)
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

    if not all_results:
        print("\nNo results.")
        return

    print(f"\n{'='*70}")
    print("RESULTS")
    print("=" * 70)
    for r in sorted(all_results, key=lambda x: -x["total_return"]):
        print(f"  {r['instrument']:8s} | {r['total_return']:+7.2f}% | DD={r['max_drawdown']:+.2f}% | Sharpe={r['sharpe']:+.2f}")

    # Portfolio
    if len(all_results) > 1:
        min_len = min(len(r["equity_curve"]) for r in all_results)
        portfolio_eq = np.ones(min_len)
        for r in all_results:
            eq = np.array(r["equity_curve"][:min_len]) / r["equity_curve"][0]
            portfolio_eq += (eq - 1) * 0.5  # 50% each
        port_return = (portfolio_eq[-1] / portfolio_eq[0] - 1) * 100
        port_dd = ((portfolio_eq / np.maximum.accumulate(portfolio_eq)) - 1).min() * 100
        port_sharpe = np.mean(np.diff(portfolio_eq) / portfolio_eq[:-1]) / (np.std(np.diff(portfolio_eq) / portfolio_eq[:-1]) + 1e-8) * np.sqrt(365*24)
        print(f"  {'PORTFOLIO':8s} | {port_return:+7.2f}% | DD={port_dd:+.2f}% | Sharpe={port_sharpe:+.2f}")

    output = {"instruments": [{k:v for k,v in r.items() if k!="equity_curve"} for r in all_results]}
    with open("results/sklearn_backtest.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to results/sklearn_backtest.json")


if __name__ == "__main__":
    main()
