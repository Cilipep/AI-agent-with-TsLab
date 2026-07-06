#!/usr/bin/env python3
"""Мультивалютный мультитаймфрейм-резюме для всех инструментов."""

import sys
import time
from datetime import datetime
from exchanges import get_client
from indicators import compute_all, analyze_trend
from volume_analysis import analyze_volume
from orderbook import ORDERBOOK_CLIENTS, analyze_orderbook
from symbols import get_all_symbols, get_top_by_volume


TIMEFRAMES = {
    "5м": "5m",
    "15м": "15m",
    "30м": "30m",
    "1ч": "1h",
    "4ч": "4h",
    "1д": "1d",
}


def analyze_single(client, symbol: str, interval: str, limit: int = 200) -> dict:
    try:
        df = client.fetch_klines(symbol, interval, limit)
        if df.empty or len(df) < 30:
            return None

        indicators = compute_all(df)
        trend = analyze_trend(df, indicators)
        volume = analyze_volume(df)

        return {
            "trend": trend,
            "volume": volume,
            "price": df["close"].iloc[-1],
        }
    except Exception:
        return None


def get_trend_score(trend: dict) -> int:
    score = 0

    t = trend["trend"].lower()
    if "восходящий" in t:
        score += 2
    elif "умеренно бычий" in t:
        score += 1
    elif "нисходящий" in t:
        score -= 2
    elif "умеренно медвежий" in t:
        score -= 1

    rsi = float(trend["rsi"])
    if 40 <= rsi <= 60:
        score += 1
    elif rsi < 30:
        score += 2
    elif rsi > 70:
        score -= 2

    if "бычий" in trend["macd_signal"].lower():
        score += 1
    elif "медвежий" in trend["macd_signal"].lower():
        score -= 1

    return score


def get_signal_emoji(score: int) -> str:
    if score >= 4:
        return "🟢🟢"
    elif score >= 2:
        return "🟢"
    elif score >= 0:
        return "⚪"
    elif score >= -2:
        return "🔴"
    else:
        return "🔴🔴"


def get_trend_emoji(trend: str) -> str:
    t = trend.lower()
    if "восходящий" in t:
        return "🟢"
    elif "бычий" in t:
        return "🟡"
    elif "нисходящий" in t:
        return "🔴"
    elif "медвежий" in t:
        return "🟠"
    return "⚪"


