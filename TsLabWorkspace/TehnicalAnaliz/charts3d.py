#!/usr/bin/env python3
"""3D визуализация для анализа графиков."""

import numpy as np
import pandas as pd
from datetime import datetime


def create_3d_candlestick(df: pd.DataFrame, symbol: str, interval: str, output: str = "chart_3d.html"):
    import plotly.graph_objects as go

    df = df.tail(100).copy()
    df["idx"] = range(len(df))

    fig = go.Figure()

    colors = ["#3fb950" if c >= o else "#f85149"
              for c, o in zip(df["close"], df["open"])]

    fig.add_trace(go.Bar(
        x=df["idx"],
        y=df["close"] - df["open"],
        base=df["open"],
        marker_color=colors,
        opacity=0.7,
        name="Тело свечи",
        width=0.6,
    ))

    fig.add_trace(go.Scatter3d(
        x=df["idx"],
        y=df["high"],
        z=[0.5] * len(df),
        mode="lines",
        line=dict(color="#3fb950", width=2),
        name="Тени",
        showlegend=False,
    ))

    fig.add_trace(go.Scatter3d(
        x=df["idx"],
        y=df["low"],
        z=[-0.5] * len(df),
        mode="lines",
        line=dict(color="#f85149", width=2),
        showlegend=False,
    ))

    ema21 = df["close"].ewm(span=21).mean()
    ema50 = df["close"].ewm(span=50).mean()

    fig.add_trace(go.Scatter3d(
        x=df["idx"],
        y=ema21,
        z=[0.3] * len(df),
        mode="lines",
        line=dict(color="#58a6ff", width=3),
        name="EMA 21",
    ))

    fig.add_trace(go.Scatter3d(
        x=df["idx"],
        y=ema50,
        z=[0.2] * len(df),
        mode="lines",
        line=dict(color="#d29922", width=3),
        name="EMA 50",
    ))

    vol_normalized = df["volume"] / df["volume"].max() * 5
    fig.add_trace(go.Scatter3d(
        x=df["idx"],
        y=df["close"],
        z=-vol_normalized,
        mode="markers",
        marker=dict(
            size=vol_normalized,
            color=colors,
            opacity=0.5,
            symbol="diamond",
        ),
        name="Объём",
    ))

    fig.update_layout(
        title=f"{symbol} — 3D Анализ ({interval})",
        scene=dict(
            xaxis_title="Свечи",
            yaxis_title="Цена",
            zaxis_title="Уровень",
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        ),
        template="plotly_dark",
        width=1200,
        height=800,
    )

    fig.write_html(output)
    return output


def create_3d_heatmap(df: pd.DataFrame, symbol: str, intervals: list, output: str = "heatmap_3d.html"):
    import plotly.graph_objects as go

    from exchanges import get_client

    client = get_client("binance")
    all_data = {}

    for iv in intervals:
        try:
            data = client.fetch_klines(symbol, iv, 100)
            if not data.empty:
                all_data[iv] = data
        except Exception:
            pass

    if not all_data:
        return None

    indicators_to_calc = ["RSI", "MACD", "Stoch", "CCI", "Williams"]

    fig = go.Figure()

    z_data = []
    labels = []

    for iv in intervals:
        if iv not in all_data:
            continue

        data = all_data[iv]
        close = data["close"]

        rsi_val = close.diff().ewm(alpha=1/14).mean()
        rsi_norm = (rsi_val - 30) / 40
        rsi_norm = rsi_norm.clip(0, 1)

        delta = close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1/14).mean()
        macd_line = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        macd_norm = (macd_line - macd_line.min()) / (macd_line.max() - macd_line.min() + 1e-10)

        low_min = data["low"].rolling(14).min()
        high_max = data["high"].rolling(14).max()
        stoch = 100 * (close - low_min) / (high_max - low_min + 1e-10)
        stoch_norm = stoch / 100

        row = []
        for i in range(len(data)):
            row.append([
                rsi_norm.iloc[i] if not np.isnan(rsi_norm.iloc[i]) else 0.5,
                macd_norm.iloc[i] if not np.isnan(macd_norm.iloc[i]) else 0.5,
                stoch_norm.iloc[i] if not np.isnan(stoch_norm.iloc[i]) else 0.5,
            ])

        z_data.append(row[-20:] if len(row) > 20 else row)
        labels.append(iv)

    fig = go.Figure(data=[
        go.Surface(
            z=np.array(z_data),
            x=list(range(20)),
            y=labels,
            colorscale="RdYlGn",
            name="Индикаторы",
        )
    ])

    fig.update_layout(
        title=f"{symbol} — 3D Тепловая карта индикаторов",
        scene=dict(
            xaxis_title="Свечи (последние 20)",
            yaxis_title="Таймфрейм",
            zaxis_title="Значение (0-1)",
        ),
        template="plotly_dark",
        width=1200,
        height=800,
    )

    fig.write_html(output)
    return output


