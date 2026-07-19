"""BTC-specific metrics and analysis for walk-forward validation."""
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict


def calculate_btc_metrics(equity, results, config, timeframe="15m"):
    """
    Calculate comprehensive BTC-specific trading metrics.
    
    Args:
        equity: Equity curve array
        results: List of WindowResult objects from walk_forward
        config: Config object
        timeframe: Timeframe used for trading
    
    Returns:
        dict: Comprehensive metrics dictionary
    """
    # Basic equity metrics
    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100
    max_dd_point = equity[np.argmax(np.maximum.accumulate(equity) - equity)]
    recovery_point = equity[np.argmax(equity >= max_dd_point)] if max_dd_point < equity[-1] else None
    
    # Risk-adjusted returns
    from backtest_v2 import calculate_sharpe, calculate_sortino, calculate_calmar
    sharpe = calculate_sharpe(equity)
    sortino = calculate_sortino(equity)
    calmar = calculate_calmar(equity)
    
    # Trade-level metrics
    total_trades = sum(r.n_trades for r in results)
    total_wins = sum(int(r.win_rate * r.n_trades / 100) for r in results)
    win_rate = total_wins / total_trades * 100 if total_trades > 0 else 0
    
    # Profit factor (gross profits / gross losses)
    gross_profit = sum(r.return_pct for r in results if r.return_pct > 0)
    gross_loss = sum(abs(r.return_pct) for r in results if r.return_pct < 0)
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    
    # Average trade
    avg_trade = total_return / total_trades if total_trades > 0 else 0
    
    # Equity statistics
    equity_returns = np.diff(equity) / equity[:-1]
    volatility = np.std(equity_returns) * np.sqrt(365) * 100  # Annualized
    
    # Drawdown duration (simplified)
    peak = equity[0]
    dd_duration = 0
    max_dd_duration = 0
    for eq in equity:
        if eq > peak:
            peak = eq
            dd_duration = 0
        else:
            dd_duration += 1
            max_dd_duration = max(max_dd_duration, dd_duration)
    
    # Fold-level statistics
    fold_returns = [r.return_pct for r in results]
    fold_sharpes = [r.sharpe for r in results if r.sharpe < 100]
    
    metrics = {
        "equity": {
            "total_return_pct": round(total_return, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "calmar_ratio": round(calmar, 2),
            "volatility_annualized_pct": round(volatility, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else "inf",
        },
        "trades": {
            "total_trades": total_trades,
            "win_rate_pct": round(win_rate, 1),
            "average_trade_pct": round(avg_trade, 2),
        },
        "drawdown": {
            "max_dd_pct": round(max_dd, 2),
            "max_dd_duration_bars": max_dd_duration,
        },
        "folds": {
            "n_folds": len(results),
            "avg_return_pct": round(np.mean(fold_returns), 2) if fold_returns else 0,
            "avg_sharpe": round(np.mean(fold_sharpes), 2) if fold_sharpes else 0,
        },
        "config": {
            "timeframe": timeframe,
            "window": config.window,
            "model_type": config.model_type,
            "hidden_size": config.hidden_size,
        },
    }
    
    return metrics


def analyze_btc_timeframes():
    """
    Analyze BTC performance across different timeframes.
    
    Returns:
        dict: Timeframe comparison metrics
    """
    from config import Config
    from features import prepare_features
    from dataset import auto_select_features
    
    timeframes = {
        "5m": {"suffix": "_5m.csv", "n_folds": 3, "epochs": 10},
        "15m": {"suffix": "_15m.csv", "n_folds": 5, "epochs": 15},
        "30m": {"suffix": "_30m.csv", "n_folds": 5, "epochs": 15},
        "1h": {"suffix": "_1h.csv", "n_folds": 5, "epochs": 20},
        "4h": {"suffix": "_4h.csv", "n_folds": 5, "epochs": 20},
    }
    
    results = {}
    
    print("=" * 60)
    print("BTC TIMEFRAME ANALYSIS")
    print("=" * 60)
    
    for tf, cfg in timeframes.items():
        print(f"\nAnalyzing {tf}...")
        
        # Load data
        df = pd.read_csv(f"data/binance_BTCUSDT{cfg['suffix']}", index_col=0, parse_dates=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Prepare config
        base_config = Config()
        base_config.model_type = "attention"
        base_config.hidden_size = 32
        base_config.num_layers = 1
        base_config.dropout = 0.2
        base_config.window = 30 if tf in ["5m", "15m"] else 40
        base_config.epochs = cfg["epochs"]
        base_config.n_folds = cfg["n_folds"]
        
        # Prepare features
        df = prepare_features(df, base_config)
        feature_cols = auto_select_features(df, df["label"], max_features=30)
        
        # Run walk-forward
        from walk_forward import walk_forward
        equity, results_list = walk_forward(
            df, base_config, "cpu", 
            n_folds=cfg["n_folds"],
            feature_cols=feature_cols
        )
        
        # Calculate metrics
        metrics = calculate_btc_metrics(equity, results_list, base_config, tf)
        results[tf] = metrics
        
        print(f"  Return: {metrics['equity']['total_return_pct']:+.2f}%")
        print(f"  Max DD: {metrics['equity']['max_drawdown_pct']:.2f}%")
        print(f"  Sharpe: {metrics['equity']['sharpe_ratio']:.2f}")
    
    # Save results
    output_path = Path("results") / "btc_timeframe_comparison.json"
    output_path.parent.mkdir(exist_ok=True)
    
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to: {output_path}")
    
    return results


def recommend_timeframe(btc_results):
    """
    Recommend optimal timeframe based on risk-adjusted returns.
    
    Args:
        btc_results: Dict of timeframe metrics from analyze_btc_timeframes()
    
    Returns:
        str: Recommended timeframe
    """
    print("\n" + "=" * 60)
    print("TIMEFRAME RECOMMENDATION")
    print("=" * 60)
    
    best_score = -float("inf")
    recommended = None
    
    for tf, metrics in btc_results.items():
        # Score: Sharpe ratio (higher is better)
        # Penalize for high drawdown
        sharpe = metrics['equity']['sharpe_ratio']
        max_dd = abs(metrics['equity']['max_drawdown_pct'])
        
        score = sharpe - (max_dd / 10)  # Penalize 1% DD as 0.1 Sharpe
        
        print(f"{tf}: Score={score:.2f} (Sharpe={sharpe:.2f}, DD={max_dd:.1f}%)")
        
        if score > best_score:
            best_score = score
            recommended = tf
    
    print(f"\n✓ Recommended timeframe: {recommended}")
    print(f"  Score: {best_score:.2f}")
    
    return recommended


if __name__ == "__main__":
    # Run analysis
    results = analyze_btc_timeframes()
    
    # Get recommendation
    recommended = recommend_timeframe(results)
    
    print("\n" + "=" * 60)
    print("Analysis completed!")
    print("=" * 60)
