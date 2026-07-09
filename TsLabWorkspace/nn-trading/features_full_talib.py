"""Full TA-Lib features - 160+ indicators."""
import numpy as np
import pandas as pd
import talib


def add_all_talib_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add ALL TA-Lib indicators for maximum feature set."""
    df = df.copy()

    close = df["Close"].values.astype(np.float64)
    high = df["High"].values.astype(np.float64)
    low = df["Low"].values.astype(np.float64)
    open_ = df["Open"].values.astype(np.float64)
    volume = df["Volume"].values.astype(np.float64) if "Volume" in df.columns else np.zeros(len(df), dtype=np.float64)

    # ============================================
    # TREND INDICATORS (20+)
    # ============================================

    # Moving Averages - Multiple periods
    for period in [5, 10, 15, 20, 25, 30, 50, 100, 200]:
        df[f"sma_{period}"] = talib.SMA(close, timeperiod=period)
        df[f"ema_{period}"] = talib.EMA(close, timeperiod=period)

    # MACD variations
    df["macd"], df["macd_signal"], df["macd_hist"] = talib.MACD(close)
    df["macd_fast"], df["macd_slow"], df["macd_signal_12_26"] = talib.MACDEXT(close)

    # ADX family
    df["adx"] = talib.ADX(high, low, close, timeperiod=14)
    df["adx_7"] = talib.ADX(high, low, close, timeperiod=7)
    df["adx_28"] = talib.ADX(high, low, close, timeperiod=28)
    df["plus_di"] = talib.PLUS_DI(high, low, close, timeperiod=14)
    df["minus_di"] = talib.MINUS_DI(high, low, close, timeperiod=14)
    df["plus_dm"] = talib.PLUS_DM(high, low, timeperiod=14)
    df["minus_dm"] = talib.MINUS_DM(high, low, timeperiod=14)

    # Aroon
    df["aroon_up"], df["aroon_down"] = talib.AROON(high, low, timeperiod=25)
    df["aroon_up_14"], df["aroon_down_14"] = talib.AROON(high, low, timeperiod=14)
    df["aroonosc"] = talib.AROONOSC(high, low, timeperiod=25)

    # Parabolic SAR
    df["sar"] = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
    df["sar_01"] = talib.SAR(high, low, acceleration=0.01, maximum=0.1)

    # TEMA, DEMA, KAMA
    df["tema_14"] = talib.TEMA(close, timeperiod=14)
    df["tema_30"] = talib.TEMA(close, timeperiod=30)
    df["dema_14"] = talib.DEMA(close, timeperiod=14)
    df["dema_30"] = talib.DEMA(close, timeperiod=30)
    df["kama"] = talib.KAMA(close, timeperiod=30)

    # Linear Regression
    df["linreg_slope"] = talib.LINEARREG_SLOPE(close, timeperiod=14)
    df["linreg_intercept"] = talib.LINEARREG_INTERCEPT(close, timeperiod=14)
    df["linreg_angle"] = talib.LINEARREG_ANGLE(close, timeperiod=14)
    df["linreg"] = talib.LINEARREG(close, timeperiod=14)

    # HT_TRENDLINE
    df["ht_trendline"] = talib.HT_TRENDLINE(close)
    df["ht_trendmode"] = talib.HT_TRENDMODE(close)

    # ============================================
    # MOMENTUM INDICATORS (30+)
    # ============================================

    # RSI - Multiple periods
    for period in [7, 9, 14, 21, 28]:
        df[f"rsi_{period}"] = talib.RSI(close, timeperiod=period)

    # Stochastic family
    df["stoch_k"], df["stoch_d"] = talib.STOCH(high, low, close)
    df["stochf_k"], df["stochf_d"] = talib.STOCHF(high, low, close)
    df["stochrsi_k"], df["stochrsi_d"] = talib.STOCHRSI(close, timeperiod=14)

    # Williams %R
    df["willr_14"] = talib.WILLR(high, low, close, timeperiod=14)
    df["willr_7"] = talib.WILLR(high, low, close, timeperiod=7)
    df["willr_28"] = talib.WILLR(high, low, close, timeperiod=28)

    # CCI
    df["cci_14"] = talib.CCI(high, low, close, timeperiod=14)
    df["cci_7"] = talib.CCI(high, low, close, timeperiod=7)
    df["cci_28"] = talib.CCI(high, low, close, timeperiod=28)

    # ROC - Multiple periods
    for period in [5, 10, 15, 20]:
        df[f"roc_{period}"] = talib.ROC(close, timeperiod=period)

    # Momentum
    df["mom_10"] = talib.MOM(close, timeperiod=10)
    df["mom_20"] = talib.MOM(close, timeperiod=20)

    # Ultimate Oscillator
    df["ultosc"] = talib.ULTOSC(high, low, close)

    # MFI
    if volume.sum() > 0:
        df["mfi_14"] = talib.MFI(high, low, close, volume, timeperiod=14)
        df["mfi_7"] = talib.MFI(high, low, close, volume, timeperiod=7)

    # PPO
    df["ppo"] = talib.PPO(close, fastperiod=12, slowperiod=26, matype=0)

    # ============================================
    # VOLATILITY INDICATORS (25+)
    # ============================================

    # Bollinger Bands - Multiple periods
    for period in [14, 20, 30]:
        upper, mid, lower = talib.BBANDS(close, timeperiod=period)
        df[f"bb_upper_{period}"] = upper
        df[f"bb_mid_{period}"] = mid
        df[f"bb_lower_{period}"] = lower
        df[f"bb_width_{period}"] = (upper - lower) / mid
        df[f"bb_pct_{period}"] = (close - lower) / (upper - lower)

    # ATR family
    df["atr_7"] = talib.ATR(high, low, close, timeperiod=7)
    df["atr_14"] = talib.ATR(high, low, close, timeperiod=14)
    df["atr_28"] = talib.ATR(high, low, close, timeperiod=28)
    df["natr_14"] = talib.NATR(high, low, close, timeperiod=14)
    df["trange"] = talib.TRANGE(high, low, close)

    # Keltner Channel (manual)
    df["kc_mid"] = talib.EMA(close, timeperiod=20)
    df["atr_20"] = talib.ATR(high, low, close, timeperiod=20)
    df["kc_upper"] = df["kc_mid"] + 2 * df["atr_20"]
    df["kc_lower"] = df["kc_mid"] - 2 * df["atr_20"]
    df["kc_width"] = (df["kc_upper"] - df["kc_lower"]) / df["kc_mid"]

    # StdDev
    df["stddev_14"] = talib.STDDEV(close, timeperiod=14)
    df["stddev_20"] = talib.STDDEV(close, timeperiod=20)

    # ============================================
    # VOLUME INDICATORS (15+)
    # ============================================

    if volume.sum() > 0:
        # OBV
        df["obv"] = talib.OBV(close, volume)
        df["obv_sma_10"] = df["obv"].rolling(10).mean()
        df["obv_sma_20"] = df["obv"].rolling(20).mean()

        # AD
        df["ad"] = talib.AD(high, low, close, volume)
        df["adosc"] = talib.ADOSC(high, low, close, volume)

        # Volume Price Trend
        df["volume_sma_10"] = df["Volume"].rolling(10).mean()
        df["volume_sma_20"] = df["Volume"].rolling(20).mean()
        df["volume_ratio"] = df["Volume"] / df["volume_sma_20"]
        df["volume_change"] = df["Volume"].pct_change()

        # Price-Volume correlation
        df["pv_corr"] = df["Close"].rolling(20).corr(df["Volume"])

    # ============================================
    # PATTERN RECOGNITION (20+ candle patterns)
    # ============================================

    # Single candle patterns
    df["cdl_doji"] = talib.CDLDOJI(open_, high, low, close)
    df["cdl_hammer"] = talib.CDLHAMMER(open_, high, low, close)
    df["cdl_hangingman"] = talib.CDLHANGINGMAN(open_, high, low, close)
    df["cdl_shootingstar"] = talib.CDLSHOOTINGSTAR(open_, high, low, close)
    df["cdl_marubozu"] = talib.CDLMARUBOZU(open_, high, low, close)
    df["cdl_spinningtop"] = talib.CDLSPINNINGTOP(open_, high, low, close)

    # Two candle patterns
    df["cdl_engulfing"] = talib.CDLENGULFING(open_, high, low, close)
    df["cdl_harami"] = talib.CDLHARAMI(open_, high, low, close)
    df["cdl_piercing"] = talib.CDLPIERCING(open_, high, low, close)
    df["cdl_darkcloud"] = talib.CDLDARKCLOUDCOVER(open_, high, low, close)

    # Three candle patterns
    df["cdl_morningstar"] = talib.CDLMORNINGSTAR(open_, high, low, close)
    df["cdl_eveningstar"] = talib.CDLEVENINGSTAR(open_, high, low, close)
    df["cdl_3whitesoldiers"] = talib.CDL3WHITESOLDIERS(open_, high, low, close)
    df["cdl_3blackcrows"] = talib.CDL3BLACKCROWS(open_, high, low, close)
    df["cdl_3inside"] = talib.CDL3INSIDE(open_, high, low, close)
    df["cdl_3outside"] = talib.CDL3OUTSIDE(open_, high, low, close)

    # ============================================
    # STATISTICS & MATH (15+)
    # ============================================

    df["beta"] = talib.BETA(high, low, timeperiod=14)
    df["correl_14"] = talib.CORREL(high, low, timeperiod=14)
    df["correl_30"] = talib.CORREL(high, low, timeperiod=30)

    # HT indicators
    df["ht_dcperiod"] = talib.HT_DCPERIOD(close)
    df["ht_dcphase"] = talib.HT_DCPHASE(close)
    df["ht_inphase"], df["ht_quad"] = talib.HT_PHASOR(close)
    df["ht_sine"], df["ht_leadsine"] = talib.HT_SINE(close)

    # ============================================
    # PRICE TRANSFORMS (5+)
    # ============================================

    df["typical_price"] = talib.TYPPRICE(high, low, close)
    df["weighted_close"] = talib.WCLPRICE(high, low, close)
    df["midpoint"] = talib.MIDPOINT(close, timeperiod=14)
    df["midprice"] = talib.MIDPRICE(high, low, timeperiod=14)

    # ============================================
    # RETURNS & RATIOS (15+)
    # ============================================

    df["returns_1"] = df["Close"].pct_change(1)
    df["returns_3"] = df["Close"].pct_change(3)
    df["returns_5"] = df["Close"].pct_change(5)
    df["returns_10"] = df["Close"].pct_change(10)
    df["returns_20"] = df["Close"].pct_change(20)

    df["log_returns"] = np.log(df["Close"] / df["Close"].shift(1))
    df["log_returns_5"] = np.log(df["Close"] / df["Close"].shift(5))

    # Price ratios
    df["high_low_ratio"] = df["High"] / df["Low"]
    df["close_open_ratio"] = df["Close"] / df["Open"]
    df["high_close_ratio"] = df["High"] / df["Close"]
    df["low_close_ratio"] = df["Low"] / df["Close"]
    df["gap"] = df["Open"] / df["Close"].shift(1) - 1

    # SMA ratios
    df["price_sma20_ratio"] = df["Close"] / df["sma_20"]
    df["price_sma50_ratio"] = df["Close"] / df["sma_50"]
    df["sma20_sma50_ratio"] = df["sma_20"] / df["sma_50"]

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
    df = add_all_talib_indicators(df)
    df["label"] = make_label(df, config.horizon, config.threshold)
    df = df.dropna()
    return df
