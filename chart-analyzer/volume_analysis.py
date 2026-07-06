import pandas as pd
import numpy as np


def analyze_volume(df: pd.DataFrame, period: int = 20) -> dict:
    if "volume" not in df.columns or df["volume"].isna().all():
        return {"status": "no_volume_data"}

    vol = df["volume"]
    avg_vol = vol.rolling(window=period).mean()
    vol_std = vol.rolling(window=period).std()

    last_vol = vol.iloc[-1]
    last_avg = avg_vol.iloc[-1]
    vol_ratio = last_vol / last_avg if last_avg > 0 else 0

    price_change = df["close"].iloc[-1] - df["close"].iloc[-2]
    vol_direction = "buy" if price_change > 0 else "sell"

    recent = df.tail(period)
    vol_spikes = []
    for i in range(1, len(recent)):
        if recent["volume"].iloc[i] > avg_vol.iloc[-(period - i)] * 2:
            vol_spikes.append({
                "timestamp": str(recent["timestamp"].iloc[i]),
                "volume": round(recent["volume"].iloc[i], 2),
                "ratio": round(recent["volume"].iloc[i] / avg_vol.iloc[-(period - i)], 2),
                "direction": "buy" if recent["close"].iloc[i] > recent["open"].iloc[i] else "sell",
            })

    obv = [0.0]
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i - 1]:
            obv.append(obv[-1] + df["volume"].iloc[i])
        elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
            obv.append(obv[-1] - df["volume"].iloc[i])
        else:
            obv.append(obv[-1])

    obv_series = pd.Series(obv, index=df.index)
    obv_trend = "Восходящий" if obv_series.iloc[-1] > obv_series.iloc[-period] else "Нисходящий"

    return {
        "last_volume": round(last_vol, 2),
        "avg_volume": round(last_avg, 2),
        "volume_ratio": round(vol_ratio, 2),
        "volume_status": (
            "Высокий" if vol_ratio > 2 else
            "Повышенный" if vol_ratio > 1.5 else
            "Нормальный" if vol_ratio > 0.8 else
            "Низкий"
        ),
        "direction": vol_direction,
        "obv_trend": obv_trend,
        "spikes": vol_spikes[:5],
    }
