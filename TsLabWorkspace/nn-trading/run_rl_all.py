"""Walk-forward with DQN RL agent for BTC + 10 instruments."""
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
import torch; torch.set_num_threads(2)

import json, numpy as np, pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from rl_agent import train_dqn, evaluate_dqn
from features_all import load_btc_8tf, load_instrument_3tf
from features import make_label


def prepare_features(df, max_features=80):
    exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
    cols = [c for c in df.columns if c not in exclude and df[c].dtype in [np.float64, np.float32, np.int64]]
    df_clean = df[cols].copy()
    df_clean = df_clean.replace([np.inf, -np.inf], np.nan).fillna(0)
    return df_clean


def walk_forward_rl(df, name, n_folds=5, window=30, min_confidence=0.6):
    from features import make_label
    df["label"] = make_label(df, 5, 0.001)
    df = df.dropna()

    features_df = prepare_features(df)
    prices = df["Close"].values.astype(np.float64)
    feature_cols = features_df.columns.tolist()
    features = features_df.values.astype(np.float32)

    # Scale features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    total = len(df)
    test_size = total // (n_folds + 1)
    min_train = total // (n_folds + 1)

    fold_results = []
    equity_parts = []

    for fold in range(n_folds):
        train_end = min_train + fold * test_size
        test_start = train_end
        test_end = min(test_start + test_size, total)
        if test_end <= test_start:
            break

        print(f"  Fold {fold+1}/{n_folds} | train:0-{train_end} test:{test_start}-{test_end}")

        # Train DQN on training data
        train_prices = prices[:train_end]
        train_features = features_scaled[:train_end]

        agent = train_dqn(
            train_prices, train_features, window=window,
            episodes=30, commission=0.001, stop_loss=0.03, take_profit=0.09,
            min_confidence=min_confidence, n_cpu=2, quiet=True,
        )

        # Evaluate on test data
        test_prices = prices[test_start - window:test_end]
        test_features = features_scaled[test_start - window:test_end]

        result = evaluate_dqn(
            agent, test_prices, test_features, window=window,
            commission=0.001, stop_loss=0.03, take_profit=0.09,
            min_confidence=min_confidence,
        )

        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

        print(f"    Return: {result['total_return_pct']:+.2f}% | "
              f"Trades: {result['n_trades']} | Win: {result['win_rate_pct']:.0f}%")

        fold_results.append({
            "fold": fold + 1,
            "return": round(result["total_return_pct"], 2),
            "trades": result["n_trades"],
            "win_rate": round(result["win_rate_pct"], 1),
        })

    eq = np.concatenate(equity_parts) if equity_parts else np.array([1.0])
    total_ret = (eq[-1] / eq[0] - 1) * 100
    max_dd = ((eq / np.maximum.accumulate(eq)) - 1).min() * 100
    avg_win = np.mean([r["win_rate"] for r in fold_results]) if fold_results else 0
    total_trades = sum(r["trades"] for r in fold_results)

    # Sharpe
    returns = np.diff(eq) / eq[:-1]
    sharpe = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(365)

    return {
        "instrument": name,
        "total_return": round(total_ret, 2),
        "max_drawdown": round(max_dd, 2),
        "total_trades": total_trades,
        "avg_win_rate": round(avg_win, 1),
        "sharpe": round(sharpe, 2),
        "folds": fold_results,
    }


def main():
    all_results = []

    # BTC with 8 timeframes
    print("=" * 60)
    print("BTC (8 timeframes + RL)")
    print("=" * 60)
    btc = load_btc_8tf()
    result = walk_forward_rl(btc, "Bitcoin", n_folds=3, window=30, min_confidence=0.6)
    all_results.append(result)

    # 10 instruments with 3 timeframes
    instruments = [
        ("NEARUSDT", "NEAR"), ("XLMUSDT", "XLM"), ("SOLUSDT", "SOL"),
        ("AAVEUSDT", "AAVE"), ("LINKUSDT", "LINK"), ("SUIUSDT", "SUI"),
        ("ADAUSDT", "ADA"), ("BCHUSDT", "BCH"), ("TRXUSDT", "TRX"),
        ("UNIUSDT", "UNI"),
    ]

    for sym, name in instruments:
        print(f"\n{'=' * 60}")
        print(f"{name} (3 timeframes + RL)")
        print("=" * 60)
        try:
            df = load_instrument_3tf(sym)
            if len(df) < 200:
                print(f"  Skip: only {len(df)} bars")
                continue
            result = walk_forward_rl(df, name, n_folds=3, window=30, min_confidence=0.6)
            all_results.append(result)
        except Exception as e:
            print(f"  Error: {e}")

    # Summary
    print(f"\n{'=' * 60}")
    print("FINAL RESULTS (DQN RL + Multi-Timeframe)")
    print("=" * 60)

    profitable = []
    for r in all_results:
        status = "PROFIT" if r["total_return"] > 0 else "LOSS"
        print(f"  {r['instrument']:8s} | {r['total_return']:+8.2f}% | DD={r['max_drawdown']:+.2f}% | "
              f"Win={r['avg_win_rate']:.0f}% | Trades={r['total_trades']:4d} | Sharpe={r['sharpe']:+.2f} | {status}")
        if r["total_return"] > 0:
            profitable.append(r)

    if profitable:
        avg_ret = np.mean([r["total_return"] for r in profitable])
        print(f"\nProfitable instruments: {len(profitable)}/{len(all_results)}")
        print(f"Avg return (profitable): {avg_ret:+.2f}%")
    else:
        print("\nNo profitable instruments found")

    with open("results/rl_walkforward_results.json", "w") as f:
        json.dump({"instruments": all_results, "profitable": [r["instrument"] for r in profitable]}, f, indent=2)

    print(f"\nSaved to results/rl_walkforward_results.json")


if __name__ == "__main__":
    main()
