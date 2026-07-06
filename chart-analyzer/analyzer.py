#!/usr/bin/env python3
"""Chart Analyzer - Анализ графиков с данными из Binance/Bybit."""

import argparse
import json
import sys
from datetime import datetime

from exchanges import get_client
from indicators import compute_all, analyze_trend
from patterns import detect_patterns
from levels import detect_levels
from volume_analysis import analyze_volume
from report import render_report, set_timestamps


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def format_price(p: float) -> str:
    if p < 0.01:
        return f"{p:.8f}"
    elif p < 1:
        return f"{p:.6f}"
    elif p < 100:
        return f"{p:.4f}"
    else:
        return f"{p:.2f}"


def main():
    parser = argparse.ArgumentParser(description="Chart Analyzer - Анализ графиков")
    parser.add_argument("--symbol", "-s", default="BTCUSDT", help="Символ (по умолчанию: BTCUSDT)")
    parser.add_argument("--interval", "-i", default="1h", help="Таймфрейм (по умолчанию: 1h)")
    parser.add_argument("--exchange", "-e", default="binance", choices=["binance", "bybit"],
                        help="Биржа (по умолчанию: binance)")
    parser.add_argument("--limit", "-l", type=int, default=200, help="Количество свечей (по умолчанию: 200)")
    parser.add_argument("--output", "-o", help="Путь для HTML-отчёта (опционально)")
    parser.add_argument("--json", "-j", action="store_true", help="Вывод в формате JSON")
    args = parser.parse_args()

    print(f"Загрузка данных {args.symbol} с {args.exchange} ({args.interval})...")

    client = get_client(args.exchange)
    df = client.fetch_klines(args.symbol, args.interval, args.limit)

    if df.empty:
        print("Ошибка: данные не получены", file=sys.stderr)
        sys.exit(1)

    set_timestamps(df["timestamp"])

    price = df["close"].iloc[-1]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    indicators = compute_all(df)
    trend = analyze_trend(df, indicators)
    volume = analyze_volume(df)
    levels = detect_levels(df)
    patterns_df = detect_patterns(df)

    if args.json:
        output = {
            "symbol": args.symbol,
            "interval": args.interval,
            "exchange": args.exchange,
            "price": price,
            "trend": trend,
            "volume": volume,
            "levels": levels,
            "patterns": [
                {"pattern": r["pattern"], "signal": r["signal"]}
                for _, r in patterns_df.iterrows() if r["pattern"]
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print_section(f"{args.symbol} — Тренд и индикаторы")
    print(f"  Цена:          {format_price(price)}")
    print(f"  Тренд:         {trend['trend']}")
    print(f"  Моментум:      {trend['momentum']} (RSI {trend['rsi']})")
    print(f"  MACD:          {trend['macd_signal']}")
    print(f"  ATR:           {trend['atr']}")
    print(f"  vs EMA21:      {trend['price_vs_ema21']}")
    print(f"  vs EMA50:      {trend['price_vs_ema50']}")

    print_section("Объём")
    print(f"  Текущий:       {volume['last_volume']}")
    print(f"  Средний:       {volume['avg_volume']}")
    print(f"  Отношение:     {volume['volume_ratio']}x ({volume['volume_status']})")
    print(f"  OBV тренд:     {volume['obv_trend']}")

    if volume["spikes"]:
        print("\n  Всплески объёма:")
        for s in volume["spikes"]:
            direction = "↑" if s["direction"] == "buy" else "↓"
            print(f"    {direction} {s['timestamp']} — {s['volume']} ({s['ratio']}x)")

    print_section("Уровни поддержки / сопротивления")
    if levels["support"]:
        print("  Поддержка:")
        for l in levels["support"]:
            print(f"    {format_price(l['price'])} ({l['touches']} касаний, -{l['distance']})")
    else:
        print("  Поддержка: не найдена")

    if levels["resistance"]:
        print("  Сопротивление:")
        for l in levels["resistance"]:
            print(f"    {format_price(l['price'])} ({l['touches']} касаний, +{l['distance']})")
    else:
        print("  Сопротивление: не найдено")

    print_section("Свечные паттерны (последние 20)")
    recent = patterns_df.tail(20)
    found_any = False
    for idx, row in recent.iterrows():
        if row["pattern"]:
            found_any = True
            print(f"  {df['timestamp'].iloc[idx]}  {row['pattern']}  [{row['signal']}]")
    if not found_any:
        print("  Сигнальных паттернов не обнаружено")

    if args.output:
        html = render_report(
            args.symbol, args.interval, args.exchange,
            timestamp, price, trend, volume, levels, recent,
        )
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML-отчёт сохранён: {args.output}")

    print()


if __name__ == "__main__":
    main()
