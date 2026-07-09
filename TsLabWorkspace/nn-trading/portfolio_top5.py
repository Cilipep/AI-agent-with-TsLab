"""Portfolio test: top 5 assets combined."""
import os
import json
import random
import numpy as np
import torch
import pandas as pd
from pathlib import Path
import yfinance as yf
from datetime import datetime

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
torch.set_num_threads(2)

from config import Config
from features_full_talib import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest_v2 import run_backtest_v2


# Top 5 assets by risk-adjusted return
TOP_5 = [
    ("NEAR-USD", "NEAR"),
    ("LTC-USD", "Litecoin"),
    ("AVAX-USD", "Avalanche"),
    ("ATOM-USD", "Cosmos"),
    ("DOT-USD", "Polkadot"),
]


def download_data(symbol, period="1820d", interval="1d"):
    """Download data from yfinance."""
    cache_path = Path("data") / f"{symbol.replace('/', '_')}_{interval}.csv"

    if cache_path.exists():
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    try:
        df = yf.download(symbol, period=period, interval=interval)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            return None
        df.to_csv(cache_path)
        return df
    except Exception as e:
        print(f"  Download failed: {e}")
        return None


def walk_forward_optimized(df, config, model_type="transformer", n_folds=5):
    """Walk-forward with optimization."""
    ds = TimeSeriesDataset(df, config.window)
    total = len(ds)
    fold_size = total // (n_folds + 1)

    all_results = []
    equity_parts = []
    seeds = [42 + i * 31 for i in range(config.n_models)]

    for fold in range(n_folds):
        train_end = fold_size * (fold + 1)
        test_start = train_end
        test_end = min(test_start + fold_size, total)

        if test_end <= test_start:
            break

        train_ds = torch.utils.data.Subset(ds, range(0, train_end - config.window))
        test_ds = torch.utils.data.Subset(ds, range(test_start - config.window, test_end - config.window))

        models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, train_ds, config, "cpu", quiet=True)
            models.append(model)

        ensemble = Ensemble(models)

        result = run_backtest_v2(
            ensemble, test_ds, df, config, "cpu",
            use_trailing_stop=True, trailing_stop_pct=0.01,
            use_dynamic_sizing=True
        )

        all_results.append({
            "fold": fold + 1,
            "return": result["total_return_pct"],
            "drawdown": result["max_drawdown_pct"],
            "trades": result["n_trades"],
            "win_rate": result["win_rate_pct"],
            "profit_factor": result["profit_factor"],
        })

        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

    full_equity = np.concatenate(equity_parts) if equity_parts else np.array([1.0])

    total_return = (full_equity[-1] / full_equity[0] - 1) * 100
    max_dd = ((full_equity / np.maximum.accumulate(full_equity)) - 1).min() * 100
    avg_win = np.mean([r["win_rate"] for r in all_results]) if all_results else 0
    avg_pf = np.mean([r["profit_factor"] for r in all_results if r["profit_factor"] < 100]) if all_results else 0

    return {
        "total_return": total_return,
        "max_drawdown": max_dd,
        "avg_win_rate": avg_win,
        "avg_profit_factor": avg_pf,
        "folds": all_results,
        "equity": full_equity.tolist(),
    }


def create_portfolio_equity(asset_equities, weights):
    """Create equal-weight portfolio equity curve from individual asset equities."""
    # Normalize all equities to start at 1.0
    normalized = []
    for eq in asset_equities:
        eq = np.array(eq)
        normalized.append(eq / eq[0])

    # Align to same length
    min_len = min(len(e) for e in normalized)
    aligned = np.array([e[:min_len] for e in normalized])

    # Equal weight portfolio
    portfolio = np.zeros(min_len)
    for i, w in enumerate(weights):
        portfolio += aligned[i] * w

    return portfolio


