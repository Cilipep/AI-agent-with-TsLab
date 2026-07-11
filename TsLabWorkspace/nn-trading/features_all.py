"""Multi-timeframe features for BTC: merge 8 timeframes into daily bars."""
import numpy as np
import pandas as pd
import talib
from pathlib import Path


def compute_indicators(df, prefix):
    df = df.copy()
    c = df["Close"].values.astype(np.float64)
    h = df["High"].values.astype(np.float64)
    l = df["Low"].values.astype(np.float64)
    v = df["Volume"].values.astype(np.float64) if "Volume" in df.columns else np.zeros(len(df))

    df[f"{prefix}ema10"] = talib.EMA(c, 10)
    df[f"{prefix}ema20"] = talib.EMA(c, 20)
    df[f"{prefix}ema50"] = talib.EMA(c, 50)
    df[f"{prefix}rsi"] = talib.RSI(c, 14)
    df[f"{prefix}rsi7"] = talib.RSI(c, 7)
    macd, sig, hist = talib.MACD(c)
    df[f"{prefix}macd"] = macd
    df[f"{prefix}macd_sig"] = sig
    df[f"{prefix}macd_hist"] = hist
    bu, bm, bl = talib.BBANDS(c, 20)
    df[f"{prefix}bb_w"] = (bu - bl) / bm
    df[f"{prefix}bb_pct"] = (c - bl) / (bu - bl + 1e-8)
    df[f"{prefix}atr"] = talib.ATR(h, l, c, 14)
    df[f"{prefix}adx"] = talib.ADX(h, l, c, 14)
    df[f"{prefix}stoch_k"], df[f"{prefix}stoch_d"] = talib.STOCH(h, l, c)
    df[f"{prefix}willr"] = talib.WILLR(h, l, c, 14)
    df[f"{prefix}cci"] = talib.CCI(h, l, c, 14)
    df[f"{prefix}roc"] = talib.ROC(c, 10)
    df[f"{prefix}mom"] = talib.MOM(c, 10)
    df[f"{prefix}pvs_ema10"] = c / (df[f"{prefix}ema10"] + 1e-8) - 1
    df[f"{prefix}pvs_ema20"] = c / (df[f"{prefix}ema20"] + 1e-8) - 1
    df[f"{prefix}ret"] = df["Close"].pct_change()
    if v.sum() > 0:
        df[f"{prefix}obv"] = talib.OBV(c, v)
        df[f"{prefix}mfi"] = talib.MFI(h, l, c, v, 14)

    keep = [col for col in df.columns if col.startswith(prefix) or col == "Close"]
    return df[keep]


def merge_timeframes(daily, tf_data):
    result = daily.copy()
    for tf_name, tf_df in tf_data.items():
        ind = compute_indicators(tf_df, f"{tf_name}_")
        aligned = ind.reindex(result.index, method="ffill")
        # Drop ALL Close columns from aligned (keep only daily Close)
        close_cols = [c for c in aligned.columns if "Close" in c or c == "Close"]
        if close_cols:
            aligned = aligned.drop(columns=close_cols)
        result = pd.concat([result, aligned], axis=1)
    result = result.ffill().bfill()
    # Remove any duplicate columns
    result = result.loc[:, ~result.columns.duplicated()]
    return result


def load_btc_8tf():
    base = Path("data")
    daily = pd.read_csv(base / "binance_BTCUSDT_1d.csv", index_col=0, parse_dates=True)
    tf_map = {}
    for tf in ["5m", "15m", "30m", "1h", "4h", "1w", "1M"]:
        path = base / f"binance_BTCUSDT_{tf}.csv"
        if path.exists():
            tf_map[tf] = pd.read_csv(path, index_col=0, parse_dates=True)
    return merge_timeframes(daily, tf_map)


def load_instrument_3tf(symbol):
    base = Path("data")
    daily = pd.read_csv(base / f"binance_{symbol}_1d.csv", index_col=0, parse_dates=True)
    tf_map = {}
    for tf in ["1w", "1M"]:
        path = base / f"binance_{symbol}_{tf}.csv"
        if path.exists():
            tf_map[tf] = pd.read_csv(path, index_col=0, parse_dates=True)
    return merge_timeframes(daily, tf_map)


if __name__ == "__main__":
    print("Loading BTC 8-timeframe data...")
    btc = load_btc_8tf()
    btc.to_csv("data/binance_BTCUSDT_8tf.csv")
    print(f"  {len(btc)} rows, {len(btc.columns)} columns")

    instruments = ["NEARUSDT", "XLMUSDT", "SOLUSDT", "AAVEUSDT", "LINKUSDT",
                   "SUIUSDT", "ADAUSDT", "BCHUSDT", "TRXUSDT", "UNIUSDT"]
    for sym in instruments:
        print(f"Loading {sym}...")
        df = load_instrument_3tf(sym)
        df.to_csv(f"data/binance_{sym}_3tf.csv")
        print(f"  {len(df)} rows, {len(df.columns)} columns")
    print("Done!")
