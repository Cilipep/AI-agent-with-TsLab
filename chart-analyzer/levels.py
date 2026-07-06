import pandas as pd
import numpy as np


def find_local_extrema(df: pd.DataFrame, window: int = 5) -> tuple:
    highs = []
    lows = []

    for i in range(window, len(df) - window):
        if df["high"].iloc[i] == df["high"].iloc[i - window:i + window + 1].max():
            highs.append((i, df["high"].iloc[i], df["timestamp"].iloc[i]))
        if df["low"].iloc[i] == df["low"].iloc[i - window:i + window + 1].min():
            lows.append((i, df["low"].iloc[i], df["timestamp"].iloc[i]))

    return highs, lows


def cluster_levels(points: list, threshold_pct: float = 0.5) -> list:
    if not points:
        return []

    sorted_points = sorted(points, key=lambda x: x[1])
    clusters = [[sorted_points[0]]]

    for point in sorted_points[1:]:
        last_cluster = clusters[-1]
        avg = np.mean([p[1] for p in last_cluster])
        if abs(point[1] - avg) / avg * 100 <= threshold_pct:
            last_cluster.append(point)
        else:
            clusters.append([point])

    result = []
    for cluster in clusters:
        avg_price = np.mean([p[1] for p in cluster])
        strength = len(cluster)
        result.append({
            "price": round(avg_price, 8),
            "strength": strength,
            "touches": strength,
            "type": "support" if cluster[0][2] < pd.Timestamp.now() else "resistance",
        })

    return sorted(result, key=lambda x: x["price"], reverse=True)


def detect_levels(df: pd.DataFrame, lookback: int = 100) -> dict:
    data = df.tail(lookback)
    highs, lows = find_local_extrema(data, window=max(3, lookback // 20))

    all_points = [(i, p, t) for i, p, t in highs] + [(i, p, t) for i, p, t in lows]
    clustered = cluster_levels(all_points, threshold_pct=0.8)

    current_price = df["close"].iloc[-1]

    support_levels = []
    resistance_levels = []

    for level in clustered:
        if level["price"] < current_price:
            level["distance"] = f"{((current_price / level['price']) - 1) * 100:.2f}%"
            support_levels.append(level)
        else:
            level["distance"] = f"{((level['price'] / current_price) - 1) * 100:.2f}%"
            resistance_levels.append(level)

    return {
        "current_price": round(current_price, 8),
        "support": support_levels[:5],
        "resistance": resistance_levels[:5],
    }
