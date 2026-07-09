"""Optimized TA-Lib features - selected for performance."""
import numpy as np
import pandas as pd
import talib


def add_talib_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add selected TA-Lib indicators optimized for trading."""
    df = df.copy()

    close = df["Close"].values.astype(np.float64)
    high = df["High"].values.astype(np.float64)
    low = df["Low"].values.astype(np.float64)
    open_ = df["Open"].values.astype(np.float64)
    volume = df["Volume"].values.astype(np.float64) if "Volume" in df.columns else np.zeros(len(df), dtype=np.float64)

    # ============================================
    # CORE INDICATORS (most effective)
    # ============================================

    # --- Trend ---
    df["ema_10"] = talib.EMA(close, timeperiod=10)
    df["ema_20"] = talib.EMA(close, timeperiod=20)
    df["ema_50"] = talib.EMA(close, timeperiod=50)
    df["macd"], df["macd_signal"], df["macd_hist"] = talib.MACD(close)
    df["adx"] = talib.ADX(high, low, close, timeperiod=14)
    df["plus_di"] = talib.PLUS_DI(high, low, close, timeperiod=14)
    df["minus_di"] = talib.MINUS_DI(high, low, close, timeperiod=14)
    df["aroon_up"], df["aroon_down"] = talib.AROON(high, low, timeperiod=25)
    df["sar"] = talib.SAR(high, low, acceleration=0.02, maximum=0.2)

    # --- Momentum ---
    df["rsi"] = talib.RSI(close, timeperiod=14)
    df["rsi_7"] = talib.RSI(close, timeperiod=7)
    df["stoch_k"], df["stoch_d"] = talib.STOCH(high, low, close)
    df["williams_r"] = talib.WILLR(high, low, close, timeperiod=14)
    df["cci"] = talib.CCI(high, low, close, timeperiod=14)
    df["roc_10"] = talib.ROC(close, timeperiod=10)
    df["momentum"] = talib.MOM(close, timeperiod=10)
    df["ultosc"] = talib.ULTOSC(high, low, close)

    # --- Volatility ---
    df["bb_upper"], df["bb_mid"], df["bb_lower"] = talib.BBANDS(close, timeperiod=20)
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"]
    df["bb_pct"] = (close - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])
    df["atr"] = talib.ATR(high, low, close, timeperiod=14)
    df["atr_pct"] = df["atr"] / df["Close"]
    df["natr"] = talib.NATR(high, low, close, timeperiod=14)

    # --- Volume ---
    if volume.sum() > 0:
        df["obv"] = talib.OBV(close, volume)
        df["obv_sma"] = df["obv"].rolling(20).mean()
        df["ad"] = talib.AD(high, low, close, volume)
        df["adosc"] = talib.ADOSC(high, low, close, volume)
        df["mfi"] = talib.MFI(high, low, close, volume, timeperiod=14)

    # --- Price Patterns ---
    df["cdl_doji"] = talib.CDLDOJI(open_, high, low, close)
    df["cdl_hammer"] = talib.CDLHAMMER(open_, high, low, close)
    df["cdl_engulfing"] = talib.CDLENGULFING(open_, high, low, close)
    df["cdl_morningstar"] = talib.CDLMORNINGSTAR(open_, high, low, close)
    df["cdl_eveningstar"] = talib.CDLEVENINGSTAR(open_, high, low, close)

    # --- Price Transforms ---
    df["typical_price"] = talib.TYPPRICE(high, low, close)
    df["weighted_close"] = talib.WCLPRICE(high, low, close)

    # --- Statistics ---
    df["beta"] = talib.BETA(high, low, timeperiod=14)
    df["correlation"] = talib.CORREL(high, low, timeperiod=14)
    df["linearreg_slope"] = talib.LINEARREG_SLOPE(close, timeperiod=14)
    df["stddev"] = talib.STDDEV(close, timeperiod=14)

    # --- Returns ---
    df["returns"] = df["Close"].pct_change()
    df["returns_5"] = df["Close"].pct_change(5)
    df["returns_10"] = df["Close"].pct_change(10)
    df["returns_20"] = df["Close"].pct_change(20)
    df["log_returns"] = np.log(df["Close"] / df["Close"].shift(1))

    # --- Price Ratios ---
    df["high_low_ratio"] = df["High"] / df["Low"]
    df["close_open_ratio"] = df["Close"] / df["Open"]
    df["gap"] = df["Open"] / df["Close"].shift(1) - 1

    # --- Volume Features ---
    if volume.sum() > 0:
        df["volume_sma"] = df["Volume"].rolling(20).mean()
        df["volume_ratio"] = df["Volume"] / df["volume_sma"]

    # Fill NaN
    df = df.ffill().bfill()

    return df


def make_label(df: pd.DataFrame, horizon: int = 5, threshold: float = 0.001) -> pd.Series:
    """Create classification label."""
    future_return = df["Close"].shift(-horizon) / df["Close"] - 1
    label = (future_return > threshold).astype(int)
    return label


def prepare_features(df: pd.DataFrame, config) -> pd.DataFrame:
    """Full feature preparation pipeline."""
    df = add_talib_indicators(df)
    df["label"] = make_label(df, config.horizon, config.threshold)
    df = df.dropna()
    return df
