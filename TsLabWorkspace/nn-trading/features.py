import numpy as np
import pandas as pd
import talib
import ta


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators using TA-Lib + ta library."""
    df = df.copy()

    close = df["Close"].values.astype(np.float64)
    high = df["High"].values.astype(np.float64)
    low = df["Low"].values.astype(np.float64)
    open_ = df["Open"].values.astype(np.float64)
    volume = df["Volume"].values.astype(np.float64) if "Volume" in df.columns else np.zeros(len(df), dtype=np.float64)

    # ============================================
    # TA-Lib Indicators (160+ indicators)
    # ============================================

    # --- Trend Indicators ---
    # Moving Averages
    df["sma_10"] = talib.SMA(close, timeperiod=10)
    df["sma_20"] = talib.SMA(close, timeperiod=20)
    df["sma_50"] = talib.SMA(close, timeperiod=50)
    df["ema_10"] = talib.EMA(close, timeperiod=10)
    df["ema_20"] = talib.EMA(close, timeperiod=20)
    df["ema_50"] = talib.EMA(close, timeperiod=50)
    df["ema_200"] = talib.EMA(close, timeperiod=200)

    # MACD
    df["macd"], df["macd_signal"], df["macd_hist"] = talib.MACD(close)

    # ADX
    df["adx"] = talib.ADX(high, low, close, timeperiod=14)
    df["adx_pos"] = talib.PLUS_DI(high, low, close, timeperiod=14)
    df["adx_neg"] = talib.MINUS_DI(high, low, close, timeperiod=14)

    # Aroon
    df["aroon_up"], df["aroon_down"] = talib.AROON(high, low, timeperiod=25)
    df["aroonosc"] = talib.AROONOSC(high, low, timeperiod=25)

    # Parabolic SAR
    df["sar"] = talib.SAR(high, low, acceleration=0.02, maximum=0.2)

    # Trix
    df["trix"] = talib.TRIX(close, timeperiod=12)

    # Linear Regression
    df["linreg_slope"] = talib.LINEARREG_SLOPE(close, timeperiod=14)

    # --- Momentum Indicators ---
    # RSI
    df["rsi"] = talib.RSI(close, timeperiod=14)
    df["rsi_7"] = talib.RSI(close, timeperiod=7)

    # Stochastic
    df["stoch_k"], df["stoch_d"] = talib.STOCH(high, low, close)

    # Stochastic Fast
    df["stochf_k"], df["stochf_d"] = talib.STOCHF(high, low, close)

    # Stochastic RSI
    df["stoch_rsi_k"], df["stoch_rsi_d"] = talib.STOCHRSI(close, timeperiod=14)

    # Williams %R
    df["williams_r"] = talib.WILLR(high, low, close, timeperiod=14)

    # CCI
    df["cci"] = talib.CCI(high, low, close, timeperiod=14)

    # MFI (Money Flow Index)
    if volume.sum() > 0:
        df["mfi"] = talib.MFI(high, low, close, volume, timeperiod=14)

    # ROC (Rate of Change)
    df["roc_10"] = talib.ROC(close, timeperiod=10)
    df["roc_20"] = talib.ROC(close, timeperiod=20)

    # Momentum
    df["momentum"] = talib.MOM(close, timeperiod=10)

    # Ultimate Oscillator
    df["ultosc"] = talib.ULTOSC(high, low, close)

    # --- Volatility Indicators ---
    # Bollinger Bands
    df["bb_upper"], df["bb_mid"], df["bb_lower"] = talib.BBANDS(close, timeperiod=20)
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"]
    df["bb_pct"] = (close - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

    # ATR
    df["atr"] = talib.ATR(high, low, close, timeperiod=14)
    df["atr_pct"] = df["atr"] / df["Close"]

    # Keltner Channel (using ATR)
    df["kc_mid"] = talib.EMA(close, timeperiod=20)
    df["kc_upper"] = df["kc_mid"] + 2 * df["atr"]
    df["kc_lower"] = df["kc_mid"] - 2 * df["atr"]

    # Normalized ATR
    df["natr"] = talib.NATR(high, low, close, timeperiod=14)

    # --- Volume Indicators ---
    if volume.sum() > 0:
        # On Balance Volume
        df["obv"] = talib.OBV(close, volume)
        df["obv_sma"] = df["obv"].rolling(20).mean()

        # Chaikin A/D Line
        df["ad"] = talib.AD(high, low, close, volume)

        # Chaikin A/D Oscillator
        df["adosc"] = talib.ADOSC(high, low, close, volume)

        # Volume Weighted Average Price (approximation)
        df["vwap"] = (volume * (high + low + close) / 3).cumsum() / volume.cumsum()

    # --- Cycle Indicators ---
    df["ht_dcperiod"] = talib.HT_DCPERIOD(close)
    df["ht_dcphase"] = talib.HT_DCPHASE(close)
    df["ht_inphase"], df["ht_quad"] = talib.HT_PHASOR(close)
    df["ht_sine"], df["ht_leadsine"] = talib.HT_SINE(close)

    # --- Price Transform ---
    df["typical_price"] = talib.TYPPRICE(high, low, close)
    df["weighted_close"] = talib.WCLPRICE(high, low, close)
    df["midpoint"] = talib.MIDPOINT(close, timeperiod=14)
    df["midprice"] = talib.MIDPRICE(high, low, timeperiod=14)

    # --- Statistic Functions ---
    df["beta"] = talib.BETA(high, low, timeperiod=14)
    df["correlation"] = talib.CORREL(high, low, timeperiod=14)
    df["linearreg"] = talib.LINEARREG(close, timeperiod=14)
    df["linearreg_angle"] = talib.LINEARREG_ANGLE(close, timeperiod=14)
    df["linearreg_intercept"] = talib.LINEARREG_INTERCEPT(close, timeperiod=14)
    df["stddev"] = talib.STDDEV(close, timeperiod=14)

    # --- Math Functions ---
    df["log_return"] = np.log(close / np.roll(close, 1))
    df["log_return"].iloc[0] = 0
    df["sqrt_return"] = np.sqrt(np.abs(df["log_return"]))

    # --- Pattern Recognition (Candlestick) ---
    # Doji
    df["cdl_doji"] = talib.CDLDOJI(open_, high, low, close)

    # Hammer
    df["cdl_hammer"] = talib.CDLHAMMER(open_, high, low, close)

    # Engulfing
    df["cdl_engulfing"] = talib.CDLENGULFING(open_, high, low, close)

    # Morning Star
    df["cdl_morningstar"] = talib.CDLMORNINGSTAR(open_, high, low, close)

    # Evening Star
    df["cdl_eveningstar"] = talib.CDLEVENINGSTAR(open_, high, low, close)

    # Three White Soldiers
    df["cdl_3whitesoldiers"] = talib.CDL3WHITESOLDIERS(open_, high, low, close)

    # Three Black Crows
    df["cdl_3blackcrows"] = talib.CDL3BLACKCROWS(open_, high, low, close)

    # Harami
    df["cdl_harami"] = talib.CDLHARAMI(open_, high, low, close)

    # Piercing
    df["cdl_piercing"] = talib.CDLPIERCING(open_, high, low, close)

    # Dark Cloud
    df["cdl_darkcloud"] = talib.CDLDARKCLOUDCOVER(open_, high, low, close)

    # ============================================
    # ta Library Indicators (additional)
    # ============================================

    # Price-based
    df["returns"] = df["Close"].pct_change()
    df["log_returns"] = np.log(df["Close"] / df["Close"].shift(1))

    # Multi-timeframe returns
    for period in [3, 5, 10, 20]:
        df[f"returns_{period}"] = df["Close"].pct_change(period)

    # Momentum (ta library)
    stoch_rsi = ta.momentum.StochRSIIndicator(df["Close"], window=14)
    df["stoch_rsi_k_ta"] = stoch_rsi.stochrsi_k()
    df["stoch_rsi_d_ta"] = stoch_rsi.stochrsi_d()

    # Trend (ta library)
    aroon = ta.trend.AroonIndicator(high=df["High"], low=df["Low"], window=25)
    df["aroon_up_ta"] = aroon.aroon_up()
    df["aroon_down_ta"] = aroon.aroon_down()

    # Donchian Channel
    dc = ta.volatility.DonchianChannel(df["High"], df["Low"], df["Close"])
    df["dc_upper"] = dc.donchian_channel_hband()
    df["dc_lower"] = dc.donchian_channel_lband()

    # Volume (ta library)
    if volume.sum() > 0:
        df["volume_sma"] = df["Volume"].rolling(20).mean()
        df["volume_ratio"] = df["Volume"] / df["volume_sma"]
        df["volume_sma_5"] = df["Volume"].rolling(5).mean()
        df["volume_trend"] = df["volume_sma_5"] / df["volume_sma"]
        df["vpt"] = ta.volume.VolumePriceTrendIndicator(df["Close"], df["Volume"]).volume_price_trend()

    # Price patterns
    df["high_low_ratio"] = df["High"] / df["Low"]
    df["close_open_ratio"] = df["Close"] / df["Open"]

    # Rolling statistics
    for window in [10, 20]:
        df[f"close_sma_{window}"] = df["Close"].rolling(window).mean()
        df[f"close_std_{window}"] = df["Close"].rolling(window).std()
        df[f"close_zscore_{window}"] = (df["Close"] - df[f"close_sma_{window}"]) / df[f"close_std_{window}"]

    # Gap
    df["gap"] = df["Open"] / df["Close"].shift(1) - 1

    # Fill NaN with forward fill then backward fill
    df = df.ffill().bfill()

    return df


def make_label(df: pd.DataFrame, horizon: int = 5, threshold: float = 0.001) -> pd.Series:
    """
    Create classification label:
      1 = price goes up by more than threshold
      0 = otherwise
    """
    future_return = df["Close"].shift(-horizon) / df["Close"] - 1
    label = (future_return > threshold).astype(int)
    return label


def prepare_features(df: pd.DataFrame, config) -> pd.DataFrame:
    """Full feature preparation pipeline."""
    df = add_indicators(df)
    df["label"] = make_label(df, config.horizon, config.threshold)
    df = df.dropna()
    return df
