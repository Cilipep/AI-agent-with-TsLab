"""Multi-instrument test with walk-forward optimization - Enhanced version."""
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


# Extended list of instruments
INSTRUMENTS = {
    # Major
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    # Top Altcoins
    "SOL-USD": "Solana",
    "XRP-USD": "Ripple",
    "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin",
    "AVAX-USD": "Avalanche",
    "DOT-USD": "Polkadot",
    "LINK-USD": "Chainlink",
    "MATIC-USD": "Polygon",
    # Mid-cap
    "UNI-USD": "Uniswap",
    "ATOM-USD": "Cosmos",
    "LTC-USD": "Litecoin",
    "FIL-USD": "Filecoin",
    "NEAR-USD": "NEAR Protocol",
    # Others
    "APT-USD": "Aptos",
    "ARB-USD": "Arbitrum",
    "OP-USD": "Optimism",
}


def download_data(symbol, period="1820d", interval="1d"):
    """Download data from yfinance."""
    cache_path = Path("data") / f"{symbol.replace('/', '_')}_{interval}.csv"

    if cache_path.exists():
        print(f"  Loading cached data from {cache_path}")
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    print(f"  Downloading {symbol}...")
    try:
        df = yf.download(symbol, period=period, interval=interval)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            raise ValueError(f"No data for {symbol}")
        df.to_csv(cache_path)
        print(f"  Saved {len(df)} bars")
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

        print(f"  Fold {fold+1}/{n_folds}...")

        train_ds = torch.utils.data.Subset(ds, range(0, train_end - config.window))
        test_ds = torch.utils.data.Subset(ds, range(test_start - config.window, test_end - config.window))

        # Train ensemble
        models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, train_ds, config, "cpu", quiet=True)
            models.append(model)

        ensemble = Ensemble(models)

        # Test with enhanced backtest
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

        # Offset equity
        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

    # Concatenate equity
    full_equity = np.concatenate(equity_parts) if equity_parts else np.array([1.0])

    # Aggregate stats
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


def calculate_correlation(results):
    """Calculate correlation between instrument returns."""
    returns = {}
    for name, result in results.items():
        if "error" not in result and "equity" in result:
            equity = np.array(result["equity"])
            daily_returns = np.diff(equity) / equity[:-1]
            returns[name] = daily_returns

    if len(returns) < 2:
        return None

    # Align lengths
    min_len = min(len(r) for r in returns.values())
    aligned = {k: v[:min_len] for k, v in returns.items()}

    df = pd.DataFrame(aligned)
    return df.corr()


