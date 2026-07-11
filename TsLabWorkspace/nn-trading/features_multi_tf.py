"""Multi-timeframe feature pipeline: merge 1d, 1w, 1m indicators into daily bars."""
import numpy as np
import pandas as pd
import talib


def compute_tf_indicators(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Compute a focused set of indicators on any timeframe."""
    df = df.copy()
    close = df["Close"].values.astype(np.float64)
    high = df["High"].values.astype(np.float64)
    low = df["Low"].values.astype(np.float64)

    # Trend
    df[f"{prefix}ema_10"] = talib.EMA(close, timeperiod=10)
    df[f"{prefix}ema_20"] = talib.EMA(close, timeperiod=20)
    df[f"{prefix}ema_50"] = talib.EMA(close, timeperiod=50)
    df[f"{prefix}sma_20"] = talib.SMA(close, timeperiod=20)
    df[f"{prefix}adx"] = talib.ADX(high, low, close, timeperiod=14)
    macd, macd_sig, macd_hist = talib.MACD(close)
    df[f"{prefix}macd"] = macd
    df[f"{prefix}macd_signal"] = macd_sig
    df[f"{prefix}macd_hist"] = macd_hist

    # Momentum
    df[f"{prefix}rsi"] = talib.RSI(close, timeperiod=14)
    df[f"{prefix}rsi_7"] = talib.RSI(close, timeperiod=7)
    df[f"{prefix}stoch_k"], df[f"{prefix}stoch_d"] = talib.STOCH(high, low, close)
    df[f"{prefix}williams_r"] = talib.WILLR(high, low, close, timeperiod=14)
    df[f"{prefix}cci"] = talib.CCI(high, low, close, timeperiod=14)
    df[f"{prefix}roc_10"] = talib.ROC(close, timeperiod=10)
    df[f"{prefix}momentum"] = talib.MOM(close, timeperiod=10)

    # Volatility
    bb_upper, bb_mid, bb_lower = talib.BBANDS(close, timeperiod=20)
    df[f"{prefix}bb_width"] = (bb_upper - bb_lower) / bb_mid
    df[f"{prefix}bb_pct"] = (close - bb_lower) / (bb_upper - bb_lower)
    df[f"{prefix}atr"] = talib.ATR(high, low, close, timeperiod=14)
    df[f"{prefix}atr_pct"] = df[f"{prefix}atr"] / df["Close"]

    # Price relative to MAs
    df[f"{prefix}price_vs_ema10"] = close / df[f"{prefix}ema_10"] - 1
    df[f"{prefix}price_vs_ema20"] = close / df[f"{prefix}ema_20"] - 1
    df[f"{prefix}price_vs_ema50"] = close / df[f"{prefix}ema_50"] - 1

    # Return
    df[f"{prefix}returns"] = df["Close"].pct_change()

    # Keep only prefixed columns + Close for alignment
    keep = [c for c in df.columns if c.startswith(prefix) or c == "Close"]
    return df[keep]


def merge_timeframes(df_daily: pd.DataFrame, df_weekly: pd.DataFrame,
                     df_monthly: pd.DataFrame) -> pd.DataFrame:
    """Merge weekly and monthly indicators into daily bars via forward-fill."""
    result = df_daily.copy()

    # Compute indicators on each timeframe
    weekly_ind = compute_tf_indicators(df_weekly, "w_")
    monthly_ind = compute_tf_indicators(df_monthly, "m_")

    # Forward-fill weekly/monthly to daily index
    weekly_daily = weekly_ind.reindex(result.index, method="ffill")
    monthly_daily = monthly_ind.reindex(result.index, method="ffill")

    # Drop Close columns from merged (we keep daily Close)
    for col in ["w_Close", "m_Close"]:
        if col in weekly_daily.columns:
            weekly_daily = weekly_daily.drop(columns=[col])
        if col in monthly_daily.columns:
            monthly_daily = monthly_daily.drop(columns=[col])

    # Merge
    result = pd.concat([result, weekly_daily, monthly_daily], axis=1)
    result = result.ffill().bfill()

    return result


def load_and_merge(symbol: str) -> pd.DataFrame:
    """Load 1d/1w/1m data and merge into multi-timeframe daily DataFrame."""
    base = Path("data")
    daily = pd.read_csv(base / f"binance_{symbol}_1d.csv", index_col=0, parse_dates=True)
    weekly = pd.read_csv(base / f"binance_{symbol}_1w.csv", index_col=0, parse_dates=True)
    monthly = pd.read_csv(base / f"binance_{symbol}_1M.csv", index_col=0, parse_dates=True)

    # Ensure consistent column names
    for df in [daily, weekly, monthly]:
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return merge_timeframes(daily, weekly, monthly)


if __name__ == "__main__":
    from pathlib import Path
    for sym in ["BTC-USD", "ETH-USD", "SOL-USD"]:
        print(f"Merging {sym}...")
        df = load_and_merge(sym)
        out = Path("data") / f"binance_{sym}_multi_tf.csv"
        df.to_csv(out)
        print(f"  {len(df)} rows, {len(df.columns)} columns -> {out}")
    print("Done!")
