"""Full 3-year backtest for portfolio of 7 profitable instruments."""
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
import torch; torch.set_num_threads(2)

import json, random, numpy as np, pandas as pd
from torch.utils.data import Subset
from config import Config
from dataset import TimeSeriesDataset, auto_select_features
from model import build_model, Ensemble, build_sklearn_models, HybridEnsemble
from train import train
from backtest_v2 import run_backtest_v2, calculate_sharpe, calculate_sortino, calculate_calmar
from features import make_label
from portfolio import load_results


def flatten_ds(ds):
    X, y = [], []
    for i in range(len(ds)):
        x, label = ds[i]
        X.append(x.numpy().flatten())
        y.append(label.item())
    return np.array(X), np.array(y)


def backtest_instrument(sym, name, cfg, n_folds=10):
    """Walk-forward backtest for one instrument."""
    # Load multi-timeframe data
    mtf_path = f"data/binance_{sym}_3tf.csv"
    d1_path = f"data/binance_{sym}_1d.csv"

    if os.path.exists(mtf_path):
        df = pd.read_csv(mtf_path, index_col=0, parse_dates=True)
    else:
        df = pd.read_csv(d1_path, index_col=0, parse_dates=True)

    df["label"] = make_label(df, cfg.horizon, cfg.threshold)
    df = df.dropna()

    exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
    feature_cols = [c for c in df.columns if c not in exclude
                    and df[c].dtype in [np.float64, np.float32, np.int64]
                    and not df[c].isna().all()]
    if len(feature_cols) > cfg.max_features:
        feature_cols = auto_select_features(df, df["label"], max_features=cfg.max_features)

    ds = TimeSeriesDataset(df, cfg.window, feature_cols=feature_cols)
    total = len(ds)
    test_size = total // (n_folds + 1)
    min_train = total // (n_folds + 1)
    seeds = [42 + i * 17 for i in range(cfg.n_models)]

    equity_parts = []
    fold_results = []

    for fold in range(n_folds):
        train_end = min_train + fold * test_size
        test_start = train_end
        test_end = min(test_start + test_size, total)
        if test_end <= test_start:
            break

        full_train = list(range(0, train_end - cfg.window))
        vs = int(len(full_train) * 0.85)
        train_ds = Subset(ds, full_train[:vs])
        val_ds = Subset(ds, full_train[vs:])
        test_ds = Subset(ds, range(test_start - cfg.window, test_end - cfg.window))

        # Train models
        base_models = []
        for seed in seeds:
            torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)
            m = build_model(cfg, len(ds.cols))
            m = train(m, train_ds, val_ds, cfg, "cpu", quiet=True)
            base_models.append(m)

        X_tr, y_tr = flatten_ds(train_ds)
        sklearn_wrappers = build_sklearn_models(X_tr, y_tr, cfg.window, len(ds.cols), n_cpu=2)
        all_sklearn = [w for _, w in sklearn_wrappers]
        ensemble = HybridEnsemble(base_models, all_sklearn)

        r = run_backtest_v2(ensemble, test_ds, df, cfg, "cpu", threshold=0.5,
                           use_trailing_stop=True, trailing_stop_pct=0.015,
                           use_dynamic_sizing=True, start_idx=test_start)

        part = r["equity"].copy()
        if equity_parts: part = part * equity_parts[-1][-1]
        equity_parts.append(part)

        fold_results.append({
            "fold": fold+1, "return": round(r["total_return_pct"], 2),
            "trades": r["n_trades"], "win_rate": round(r["win_rate_pct"], 1),
        })
        print(f"    Fold {fold+1:2d}: {r['total_return_pct']:+7.2f}% | trades={r['n_trades']:3d} | win={r['win_rate_pct']:.0f}%")

    eq = np.concatenate(equity_parts) if equity_parts else np.array([1.0])
    total_ret = (eq[-1]/eq[0]-1)*100
    max_dd = ((eq/np.maximum.accumulate(eq))-1).min()*100
    sharpe = calculate_sharpe(eq)
    sortino = calculate_sortino(eq)
    calmar = calculate_calmar(eq)

    return {
        "instrument": name, "symbol": sym,
        "total_return": round(total_ret, 2),
        "max_drawdown": round(max_dd, 2),
        "total_trades": sum(r["trades"] for r in fold_results),
        "avg_win_rate": round(np.mean([r["win_rate"] for r in fold_results]), 1),
        "sharpe": round(sharpe, 2),
        "sortino": round(sortino, 2),
        "calmar": round(calmar, 2),
        "equity_curve": eq.tolist(),
        "folds": fold_results,
    }