def generate_multi_mtf_summary(symbols: list, exchange: str = "binance") -> str:
    client = get_client(exchange)
    all_data = {}

    print(f"Анализ {len(symbols)} монет x {len(TIMEFRAMES)} ТФ ({exchange})...", file=sys.stderr)

    for i, symbol in enumerate(symbols):
        print(f"  [{i+1}/{len(symbols)}] {symbol}...", file=sys.stderr)
        symbol_data = {}

        for tf_name, tf_interval in TIMEFRAMES.items():
            result = analyze_single(client, symbol, tf_interval)
            if result:
                symbol_data[tf_name] = result
            time.sleep(0.1)

        if symbol_data:
            try:
                ob_client = ORDERBOOK_CLIENTS[exchange]()
                df = client.fetch_klines(symbol, "1h", 10)
                if not df.empty:
                    book = ob_client.fetch(symbol, 50)
                    ob = analyze_orderbook(book, df["close"].iloc[-1])
                    symbol_data["orderbook"] = ob
            except Exception:
                pass

            all_data[symbol] = symbol_data

        time.sleep(0.05)

    lines = []
    lines.append(f"{'=' * 120}")
    lines.append(f"  МУЛЬТИВАЛЮТНЫЙ МУЛЬТИТАЙМФРЕЙМ-АНАЛИЗ")
    lines.append(f"  Биржа: {exchange} | {len(symbols)} монет | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"{'=' * 120}")

    tf_names = list(TIMEFRAMES.keys())

    header = f"  {'Монета':<12}"
    for tf in tf_names:
        header += f" {tf:>6}"
    header += f" {'Средняя':>8} {'Стакан':>6} {'ИТОГО':>6}"
    lines.append(f"\n{'─' * 120}")
    lines.append(header)
    lines.append(f"{'─' * 120}")

    rankings = []

    for symbol in all_data:
        data = all_data[symbol]
        row = f"  {symbol:<12}"
        scores = []

        for tf in tf_names:
            if tf in data:
                t = data[tf]["trend"]
                score = get_trend_score(t)
                scores.append(score)
                emoji = get_trend_emoji(t["trend"])
                row += f" {emoji}{t['rsi']:>4}"
            else:
                row += f" {'--':>6}"

        avg_score = sum(scores) / len(scores) if scores else 0

        ob_signal = "⚪"
        if "orderbook" in data and "error" not in data.get("orderbook", {}):
            ob = data["orderbook"]
            imb = ob.get("imbalance", 0)
            if imb > 0.2:
                ob_signal = "🟢"
            elif imb < -0.2:
                ob_signal = "🔴"

        overall = get_signal_emoji(avg_score)

        row += f" {avg_score:>+7.1f} {ob_signal:>6} {overall:>6}"
        lines.append(row)

        rankings.append((symbol, avg_score, ob_signal, data))

    lines.append(f"{'─' * 120}")

    lines.append(f"\n{'=' * 120}")
    lines.append(f"  РЕЙТИНГ ПО СРЕДНЕЙ ОЦЕНКЕ")
    lines.append(f"{'=' * 120}")

    rankings.sort(key=lambda x: x[1], reverse=True)

    lines.append(f"\n  {'#':<4} {'Монета':<12} {'Оценка':>6} {'Сигнал':<28}")
    lines.append(f"  {'─' * 60}")

    for i, (symbol, avg_score, ob_sig, data) in enumerate(rankings, 1):
        if avg_score >= 3:
            signal = "🟢🟢 КАТЕГОРИЧЕСКИ ПОКУПАТЬ"
        elif avg_score >= 2:
            signal = "🟢 ПОКУПАТЬ"
        elif avg_score >= 1:
            signal = "🟢 СЛАБО ПОКУПАТЬ"
        elif avg_score >= 0:
            signal = "⚪ НЕЙТРАЛЬНО"
        elif avg_score >= -1:
            signal = "🔴 СЛАБО ПРОДАВАТЬ"
        elif avg_score >= -3:
            signal = "🔴 ПРОДАВАТЬ"
        else:
            signal = "🔴🔴 КАТЕГОРИЧЕСКИ ПРОДАВАТЬ"

        lines.append(f"  {i:<4} {symbol:<12} {avg_score:>+6.1f} {signal}")

    lines.append(f"\n{'=' * 120}")

    bull = sum(1 for _, s, _, _ in rankings if s > 0)
    bear = sum(1 for _, s, _, _ in rankings if s < 0)
    neut = sum(1 for _, s, _, _ in rankings if s == 0)
    lines.append(f"  ИТОГО: 🟢 Бычий: {bull} | 🔴 Медвежий: {bear} | ⚪ Нейтрал: {neut}")

    lines.append(f"\n{'=' * 120}")
    lines.append(f"  ТОП-10 ЛУЧШИХ ДЛЯ ПОКУПКИ")
    lines.append(f"{'=' * 120}")

    top_buy = [x for x in rankings if x[1] > 0][:10]
    for i, (symbol, avg_score, ob_sig, data) in enumerate(top_buy, 1):
        vol_4h = ""
        if "4ч" in data:
            v = data["4ч"]["volume"]
            vol_4h = f"{v['volume_ratio']}x" if v.get("volume_ratio") else ""

        price_4h = data.get("4ч", {}).get("price", 0)
        lines.append(f"  {i}. {symbol:<12} Оценка: {avg_score:+.1f} | Цена: {price_4h:>12,.2f} | Объём: {vol_4h}")

    lines.append(f"\n{'=' * 120}")
    lines.append(f"  ТОП-10 ЛУЧШИХ ДЛЯ ПРОДАЖИ")
    lines.append(f"{'=' * 120}")

    top_sell = [x for x in rankings if x[1] < 0][-10:]
    top_sell.reverse()
    for i, (symbol, avg_score, ob_sig, data) in enumerate(top_sell, 1):
        vol_4h = ""
        if "4ч" in data:
            v = data["4ч"]["volume"]
            vol_4h = f"{v['volume_ratio']}x" if v.get("volume_ratio") else ""

        price_4h = data.get("4ч", {}).get("price", 0)
        lines.append(f"  {i}. {symbol:<12} Оценка: {avg_score:+.1f} | Цена: {price_4h:>12,.2f} | Объём: {vol_4h}")

    lines.append(f"\n{'=' * 120}")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Мультивалютный мультитаймфрейм-анализатор")
    parser.add_argument("--symbols", "-s", nargs="+", help="Список монет (пусто = все)")
    parser.add_argument("--all", "-a", action="store_true", help="Все доступные монеты")
    parser.add_argument("--top", "-t", type=int, default=0, help="Топ N монет по объёму")
    parser.add_argument("--exchange", "-e", default="binance", choices=["binance", "bybit"])
    parser.add_argument("--output", "-o", help="Сохранить в файл")
    args = parser.parse_args()

    if args.all:
        raw = get_all_symbols(args.exchange, "USDT")
        symbols = [s["symbol"] for s in raw]
        print(f"Загружено {len(symbols)} монет", file=sys.stderr)
    elif args.top > 0:
        raw = get_top_by_volume(args.exchange, "USDT", args.top)
        symbols = [s["symbol"] for s in raw]
        print(f"Загружен топ-{args.top} монет", file=sys.stderr)
    elif args.symbols:
        symbols = args.symbols
    else:
        raw = get_top_by_volume(args.exchange, "USDT", 20)
        symbols = [s["symbol"] for s in raw]

    result = generate_multi_mtf_summary(symbols, args.exchange)
    print(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nСохранено в {args.output}")