def main():
    # Load best parameters
    params_path = Path("results/best_params_simple.json")
    with open(params_path) as f:
        best = json.load(f)

    cfg = Config()
    params = best["params"]
    cfg.model_type = "transformer"
    cfg.hidden_size = params["hidden_size"]
    cfg.num_layers = 1
    cfg.dropout = params["dropout"]
    cfg.window = params["window"]
    cfg.batch_size = params["batch_size"]
    cfg.learning_rate = params["learning_rate"]
    cfg.n_models = 3
    cfg.stop_loss_pct = params["stop_loss_pct"]
    cfg.take_profit_pct = params["take_profit_pct"]

    for d in [cfg.data_dir, cfg.model_dir, cfg.result_dir]:
        d.mkdir(exist_ok=True)

    print("=" * 80)
    print("PORTFOLIO BACKTEST: TOP 5 ASSETS")
    print("Assets: NEAR, LTC, AVAX, ATOM, DOT")
    print("Model: Transformer | Trailing Stop: 1% | Dynamic Sizing: ON")
    print("Weights: Equal (20% each)")
    print("=" * 80)

    all_results = {}
    asset_equities = []

    for symbol, name in TOP_5:
        print(f"\n{'='*80}")
        print(f"TESTING: {name} ({symbol})")
        print("=" * 80)

        try:
            df = download_data(symbol, period="1820d", interval="1d")
            if df is None or len(df) < 100:
                print(f"  Skipping {name}: insufficient data")
                continue

            print(f"  Data: {len(df)} bars")

            print("  Computing features...")
            df = prepare_features(df, cfg)
            print(f"  Features: {len(df.columns)}")

            print("  Running walk-forward...")
            result = walk_forward_optimized(df, cfg, model_type="transformer", n_folds=5)

            all_results[name] = result
            asset_equities.append(result["equity"])

            print(f"\n  Results for {name}:")
            print(f"    Total Return: {result['total_return']:+.2f}%")
            print(f"    Max Drawdown: {result['max_drawdown']:.2f}%")
            print(f"    Avg Win Rate: {result['avg_win_rate']:.1f}%")
            print(f"    Avg PF: {result['avg_profit_factor']:.2f}")

        except Exception as e:
            print(f"  Error: {e}")
            all_results[name] = {"error": str(e)}

    # Calculate portfolio equity
    if asset_equities and len(asset_equities) == len(TOP_5):
        print("\n" + "=" * 80)
        print("PORTFOLIO CALCULATION (Equal Weight)")
        print("=" * 80)

        weights = [1.0 / len(TOP_5)] * len(TOP_5)
        portfolio_equity = create_portfolio_equity(asset_equities, weights)

        # Portfolio metrics
        total_return = (portfolio_equity[-1] / portfolio_equity[0] - 1) * 100
        max_dd = ((portfolio_equity / np.maximum.accumulate(portfolio_equity)) - 1).min() * 100

        # Sharpe ratio (simplified)
        daily_returns = np.diff(portfolio_equity) / portfolio_equity[:-1]
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(365) if np.std(daily_returns) > 0 else 0

        # Sortino ratio
        downside_returns = daily_returns[daily_returns < 0]
        sortino = np.mean(daily_returns) / np.std(downside_returns) * np.sqrt(365) if len(downside_returns) > 0 and np.std(downside_returns) > 0 else 0

        # Calmar ratio
        calmar = total_return / abs(max_dd) if max_dd != 0 else 0

        print(f"\n  Portfolio Return:    {total_return:+.2f}%")
        print(f"  Portfolio Drawdown:  {max_dd:.2f}%")
        print(f"  Sharpe Ratio:        {sharpe:.2f}")
        print(f"  Sortino Ratio:       {sortino:.2f}")
        print(f"  Calmar Ratio:        {calmar:.2f}")

        # Individual asset summary
        print(f"\n{'='*80}")
        print("INDIVIDUAL ASSET SUMMARY")
        print("=" * 80)

        print(f"\n{'Asset':<15} {'Return':>10} {'Drawdown':>10} {'Win Rate':>10} {'PF':>8} {'Weight':>8}")
        print("-" * 71)

        for i, (symbol, name) in enumerate(TOP_5):
            if name in all_results and "error" not in all_results[name]:
                r = all_results[name]
                print(f"{name:<15} {r['total_return']:>+9.2f}% "
                      f"{r['max_drawdown']:>9.2f}% "
                      f"{r['avg_win_rate']:>9.1f}% "
                      f"{r['avg_profit_factor']:>7.2f} "
                      f"{weights[i]*100:>7.0f}%")

        # Portfolio vs individual
        print(f"\n{'='*80}")
        print("PORTFOLIO vs INDIVIDUAL ASSETS")
        print("=" * 80)

        # Find best individual
        best_individual = max(
            [(n, r) for n, r in all_results.items() if "error" not in r],
            key=lambda x: x[1]["total_return"]
        )

        # Find most stable individual
        most_stable = min(
            [(n, r) for n, r in all_results.items() if "error" not in r],
            key=lambda x: abs(x[1]["max_drawdown"])
        )

        print(f"\n  Portfolio Return:        {total_return:+.2f}%")
        print(f"  Best Individual ({best_individual[0]}):  {best_individual[1]['total_return']:+.2f}%")
        print(f"\n  Portfolio Drawdown:      {max_dd:.2f}%")
        print(f"  Most Stable ({most_stable[0]}):    {most_stable[1]['max_drawdown']:.2f}%")
        print(f"\n  Portfolio Sharpe:        {sharpe:.2f}")

        # Correlation analysis
        print(f"\n{'='*80}")
        print("CORRELATION BETWEEN ASSETS")
        print("=" * 80)

        # Create returns DataFrame
        returns_dict = {}
        for i, (symbol, name) in enumerate(TOP_5):
            if name in all_results and "error" not in all_results[name]:
                eq = np.array(all_results[name]["equity"])
                daily_ret = np.diff(eq) / eq[:-1]
                min_len = min(len(d) for d in [daily_ret] + [np.diff(np.array(e)) / np.array(e)[:-1] for e in asset_equities if e != asset_equities[i]])
                returns_dict[name] = daily_ret[:min_len]

        if len(returns_dict) >= 2:
            df_returns = pd.DataFrame(returns_dict)
            corr = df_returns.corr()
            print("\n" + corr.to_string())

            # Find low correlation pairs
            print("\nLow correlation pairs (good for diversification):")
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    corr_val = corr.iloc[i, j]
                    if abs(corr_val) < 0.7:
                        print(f"  {corr.columns[i]} <-> {corr.columns[j]}: {corr_val:.3f}")

        # Save results
        output = {
            "portfolio": {
                "assets": [name for _, name in TOP_5],
                "weights": weights,
                "total_return": total_return,
                "max_drawdown": max_dd,
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "calmar_ratio": calmar,
            },
            "individual": {
                name: {
                    "return": r["total_return"],
                    "drawdown": r["max_drawdown"],
                    "win_rate": r["avg_win_rate"],
                    "profit_factor": r["avg_profit_factor"],
                }
                for name, r in all_results.items()
                if "error" not in r
            },
            "params": params,
        }

        output_path = cfg.result_dir / "portfolio_top5_results.json"
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\nResults saved to {output_path}")

    else:
        print("\nNot enough assets completed for portfolio calculation.")


if __name__ == "__main__":
    main()