def simulate_portfolio(instrument_results, alloc):
    """Simulate combined portfolio equity curve."""
    # Find shortest equity curve
    min_len = min(len(r["equity_curve"]) for r in instrument_results)
    portfolio_equity = np.ones(min_len)

    for r in instrument_results:
        name = r["instrument"]
        if name not in alloc:
            continue
        pct = alloc[name] / 100
        eq = np.array(r["equity_curve"][:min_len])
        # Normalize to start at 1
        eq = eq / eq[0]
        portfolio_equity += (eq - 1) * pct

    total_ret = (portfolio_equity[-1] / portfolio_equity[0] - 1) * 100
    max_dd = ((portfolio_equity / np.maximum.accumulate(portfolio_equity)) - 1).min() * 100
    sharpe = calculate_sharpe(portfolio_equity)
    sortino = calculate_sortino(portfolio_equity)
    calmar = calculate_calmar(portfolio_equity)

    return {
        "total_return": round(total_ret, 2),
        "max_drawdown": round(max_dd, 2),
        "sharpe": round(sharpe, 2),
        "sortino": round(sortino, 2),
        "calmar": round(calmar, 2),
        "equity_curve": portfolio_equity.tolist(),
    }


def main():
    # Load portfolio allocation
    alloc_path = Path("results/portfolio_allocation.json")
    if alloc_path.exists():
        with open(alloc_path) as f:
            alloc = json.load(f).get("allocation", {})
    else:
        alloc = {}

    # 5 instruments (skip ETH/SOL2 - use existing results)
    instruments = [
        ("SOLUSDT", "SOL"), ("XLMUSDT", "XLM"), ("BCHUSDT", "BCH"),
        ("AAVEUSDT", "AAVE"), ("NEARUSDT", "NEAR"),
    ]

    all_results = []
    cfg = Config()
    cfg.hidden_size = 32; cfg.num_layers = 2; cfg.dropout = 0.35
    cfg.window = 30; cfg.batch_size = 64; cfg.learning_rate = 0.0002
    cfg.n_models = 3; cfg.max_features = 40
    cfg.stop_loss_pct = 0.03; cfg.take_profit_pct = 0.07
    cfg.n_cpu_threads = 2

    print("=" * 70)
    print("FULL 3-YEAR BACKTEST: 7 Profitable Instruments")
    print("=" * 70)

    for sym, name in instruments:
        print(f"\n{'='*70}")
        print(f"  {name} ({sym})")
        print(f"{'='*70}")
        try:
            result = backtest_instrument(sym, name, cfg, n_folds=3)
            all_results.append(result)
        except Exception as e:
            print(f"  Error: {e}")

    # Portfolio simulation
    print(f"\n{'='*70}")
    print("PORTFOLIO BACKTEST")
    print("=" * 70)

    if all_results:
        portfolio = simulate_portfolio(all_results, alloc)
        print(f"\n  Total Return:  {portfolio['total_return']:+.2f}%")
        print(f"  Max Drawdown:  {portfolio['max_drawdown']:.2f}%")
        print(f"  Sharpe:        {portfolio['sharpe']:.2f}")
        print(f"  Sortino:       {portfolio['sortino']:.2f}")
        print(f"  Calmar:        {portfolio['calmar']:.2f}")

    # Summary table
    print(f"\n{'='*70}")
    print("INSTRUMENT SUMMARY")
    print("=" * 70)
    print(f"  {'Name':8s} | {'Return':>8s} | {'DD':>8s} | {'Win%':>5s} | {'Trades':>6s} | {'Sharpe':>7s} | {'Alloc':>6s}")
    print(f"  {'-'*8} | {'-'*8} | {'-'*8} | {'-'*5} | {'-'*6} | {'-'*7} | {'-'*6}")

    for r in sorted(all_results, key=lambda x: -x["total_return"]):
        pct = alloc.get(r["instrument"], 0)
        print(f"  {r['instrument']:8s} | {r['total_return']:+7.2f}% | {r['max_drawdown']:+7.2f}% | "
              f"{r['avg_win_rate']:4.0f}% | {r['total_trades']:6d} | {r['sharpe']:+7.2f} | {pct:5.1f}%")

    if all_results:
        print(f"  {'PORTFOLIO':8s} | {portfolio['total_return']:+7.2f}% | {portfolio['max_drawdown']:+7.2f}% | "
              f"{'':5s} | {'':6s} | {portfolio['sharpe']:+7.2f} | {'100.0':>5s}%")

    # Save results
    output = {
        "instruments": [{k: v for k, v in r.items() if k != "equity_curve"} for r in all_results],
        "portfolio": {k: v for k, v in portfolio.items() if k != "equity_curve"},
        "allocation": alloc,
    }
    with open("results/full_backtest_3yr.json", "w") as f:
        json.dump(output, f, indent=2)

    # Save equity curves
    equity_data = {r["instrument"]: r["equity_curve"] for r in all_results}
    equity_data["portfolio"] = portfolio["equity_curve"]
    with open("results/equity_curves_3yr.json", "w") as f:
        json.dump(equity_data, f)

    print(f"\nSaved to results/full_backtest_3yr.json")
    print(f"Equity curves saved to results/equity_curves_3yr.json")


if __name__ == "__main__":
    from pathlib import Path
    main()