def create_3d_volume_surface(df: pd.DataFrame, symbol: str, output: str = "volume_3d.html"):
    import plotly.graph_objects as go

    df = df.tail(50).copy()

    price_bins = 50
    time_bins = len(df)

    price_min = df["low"].min()
    price_max = df["high"].max()
    price_range = np.linspace(price_min, price_max, price_bins)

    z = np.zeros((price_bins, time_bins))

    for t in range(time_bins):
        row = df.iloc[t]
        for p in range(price_bins):
            if row["low"] <= price_range[p] <= row["high"]:
                z[p, t] = row["volume"] / (price_bins / 3)

    fig = go.Figure(data=[
        go.Surface(
            z=z,
            x=list(range(time_bins)),
            y=price_range,
            colorscale="Viridis",
            name="Объём",
        )
    ])

    fig.update_layout(
        title=f"{symbol} — 3D Профиль объёмов",
        scene=dict(
            xaxis_title="Свечи",
            yaxis_title="Цена",
            zaxis_title="Объём",
        ),
        template="plotly_dark",
        width=1200,
        height=800,
    )

    fig.write_html(output)
    return output


def create_3d_indicator_terrain(df: pd.DataFrame, symbol: str, output: str = "terrain_3d.html"):
    import plotly.graph_objects as go

    df = df.tail(100).copy()
    close = df["close"]

    rsi = close.diff().ewm(alpha=1/14).mean()
    macd_line = close.ewm(span=12).mean() - close.ewm(span=26).mean()
    signal_line = macd_line.ewm(span=9).mean()

    low_min = df["low"].rolling(14).min()
    high_max = df["high"].rolling(14).max()
    stoch_k = 100 * (close - low_min) / (high_max - low_min)

    x = np.arange(len(df))
    y_prices = close.values
    z_macd = macd_line.values
    z_signal = signal_line.values

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=x, y=y_prices, z=z_macd,
        mode="lines",
        line=dict(color="#58a6ff", width=4),
        name="MACD",
    ))

    fig.add_trace(go.Scatter3d(
        x=x, y=y_prices, z=z_signal,
        mode="lines",
        line=dict(color="#f85149", width=4),
        name="Signal",
    ))

    fig.add_trace(go.Scatter3d(
        x=x, y=y_prices, z=rsi.values,
        mode="lines",
        line=dict(color="#3fb950", width=4),
        name="RSI",
    ))

    fig.add_trace(go.Scatter3d(
        x=x, y=y_prices, z=stoch_k.values,
        mode="lines",
        line=dict(color="#d29922", width=4),
        name="Stochastic",
    ))

    fig.update_layout(
        title=f"{symbol} — 3D Ландшафт индикаторов",
        scene=dict(
            xaxis_title="Свечи",
            yaxis_title="Цена",
            zaxis_title="Значение индикатора",
        ),
        template="plotly_dark",
        width=1200,
        height=800,
    )

    fig.write_html(output)
    return output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="3D Визуализация графиков")
    parser.add_argument("--symbol", "-s", default="BTCUSDT")
    parser.add_argument("--type", "-t", choices=["candle", "heatmap", "volume", "terrain", "all"],
                        default="all", help="Тип графика")
    parser.add_argument("--interval", "-i", default="1h")
    parser.add_argument("--output", "-o", default="charts3d")
    args = parser.parse_args()

    from exchanges import get_client

    client = get_client("binance")
    df = client.fetch_klines(args.symbol, args.interval, 200)

    if df.empty:
        print("Ошибка: данные не получены")
        exit(1)

    print(f"Создание 3D графиков для {args.symbol} ({args.interval})...")

    if args.type in ["candle", "all"]:
        print("  Свечной график 3D...")
        create_3d_candlestick(df, args.symbol, args.interval, f"{args.output}_candle.html")

    if args.type in ["heatmap", "all"]:
        print("  Тепловая карта...")
        intervals = ["5m", "15m", "30m", "1h", "4h", "1d"]
        create_3d_heatmap(df, args.symbol, intervals, f"{args.output}_heatmap.html")

    if args.type in ["volume", "all"]:
        print("  Профиль объёмов 3D...")
        create_3d_volume_surface(df, args.symbol, f"{args.output}_volume.html")

    if args.type in ["terrain", "all"]:
        print("  Ландшафт индикаторов...")
        create_3d_indicator_terrain(df, args.symbol, f"{args.output}_terrain.html")

    print(f"\nГотово! Файлы сохранены: {args.output}_*.html")
