import pandas as pd
import numpy as np


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    mid = sma(series, period)
    std = series.rolling(window=period).std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    return upper, mid, lower


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    low_min = df["low"].rolling(window=k_period).min()
    high_max = df["high"].rolling(window=k_period).max()
    k = 100 * (df["close"] - low_min) / (high_max - low_min)
    d = k.rolling(window=d_period).mean()
    return k, d


def stochastic_rsi(series: pd.Series, rsi_period: int = 14, stoch_period: int = 14, k_smooth: int = 3, d_smooth: int = 3):
    rsi_val = rsi(series, rsi_period)
    low_rsi = rsi_val.rolling(window=stoch_period).min()
    high_rsi = rsi_val.rolling(window=stoch_period).max()
    stoch_rsi = (rsi_val - low_rsi) / (high_rsi - low_rsi) * 100
    k = stoch_rsi.rolling(window=k_smooth).mean()
    d = k.rolling(window=d_smooth).mean()
    return k, d


def williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_max = df["high"].rolling(window=period).max()
    low_min = df["low"].rolling(window=period).min()
    wr = -100 * (high_max - df["close"]) / (high_max - low_min)
    return wr


def cci(df: pd.DataFrame, period: int = 14) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3
    sma_tp = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    cci_val = (tp - sma_tp) / (0.015 * mad)
    return cci_val


def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    tr = atr(df, 1)

    atr_smooth = tr.ewm(alpha=1 / period, min_periods=period).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1 / period, min_periods=period).mean() / atr_smooth)
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period, min_periods=period).mean() / atr_smooth)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx_val = dx.ewm(alpha=1 / period, min_periods=period).mean()

    return adx_val


def pivot_points(df: pd.DataFrame, method: str = "classic") -> dict:
    high = df["high"].iloc[-1]
    low = df["low"].iloc[-1]
    close = df["close"].iloc[-1]

    if method == "classic":
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)
    elif method == "fibonacci":
        pivot = (high + low + close) / 3
        r1 = pivot + 0.382 * (high - low)
        r2 = pivot + 0.618 * (high - low)
        r3 = pivot + 1.0 * (high - low)
        s1 = pivot - 0.382 * (high - low)
        s2 = pivot - 0.618 * (high - low)
        s3 = pivot - 1.0 * (high - low)
    elif method == "woodie":
        pivot = (high + low + 2 * close) / 4
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = r1 + (high - low)
        s3 = s1 - (high - low)
    else:
        pivot = (high + low + close) / 3
        r1 = s1 = r2 = s2 = r3 = s3 = pivot

    return {
        "pivot": round(pivot, 1),
        "r1": round(r1, 1), "r2": round(r2, 1), "r3": round(r3, 1),
        "s1": round(s1, 1), "s2": round(s2, 1), "s3": round(s3, 1),
    }


def compute_all(df: pd.DataFrame) -> dict:
    close = df["close"]
    indicators = {}

    indicators["ema_9"] = ema(close, 9)
    indicators["ema_21"] = ema(close, 21)
    indicators["ema_50"] = ema(close, 50)
    indicators["sma_20"] = sma(close, 20)
    indicators["rsi"] = rsi(close)
    indicators["macd_line"], indicators["macd_signal"], indicators["macd_hist"] = macd(close)
    indicators["bb_upper"], indicators["bb_mid"], indicators["bb_lower"] = bollinger_bands(close)
    indicators["atr"] = atr(df)
    indicators["stoch_k"], indicators["stoch_d"] = stochastic(df)
    indicators["stochrsi_k"], indicators["stochrsi_d"] = stochastic_rsi(close)
    indicators["williams_r"] = williams_r(df)
    indicators["cci"] = cci(df)
    indicators["adx"] = adx(df)
    indicators["pivot"] = pivot_points(df, "classic")
    indicators["pivot_fib"] = pivot_points(df, "fibonacci")
    indicators["pivot_woodie"] = pivot_points(df, "woodie")

    return indicators


def analyze_trend(df: pd.DataFrame, indicators: dict) -> dict:
    close = df["close"].iloc[-1]
    ema9 = indicators["ema_9"].iloc[-1]
    ema21 = indicators["ema_21"].iloc[-1]
    ema50 = indicators["ema_50"].iloc[-1]
    rsi_val = indicators["rsi"].iloc[-1]
    macd_val = indicators["macd_line"].iloc[-1]
    macd_sig = indicators["macd_signal"].iloc[-1]
    stoch_k = indicators["stoch_k"].iloc[-1]
    stochrsi_k = indicators["stochrsi_k"].iloc[-1]
    williams = indicators["williams_r"].iloc[-1]
    cci_val = indicators["cci"].iloc[-1]
    adx_val = indicators["adx"].iloc[-1]

    trend = "Нет тренда"
    if close > ema21 > ema50:
        trend = "Восходящий"
    elif close < ema21 < ema50:
        trend = "Нисходящий"
    elif close > ema21:
        trend = "Умеренно бычий"
    elif close < ema21:
        trend = "Умеренно медвежий"

    momentum = "Нейтральный"
    if rsi_val > 70:
        momentum = "Перекупленность"
    elif rsi_val < 30:
        momentum = "Перепроданность"
    elif rsi_val > 60:
        momentum = "Бычий"
    elif rsi_val < 40:
        momentum = "Медвежий"

    macd_signal = "Нейтрально"
    if macd_val > macd_sig:
        macd_signal = "Бычий кроссовер"
    elif macd_val < macd_sig:
        macd_signal = "Медвежий кроссовер"

    stoch_signal = "Нейтрально"
    if stoch_k > 80:
        stoch_signal = "Перекупленность"
    elif stoch_k < 20:
        stoch_signal = "Перепроданность"

    stochrsi_signal = "Нейтрально"
    if stochrsi_k > 80:
        stochrsi_signal = "Перекупленность"
    elif stochrsi_k < 20:
        stochrsi_signal = "Перепроданность"

    williams_signal = "Нейтрально"
    if williams > -20:
        williams_signal = "Перекупленность"
    elif williams < -80:
        williams_signal = "Перепроданность"

    cci_signal = "Нейтрально"
    if cci_val > 100:
        cci_signal = "Перекупленность"
    elif cci_val < -100:
        cci_signal = "Перепроданность"

    trend_strength = "Слабый"
    if adx_val > 25:
        trend_strength = "Сильный"
    elif adx_val > 20:
        trend_strength = "Умеренный"

    return {
        "trend": trend,
        "momentum": momentum,
        "macd_signal": macd_signal,
        "stoch_signal": stoch_signal,
        "stochrsi_signal": stochrsi_signal,
        "williams_signal": williams_signal,
        "cci_signal": cci_signal,
        "trend_strength": trend_strength,
        "price_vs_ema21": f"{((close / ema21) - 1) * 100:+.2f}%",
        "price_vs_ema50": f"{((close / ema50) - 1) * 100:+.2f}%",
        "rsi": f"{rsi_val:.1f}",
        "stoch_k": f"{stoch_k:.1f}",
        "stochrsi_k": f"{stochrsi_k:.1f}",
        "williams_r": f"{williams:.1f}",
        "cci": f"{cci_val:.1f}",
        "adx": f"{adx_val:.1f}",
        "atr": f"{indicators['atr'].iloc[-1]:.4f}",
        "pivot": indicators["pivot"],
    }
