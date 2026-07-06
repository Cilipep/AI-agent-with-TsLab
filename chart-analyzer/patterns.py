import pandas as pd
import numpy as np


def body_size(df: pd.DataFrame) -> pd.Series:
    return abs(df["close"] - df["open"])


def upper_shadow(df: pd.DataFrame) -> pd.Series:
    return df["high"] - df[["open", "close"]].max(axis=1)


def lower_shadow(df: pd.DataFrame) -> pd.Series:
    return df[["open", "close"]].min(axis=1) - df["low"]


def total_range(df: pd.DataFrame) -> pd.Series:
    return df["high"] - df["low"]


def is_bullish(df: pd.DataFrame) -> pd.Series:
    return df["close"] > df["open"]


def is_bearish(df: pd.DataFrame) -> pd.Series:
    return df["close"] < df["open"]


def detect_patterns(df: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)
    result["pattern"] = ""
    result["signal"] = ""

    rng = total_range(df)
    body = body_size(df)
    ushadow = upper_shadow(df)
    lshadow = lower_shadow(df)
    bull = is_bullish(df)
    bear = is_bearish(df)

    # Doji - body很小相对于全范围
    doji = body < rng * 0.05
    result.loc[doji, "pattern"] = "Доджи"
    result.loc[doji, "signal"] = "Нейтрально"

    # Hammer - 下影线长，上影线短，在下跌趋势中
    hammer = (lshadow > body * 2) & (ushadow < body * 0.5) & (rng > 0)
    result.loc[hammer & ~doji, "pattern"] = "Молот"
    result.loc[hammer & ~doji, "signal"] = "Бычий"

    # Inverted Hammer - 上影线长，下影线短
    inv_hammer = (ushadow > body * 2) & (lshadow < body * 0.5) & (rng > 0)
    result.loc[inv_hammer & ~doji, "pattern"] = "Перевёрнутый молот"
    result.loc[inv_hammer & ~doji, "signal"] = "Бычий"

    # Bullish Engulfing - 当前是看涨且完全包围前一个看跌
    eng_bull = bull.shift(1) == False  # prev bearish
    eng_bull &= bull  # current bullish
    eng_bull &= df["open"] <= df["close"].shift(1)
    eng_bull &= df["close"] >= df["open"].shift(1)
    result.loc[eng_bull, "pattern"] = "Бычье поглощение"
    result.loc[eng_bull, "signal"] = "Бычий"

    # Bearish Engulfing
    eng_bear = bull.shift(1) == True  # prev bullish
    eng_bear &= bear  # current bearish
    eng_bear &= df["open"] >= df["close"].shift(1)
    eng_bear &= df["close"] <= df["open"].shift(1)
    result.loc[eng_bear, "pattern"] = "Медвежье поглощение"
    result.loc[eng_bear, "signal"] = "Медвежий"

    # Morning Star (3-bar pattern)
    star_body = body.shift(1)
    star_range = rng.shift(1)
    ms = (bear.shift(2)) & (star_body < star_range * 0.1) & (bull)
    ms &= df["close"] > (df["open"].shift(2) + df["close"].shift(2)) / 2
    result.loc[ms, "pattern"] = "Утренняя звезда"
    result.loc[ms, "signal"] = "Сильный бычий"

    # Evening Star
    es = (bull.shift(2)) & (star_body < star_range * 0.1) & (bear)
    es &= df["close"] < (df["open"].shift(2) + df["close"].shift(2)) / 2
    result.loc[es, "pattern"] = "Вечерняя звезда"
    result.loc[es, "signal"] = "Сильный медвежий"

    # Three White Soldiers
    tws = bull & bull.shift(1) & bull.shift(2)
    tws &= df["close"] > df["close"].shift(1)
    tws &= df["close"].shift(1) > df["close"].shift(2)
    tws &= body > rng * 0.6
    tws_empty = tws & (result["pattern"] == "")
    result.loc[tws_empty, "pattern"] = "Три белых солдата"
    result.loc[tws_empty, "signal"] = "Сильный бычий"

    # Three Black Crows
    tbc = bear & bear.shift(1) & bear.shift(2)
    tbc &= df["close"] < df["close"].shift(1)
    tbc &= df["close"].shift(1) < df["close"].shift(2)
    tbc &= body > rng * 0.6
    tbc_empty = tbc & (result["pattern"] == "")
    result.loc[tbc_empty, "pattern"] = "Три чёрных ворона"
    result.loc[tbc_empty, "signal"] = "Сильный медвежий"

    return result
