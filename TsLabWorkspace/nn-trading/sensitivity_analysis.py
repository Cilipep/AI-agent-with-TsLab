"""Transaction cost sensitivity analysis for backtesting."""
import numpy as np
import pandas as pd
import torch
from pathlib import Path


def run_with_commission_sensitivity(model, dataset, df, config, device, 
                                    commission_range=None, 
                                    slippage_range=None,
                                    spread_range=None):
    """
    Run backtest with varying transaction costs to assess sensitivity.
    
    Args:
        model: Trained model
        dataset: Test dataset
        df: Price dataframe
        config: Configuration object
        device: Computation device
        commission_range: Range of commission percentages to test
        slippage_range: Range of slippage percentages to test
        spread_range: Range of spread percentages to test
    """
    from backtest_v2 import run_backtest_v2
    
    if commission_range is None:
        commission_range = [0.0001, 0.0002, 0.0005, 0.001, 0.002]
    
    if slippage_range is None:
        slippage_range = [0.00005, 0.0001, 0.0002, 0.0005, 0.001]
    
    if spread_range is None:
        spread_range = [0.0001, 0.0002, 0.0005, 0.001, 0.002]
    
    results = []
    
    print("\n" + "=" * 60)
    print("TRANSACTION COST SENSITIVITY ANALYSIS")
    print("=" * 60)
    
    # Base case
    base_result = run_backtest_v2(
        model, dataset, df, config, device,
        threshold=0.5,
        use_trailing_stop=True, trailing_stop_pct=0.01,
        use_dynamic_sizing=True,
        commission_pct=config.commission_pct,
        slippage_pct=config.slippage_pct,
        spread_pct=config.spread_pct,
    )
    
    base_return = base_result["total_return_pct"]
    
    print(f"\nBase case (comm={config.commission_pct*100:.2f}%, "
          f"slippage={config.slippage_pct*100:.2f}%, "
          f"spread={config.spread_pct*100:.2f}%):")
    print(f"  Return: {base_return:+.2f}% | Trades: {base_result['n_trades']}")
    
    # Test commission sensitivity
    print("\n" + "-" * 60)
    print("COMMISSION SENSITIVITY")
    print("-" * 60)
    
    commission_results = []
    for comm in commission_range:
        result = run_backtest_v2(
            model, dataset, df, config, device,
            threshold=0.5,
            use_trailing_stop=True, trailing_stop_pct=0.01,
            use_dynamic_sizing=True,
            commission_pct=comm,
            slippage_pct=config.slippage_pct,
            spread_pct=config.spread_pct,
        )
        
        return_pct = result["total_return_pct"]
        diff_from_base = return_pct - base_return
        
        commission_results.append({
            "commission_pct": comm,
            "return_pct": return_pct,
            "diff_from_base": diff_from_base,
            "n_trades": result["n_trades"],
        })
        
        print(f"  {comm*100:.2f}% → {return_pct:+.2f}% (Δ {diff_from_base:+.2f}%)")
    
    # Test slippage sensitivity
    print("\n" + "-" * 60)
    print("SLIPPAGE SENSITIVITY")
    print("-" * 60)
    
    slippage_results = []
    for slip in slippage_range:
        result = run_backtest_v2(
            model, dataset, df, config, device,
            threshold=0.5,
            use_trailing_stop=True, trailing_stop_pct=0.01,
            use_dynamic_sizing=True,
            commission_pct=config.commission_pct,
            slippage_pct=slip,
            spread_pct=config.spread_pct,
        )
        
        return_pct = result["total_return_pct"]
        diff_from_base = return_pct - base_return
        
        slippage_results.append({
            "slippage_pct": slip,
            "return_pct": return_pct,
            "diff_from_base": diff_from_base,
            "n_trades": result["n_trades"],
        })
        
        print(f"  {slip*100:.2f}% → {return_pct:+.2f}% (Δ {diff_from_base:+.2f}%)")
    
    # Test spread sensitivity
    print("\n" + "-" * 60)
    print("SPREAD SENSITIVITY")
    print("-" * 60)
    
    spread_results = []
    for spread in spread_range:
        result = run_backtest_v2(
            model, dataset, df, config, device,
            threshold=0.5,
            use_trailing_stop=True, trailing_stop_pct=0.01,
            use_dynamic_sizing=True,
            commission_pct=config.commission_pct,
            slippage_pct=config.slippage_pct,
            spread_pct=spread,
        )
        
        return_pct = result["total_return_pct"]
        diff_from_base = return_pct - base_return
        
        spread_results.append({
            "spread_pct": spread,
            "return_pct": return_pct,
            "diff_from_base": diff_from_base,
            "n_trades": result["n_trades"],
        })
        
        print(f"  {spread*100:.2f}% → {return_pct:+.2f}% (Δ {diff_from_base:+.2f}%)")
    
    # Aggregate results
    all_results = {
        "base_case": {
            "commission_pct": config.commission_pct,
            "slippage_pct": config.slippage_pct,
            "spread_pct": config.spread_pct,
            "return_pct": base_return,
            "n_trades": base_result["n_trades"],
        },
        "commission_sensitivity": commission_results,
        "slippage_sensitivity": slippage_results,
        "spread_sensitivity": spread_results,
    }
    
    return all_results