def generate_report(results, output_path):
    """Generate comprehensive report."""
    lines = []
    lines.append("=" * 80)
    lines.append("MULTI-INSTRUMENT NEURAL NETWORK TRADING - COMPREHENSIVE REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)

    # Results table
    lines.append("\n## RESULTS BY INSTRUMENT\n")
    lines.append(f"{'Instrument':<20} {'Return':>10} {'Drawdown':>10} {'Win Rate':>10} {'PF':>8} {'Trades':>8}")
    lines.append("-" * 76)

    valid_results = {}
    for name, result in sorted(results.items()):
        if "error" not in result:
            valid_results[name] = result
            avg_trades = np.mean([f["trades"] for f in result["folds"]]) if result["folds"] else 0
            lines.append(
                f"{name:<20} {result['total_return']:>+9.2f}% "
                f"{result['max_drawdown']:>9.2f}% "
                f"{result['avg_win_rate']:>9.1f}% "
                f"{result['avg_profit_factor']:>7.2f} "
                f"{avg_trades:>7.0f}"
            )
        else:
            lines.append(f"{name:<20} ERROR: {result['error'][:40]}")

    # Portfolio stats
    if valid_results:
        lines.append("\n## PORTFOLIO STATISTICS\n")
        avg_return = np.mean([r["total_return"] for r in valid_results.values()])
        avg_dd = np.mean([r["max_drawdown"] for r in valid_results.values()])
        avg_wr = np.mean([r["avg_win_rate"] for r in valid_results.values()])
        avg_pf = np.mean([r["avg_profit_factor"] for r in valid_results.values() if r["avg_profit_factor"] < 100])

        lines.append(f"  Instruments tested: {len(valid_results)}")
        lines.append(f"  Average Return:     {avg_return:+.2f}%")
        lines.append(f"  Average Drawdown:   {avg_dd:.2f}%")
        lines.append(f"  Average Win Rate:   {avg_wr:.1f}%")
        lines.append(f"  Average PF:         {avg_pf:.2f}")

        # Best and worst
        best = max(valid_results.items(), key=lambda x: x[1]["total_return"])
        worst = min(valid_results.items(), key=lambda x: x[1]["total_return"])
        lines.append(f"\n  Best performer:  {best[0]} ({best[1]['total_return']:+.2f}%)")
        lines.append(f"  Worst performer: {worst[0]} ({worst[1]['total_return']:+.2f}%)")

    # Correlation analysis
    corr = calculate_correlation(valid_results)
    if corr is not None:
        lines.append("\n## CORRELATION MATRIX\n")
        lines.append(corr.to_string())

        # Find uncorrelated pairs
        lines.append("\n## LOW CORRELATION PAIRS (potential diversification)\n")
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                corr_val = corr.iloc[i, j]
                if abs(corr_val) < 0.7:
                    lines.append(f"  {corr.columns[i]} <-> {corr.columns[j]}: {corr_val:.3f}")

    # Fold details
    lines.append("\n## DETAILED FOLD RESULTS\n")
    for name, result in valid_results.items():
        lines.append(f"\n### {name}")
        for fold in result["folds"]:
            lines.append(
                f"  Fold {fold['fold']}: Return={fold['return']:+.2f}%, "
                f"DD={fold['drawdown']:.2f}%, WR={fold['win_rate']:.1f}%, "
                f"PF={fold['profit_factor']:.2f}, Trades={fold['trades']}"
            )

    # Recommendations
    lines.append("\n## RECOMMENDATIONS\n")
    if valid_results:
        profitable = [n for n, r in valid_results.items() if r["total_return"] > 0]
        unprofitable = [n for n, r in valid_results.items() if r["total_return"] <= 0]

        lines.append(f"  Profitable instruments ({len(profitable)}): {', '.join(profitable)}")
        if unprofitable:
            lines.append(f"  Unprofitable instruments ({len(unprofitable)}): {', '.join(unprofitable)}")

        # Risk-adjusted ranking
        risk_adjusted = {
            n: r["total_return"] / abs(r["max_drawdown"]) if r["max_drawdown"] != 0 else 0
            for n, r in valid_results.items()
        }
        best_ra = max(risk_adjusted.items(), key=lambda x: x[1])
        lines.append(f"\n  Best risk-adjusted: {best_ra[0]} (return/dd ratio: {best_ra[1]:.2f})")

    lines.append("\n" + "=" * 80)

    report = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(report)

    return report


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

    # Instruments to test
    instruments = [
        ("BTC-USD", "Bitcoin"),
        ("ETH-USD", "Ethereum"),
        ("SOL-USD", "Solana"),
    ]

    print("=" * 70)
    print("MULTI-INSTRUMENT TEST WITH WALK-FORWARD")
    print("Model: Transformer | Features: 163 | Trailing Stop: 1%")
    print("=" * 70)

    all_results = {}

    for symbol, name in instruments:
        print(f"\n{'='*70}")
        print(f"TESTING: {name} ({symbol})")
        print("=" * 70)

        try:
            # Download data
            df = download_data(symbol, period="1820d", interval="1d")
            print(f"  Data: {len(df)} bars")

            # Prepare features
            print("  Computing features...")
            df = prepare_features(df, cfg)
            print(f"  Features: {len(df.columns)}")

            # Walk-forward
            print("  Running walk-forward...")
            result = walk_forward_optimized(df, cfg, model_type="transformer", n_folds=5)

            all_results[name] = result

            print(f"\n  Results for {name}:")
            print(f"    Total Return: {result['total_return']:+.2f}%")
            print(f"    Max Drawdown: {result['max_drawdown']:.2f}%")
            print(f"    Avg Win Rate: {result['avg_win_rate']:.1f}%")
            print(f"    Avg PF: {result['avg_profit_factor']:.2f}")

        except Exception as e:
            print(f"  Error: {e}")
            all_results[name] = {"error": str(e)}

    # Summary
    print("\n" + "=" * 70)
    print("MULTI-INSTRUMENT SUMMARY")
    print("=" * 70)

    print(f"\n{'Instrument':<15} {'Return':>10} {'Drawdown':>10} {'Win Rate':>10} {'PF':>8}")
    print("-" * 55)

    for name, result in all_results.items():
        if "error" not in result:
            print(f"{name:<15} {result['total_return']:>+9.2f}% "
                  f"{result['max_drawdown']:>9.2f}% "
                  f"{result['avg_win_rate']:>9.1f}% "
                  f"{result['avg_profit_factor']:>7.2f}")
        else:
            print(f"{name:<15} ERROR: {result['error'][:30]}")

    # Portfolio stats
    valid_results = [r for r in all_results.values() if "error" not in r]
    if valid_results:
        avg_return = np.mean([r["total_return"] for r in valid_results])
        avg_dd = np.mean([r["max_drawdown"] for r in valid_results])
        avg_wr = np.mean([r["avg_win_rate"] for r in valid_results])

        print(f"\n{'PORTFOLIO':<15} {avg_return:>+9.2f}% {avg_dd:>9.2f}% {avg_wr:>9.1f}%")

    # Save results
    output = {
        "params": params,
        "model": "transformer",
        "enhancements": {
            "trailing_stop": 0.01,
            "dynamic_sizing": True,
            "full_talib": True,
        },
        "instruments": all_results,
    }

    with open(cfg.result_dir / "multi_instrument_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {cfg.result_dir / 'multi_instrument_results.json'}")

    # Generate report
    report_path = cfg.result_dir / "multi_instrument_report.txt"
    generate_report(all_results, report_path)
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
