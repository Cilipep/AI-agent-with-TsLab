"""BTC multi-timeframe configuration and training pipeline."""
import numpy as np
import pandas as pd
from pathlib import Path


# BTC timeframes and recommended settings
BTC_TIMEFRAMES = {
    "5m": {
        "suffix": "_5m.csv",
        "max_bars": 10000,
        "window": 20,
        "n_folds": 5,
        "epochs": 15,
        "batch_size": 64,
        "learning_rate": 0.0005,
    },
    "15m": {
        "suffix": "_15m.csv",
        "max_bars": 8000,
        "window": 30,
        "n_folds": 5,
        "epochs": 15,
        "batch_size": 64,
        "learning_rate": 0.0005,
    },
    "30m": {
        "suffix": "_30m.csv",
        "max_bars": 6000,
        "window": 30,
        "n_folds": 5,
        "epochs": 15,
        "batch_size": 64,
        "learning_rate": 0.0005,
    },
    "1h": {
        "suffix": "_1h.csv",
        "max_bars": 6000,
        "window": 40,
        "n_folds": 5,
        "epochs": 20,
        "batch_size": 32,
        "learning_rate": 0.0003,
    },
    "4h": {
        "suffix": "_4h.csv",
        "max_bars": 4000,
        "window": 50,
        "n_folds": 5,
        "epochs": 20,
        "batch_size": 32,
        "learning_rate": 0.0003,
    },
}

# Recommended timeframe for BTC (higher liquidity, better signal quality)
BTC_RECOMMENDED_TF = "15m"

# Alternative: Multi-timeframe ensemble
BTC_MULTI_TF = ["5m", "15m", "1h"]


def get_btc_config(timeframe="15m"):
    """Get BTC-specific configuration for a given timeframe."""
    tf_cfg = BTC_TIMEFRAMES.get(timeframe, BTC_TIMEFRAMES[BTC_RECOMMENDED_TF])
    
    from config import Config
    cfg = Config()
    
    # Override with timeframe-specific settings
    cfg.window = tf_cfg["window"]
    cfg.batch_size = tf_cfg["batch_size"]
    cfg.learning_rate = tf_cfg["learning_rate"]
    cfg.epochs = tf_cfg["epochs"]
    
    # BTC-specific adjustments (higher volatility)
    cfg.stop_loss_pct = 0.025  # Wider stops for BTC
    cfg.take_profit_pct = 0.08  # Higher target for higher volatility
    cfg.risk_per_trade = 0.03  # Slightly higher risk tolerance
    
    # Feature settings
    cfg.max_features = 40
    cfg.use_feature_selection = True
    
    return cfg


def load_btc_data(timeframe="15m"):
    """Load BTC data for specified timeframe."""
    tf_cfg = BTC_TIMEFRAMES.get(timeframe, BTC_TIMEFRAMES[BTC_RECOMMENDED_TF])
    
    cache = Path("data") / f"binance_BTCUSDT{tf_cfg['suffix']}"
    if cache.exists():
        import pandas as pd
        df = pd.read_csv(cache, index_col=0, parse_dates=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    return None


def train_btc(timeframe="15m", use_stacking=False):
    """Train model on BTC data with walk-forward validation."""
    from config import Config
    from features import prepare_features
    from dataset import auto_select_features
    from walk_forward import walk_forward
    
    # Load data
    df = load_btc_data(timeframe)
    if df is None:
        raise FileNotFoundError(f"BTC data for {timeframe} not found")
    
    # Get config
    cfg = get_btc_config(timeframe)
    
    # Prepare features
    df = prepare_features(df, cfg)
    
    # Auto-select features
    feature_cols = auto_select_features(df, df["label"], max_features=cfg.max_features)
    
    # Run walk-forward
    equity, results = walk_forward(
        df, cfg, "cpu", 
        n_folds=BTC_TIMEFRAMES[timeframe]["n_folds"],
        feature_cols=feature_cols,
        use_stacking=use_stacking
    )
    
    return equity, results, cfg


if __name__ == "__main__":
    import json
    
    # Train on recommended timeframe
    print("Training BTC on 15m timeframe...")
    equity, results, cfg = train_btc(timeframe=BTC_RECOMMENDED_TF)
    
    # Calculate summary stats
    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100
    
    from backtest_v2 import calculate_sharpe, calculate_sortino, calculate_calmar
    sharpe = calculate_sharpe(equity)
    sortino = calculate_sortino(equity)
    calmar = calculate_calmar(equity)
    
    summary = {
        "symbol": "BTCUSDT",
        "timeframe": BTC_RECOMMENDED_TF,
        "total_return_pct": round(total_return, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "calmar_ratio": round(calmar, 2),
        "config": {
            "window": cfg.window,
            "batch_size": cfg.batch_size,
            "learning_rate": cfg.learning_rate,
            "epochs": cfg.epochs,
            "stop_loss_pct": cfg.stop_loss_pct,
            "take_profit_pct": cfg.take_profit_pct,
        }
    }
    
    # Save results
    output_path = Path("results") / "btc_walkforward.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\nBTC Walk-forward results saved to: {output_path}")
    print(f"Return: {total_return:+.2f}% | Sharpe: {sharpe:.2f} | Max DD: {max_dd:.2f}%")