def analyze_sensitivity(all_results, symbol="BTCUSDT"):
    """Analyze and summarize sensitivity results."""
    print("\n" + "=" * 60)
    print("SENSITIVITY ANALYSIS SUMMARY")
    print("=" * 60)
    
    base_return = all_results["base_case"]["return_pct"]
    
    # Commission sensitivity
    comm_data = all_results["commission_sensitivity"]
    comm_changes = [r["diff_from_base"] for r in comm_data]
    comm_max_change = max(abs(c) for c in comm_changes)
    
    print(f"\nCommission Sensitivity:")
    print(f"  Max change from base: ±{comm_max_change:.2f}%")
    print(f"  Sensitivity level: {'HIGH' if comm_max_change > 5 else 'MEDIUM' if comm_max_change > 2 else 'LOW'}")
    
    # Slippage sensitivity
    slip_data = all_results["slippage_sensitivity"]
    slip_changes = [r["diff_from_base"] for r in slip_data]
    slip_max_change = max(abs(s) for s in slip_changes)
    
    print(f"\nSlippage Sensitivity:")
    print(f"  Max change from base: ±{slip_max_change:.2f}%")
    print(f"  Sensitivity level: {'HIGH' if slip_max_change > 5 else 'MEDIUM' if slip_max_change > 2 else 'LOW'}")
    
    # Spread sensitivity
    spread_data = all_results["spread_sensitivity"]
    spread_changes = [r["diff_from_base"] for r in spread_data]
    spread_max_change = max(abs(s) for s in spread_changes)
    
    print(f"\nSpread Sensitivity:")
    print(f"  Max change from base: ±{spread_max_change:.2f}%")
    print(f"  Sensitivity level: {'HIGH' if spread_max_change > 5 else 'MEDIUM' if spread_max_change > 2 else 'LOW'}")
    
    # Overall assessment
    total_max_change = max(comm_max_change, slip_max_change, spread_max_change)
    
    print(f"\n{'='*60}")
    print("OVERALL ASSESSMENT")
    print("=" * 60)
    
    if total_max_change < 2:
        print("✓ Model is ROBUST to transaction costs")
        print("  Strategy is viable even with higher-than-expected costs")
    elif total_max_change < 5:
        print("⚠ Model has MODERATE sensitivity")
        print("  Monitor actual execution costs in live trading")
    else:
        print("✗ Model is HIGHLY sensitive to transaction costs")
        print("  Strategy may not be viable with realistic costs")
        print("  Consider:")
        print("    • Reducing trading frequency")
        print("    • Increasing position sizing thresholds")
        print("    • Optimizing entry/exit timing")
    
    return total_max_change


def save_results(all_results, symbol="BTCUSDT", output_path=None):
    """Save sensitivity analysis results to JSON."""
    if output_path is None:
        output_path = Path("results") / f"{symbol.lower()}_cost_sensitivity.json"
    
    output_path.parent.mkdir(exist_ok=True)
    
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to: {output_path}")
    
    return output_path


if __name__ == "__main__":
    import torch
    from config import Config
    from features import prepare_features
    from dataset import auto_select_features, TimeSeriesDataset
    from model import build_model, Ensemble
    from train import train
    from walk_forward import walk_forward
    
    print("Transaction Cost Sensitivity Analysis")
    print("=" * 60)
    
    # Load BTC data
    df = pd.read_csv("data/binance_BTCUSDT_15m.csv", index_col=0, parse_dates=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Prepare features
    config = Config()
    config.model_type = "attention"
    config.hidden_size = 32
    config.num_layers = 1
    config.dropout = 0.2
    
    df = prepare_features(df, config)
    feature_cols = auto_select_features(df, df["label"], max_features=30)
    
    # Train model (simplified for demo)
    device = "cpu"
    input_size = len(feature_cols)
    model = build_model(config, input_size)
    
    # Create dataset
    scaler = TimeSeriesDataset(df, config.window, feature_cols=feature_cols)
    train_ds, val_ds, test_ds = scaler.split(0.7, 0.15)
    
    # Train
    model = train(model, train_ds, val_ds, config, device, quiet=False)
    
    # Run sensitivity analysis
    results = run_with_commission_sensitivity(
        model, test_ds, df, config, device
    )
    
    # Analyze
    max_change = analyze_sensitivity(results, "BTCUSDT")
    
    # Save
    save_results(results, "BTCUSDT")
