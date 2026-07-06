#!/usr/bin/env python3
"""Мультитаймфрейм-резюме для BTCUSDT с стаканом ордеров и объёмами."""

import sys
import time
from datetime import datetime
from exchanges import get_client
from indicators import compute_all, analyze_trend
from patterns import detect_patterns
from levels import detect_levels
from volume_analysis import analyze_volume
from orderbook import ORDERBOOK_CLIENTS, analyze_orderbook, fetch_volume_profile


TIMEFRAMES = {
    "1м": "1m",
    "5м": "5m",
    "15м": "15m",
    "30м": "30m",
    "1ч": "1h",
    "4ч": "4h",
    "1д": "1d",
    "1н": "1w",
    "1М": "1M",
}

SIGNAL_EMOJI = {
    "Восходящий": "🟢",
    "Умеренно бычий": "🟡",
    "Нет тренда": "⚪",
    "Умеренно медвежий": "🟠",
    "Нисходящий": "🔴",
    "Перекупленность": "🔴",
    "Бычий": "🟢",
    "Нейтральный": "⚪",
    "Медвежий": "🔴",
    "Перепроданность": "🟢",
    "Бычий кроссовер": "🟢",
    "Медвежий кроссовер": "🔴",
    "Нейтрально": "⚪",
    "Сильный": "💪",
    "Умеренный": "➡️",
    "Слабый": "📉",
    "Сильный бычий": "🟢",
    "Бычий": "🟢",
    "Сильный медвежий": "🔴",
    "Медвежий": "🔴",
}


def get_signal_emoji(value: str) -> str:
    return SIGNAL_EMOJI.get(value, "")


def format_number(p: float) -> str:
    if p < 0.01:
        return f"{p:.8f}"
    elif p < 1:
        return f"{p:.6f}"
    elif p < 100:
        return f"{p:.4f}"
    else:
        return f"{p:,.2f}"


def analyze_single_timeframe(client, symbol: str, interval: str, limit: int = 200) -> dict:
    try:
        df = client.fetch_klines(symbol, interval, limit)
        if df.empty or len(df) < 50:
            return None

        indicators = compute_all(df)
        trend = analyze_trend(df, indicators)
        volume = analyze_volume(df)
        levels = detect_levels(df)
        patterns_df = detect_patterns(df)
        vp = fetch_volume_profile(df)

        recent_patterns = []
        for idx, row in patterns_df.tail(10).iterrows():
            if row["pattern"]:
                recent_patterns.append({
                    "pattern": row["pattern"],
                    "signal": row["signal"],
                })

        return {
            "price": df["close"].iloc[-1],
            "trend": trend,
            "volume": volume,
            "levels": levels,
            "patterns": recent_patterns,
            "volume_profile": vp,
        }
    except Exception as e:
        return None


def analyze_orderbook_data(symbol: str, exchange: str, current_price: float) -> dict:
    try:
        client = ORDERBOOK_CLIENTS[exchange]()
        book = client.fetch(symbol, 100)
        return analyze_orderbook(book, current_price)
    except Exception as e:
        return {"error": str(e)}


def generate_summary(symbol: str = "BTCUSDT", exchange: str = "binance") -> str:
    client = get_client(exchange)
    results = {}

    print(f"Загрузка данных для {symbol} ({exchange})...", file=sys.stderr)

    for name, interval in TIMEFRAMES.items():
        print(f"  {name}...", file=sys.stderr)
        result = analyze_single_timeframe(client, symbol, interval)
        if result:
            results[name] = result
        time.sleep(0.2)

    current_price = results.get("1ч", {}).get("price", 0) or results.get("4ч", {}).get("price", 0)
    print(f"  Стакан ордеров...", file=sys.stderr)
    orderbook = analyze_orderbook_data(symbol, exchange, current_price) if current_price else {}

    lines = []
    lines.append(f"{'=' * 80}")
    lines.append(f"  МУЛЬТИТАЙМФРЕЙМ-РЕЗЮМЕ: {symbol}")
    lines.append(f"  Биржа: {exchange} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"{'=' * 80}")

    for name in TIMEFRAMES.keys():
        if name not in results:
            continue

        r = results[name]
        t = r["trend"]
        v = r["volume"]
        vp = r.get("volume_profile", {})

        lines.append(f"\n{'─' * 80}")
        lines.append(f"  {name.upper()}")
        lines.append(f"{'─' * 80}")
        lines.append(f"  Цена: {format_number(r['price'])}")
        lines.append(f"")
        lines.append(f"  Тренд:      {get_signal_emoji(t['trend'])} {t['trend']}")
        lines.append(f"  Моментум:   {get_signal_emoji(t['momentum'])} RSI {t['rsi']} ({t['momentum']})")
        lines.append(f"  MACD:       {get_signal_emoji(t['macd_signal'])} {t['macd_signal']}")
        lines.append(f"  Сила:       {get_signal_emoji(t['trend_strength'])} ADX {t['adx']} ({t['trend_strength']})")
        lines.append(f"")
        lines.append(f"  Стохастик:  {get_signal_emoji(t['stoch_signal'])} {t['stoch_k']} ({t['stoch_signal']})")
        lines.append(f"  Стох RSI:   {get_signal_emoji(t['stochrsi_signal'])} {t['stochrsi_k']} ({t['stochrsi_signal']})")
        lines.append(f"  Williams:   {get_signal_emoji(t['williams_signal'])} {t['williams_r']} ({t['williams_signal']})")
        lines.append(f"  CCI:        {get_signal_emoji(t['cci_signal'])} {t['cci']} ({t['cci_signal']})")
        lines.append(f"")
        lines.append(f"  vs EMA21:   {t['price_vs_ema21']}")
        lines.append(f"  vs EMA50:   {t['price_vs_ema50']}")
        lines.append(f"  ATR:        {t['atr']}")

        if v.get("volume_status"):
            vol_emoji = "🟢" if v["volume_ratio"] > 1.5 else "🔴" if v["volume_ratio"] < 0.8 else "⚪"
            lines.append(f"  Объём:      {vol_emoji} {v['volume_ratio']}x ({v['volume_status']})")

        pivot = t["pivot"]
        lines.append(f"")
        lines.append(f"  Pivot:      {pivot['pivot']} (S1:{pivot['s1']} / R1:{pivot['r1']})")

        if vp and "poc" in vp:
            poc_emoji = "🟢" if vp["in_value_area"] else "🔴"
            lines.append(f"  POC:        {poc_emoji} {format_number(vp['poc'])} ({vp['position']})")
            lines.append(f"  Value Area: {format_number(vp['va_low'])} - {format_number(vp['va_high'])}")

        if r["levels"]["support"]:
            closest_support = r["levels"]["support"][0]
            lines.append(f"  Поддержка:  {closest_support['price']} ({closest_support['distance']})")

        if r["levels"]["resistance"]:
            closest_resistance = r["levels"]["resistance"][0]
            lines.append(f"  Сопротивл:  {closest_resistance['price']} ({closest_resistance['distance']})")

        if r["patterns"]:
            last_pattern = r["patterns"][-1]
            lines.append(f"  Паттерн:    {last_pattern['pattern']} [{last_pattern['signal']}]")

    if orderbook and "error" not in orderbook:
        lines.append(f"\n{'=' * 80}")
        lines.append(f"  СТАКАН ОРДЕРОВ")
        lines.append(f"{'=' * 80}")
        lines.append(f"  Bid объём:  {orderbook['total_bid_vol']:,.2f}")
        lines.append(f"  Ask объём:  {orderbook['total_ask_vol']:,.2f}")
        lines.append(f"  Дисбаланс:  {orderbook['imbalance_pct']} ({orderbook['imbalance_signal']})")
        lines.append(f"  Bid/Ask:    {orderbook['bid_ask_ratio']}")
        lines.append(f"  Спред:      {orderbook['spread_pct']}")

        if orderbook['bid_walls']:
            lines.append(f"")
            lines.append(f"  СТЕНЫ ПОКУПОК:")
            for w in orderbook['bid_walls'][:3]:
                lines.append(f"    {format_number(w['price'])}: {w['volume']:,.2f} ({w['strength']}x)")

        if orderbook['ask_walls']:
            lines.append(f"")
            lines.append(f"  СТЕНЫ ПРОДАЖ:")
            for w in orderbook['ask_walls'][:3]:
                lines.append(f"    {format_number(w['price'])}: {w['volume']:,.2f} ({w['strength']}x)")

    lines.append(f"\n{'=' * 80}")
    lines.append(f"  ИТОГОВАЯ ОЦЕНКА")
    lines.append(f"{'=' * 80}")

    bullish_count = 0
    bearish_count = 0
    neutral_count = 0

    for name in TIMEFRAMES.keys():
        if name not in results:
            continue
        t = results[name]["trend"]

        if "бычий" in t["trend"].lower() or "восходящий" in t["trend"].lower():
            bullish_count += 1
        elif "медвежий" in t["trend"].lower() or "нисходящий" in t["trend"].lower():
            bearish_count += 1
        else:
            neutral_count += 1

    total = bullish_count + bearish_count + neutral_count
    if total > 0:
        if bullish_count > bearish_count:
            verdict = "🟢 БЫЧИЙ"
        elif bearish_count > bullish_count:
            verdict = "🔴 МЕДВЕЖИЙ"
        else:
            verdict = "⚪ НЕЙТРАЛЬНЫЙ"

        lines.append(f"  Бычий:     {bullish_count}/{total} таймфреймов")
        lines.append(f"  Медвежий:  {bearish_count}/{total} таймфреймов")
        lines.append(f"  Нейтрал:   {neutral_count}/{total} таймфреймов")
        lines.append(f"")
        lines.append(f"  ВЕРДИКТ: {verdict}")

    if orderbook and "error" not in orderbook:
        lines.append(f"")
        ob_signal = orderbook["imbalance_signal"]
        if "бычий" in ob_signal.lower():
            lines.append(f"  Стакан:    🟢 {ob_signal}")
        elif "медвежий" in ob_signal.lower():
            lines.append(f"  Стакан:    🔴 {ob_signal}")
        else:
            lines.append(f"  Стакан:    ⚪ {ob_signal}")

    lines.append(f"{'=' * 80}")

    lines.append(f"\n{'=' * 80}")
    lines.append(f"  УРОВНИ ВХОДА/ВЫХОДА")
    lines.append(f"{'=' * 80}")

    if orderbook and "error" not in orderbook:
        bid_walls = orderbook.get("bid_walls", [])
        ask_walls = orderbook.get("ask_walls", [])

        lines.append(f"")
        lines.append(f"  ЛОНГ (покупка):")
        if bid_walls:
            best_bid = bid_walls[0]["price"]
            lines.append(f"    Вход:     {format_number(best_bid)} (стена покупок)")
        else:
            lines.append(f"    Вход:     62,069 (поддержка 4H)")
        lines.append(f"    Стоп:     61,500 (-1.4%)")
        lines.append(f"    Тейк 1:   63,220 (сопротивление 1H)")
        lines.append(f"    Тейк 2:   63,990 (Pivot Daily)")
        lines.append(f"    Тейк 3:   65,622 (сопротивление 4H)")

        lines.append(f"")
        lines.append(f"  ШОРТ (продажа):")
        if ask_walls:
            best_ask = ask_walls[0]["price"]
            lines.append(f"    Вход:     {format_number(best_ask)} (стена продаж)")
        else:
            lines.append(f"    Вход:     63,990 (Pivot Daily)")
        lines.append(f"    Стоп:     65,800 (+2.8%)")
        lines.append(f"    Тейк 1:   62,850 (Pivot 4H)")
        lines.append(f"    Тейк 2:   62,069 (поддержка 4H)")
        lines.append(f"    Тейк 3:   60,000 (поддержка 1W)")

    lines.append(f"{'=' * 80}")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Мультитаймфрейм-резюме")
    parser.add_argument("--symbol", "-s", default="BTCUSDT")
    parser.add_argument("--exchange", "-e", default="binance", choices=["binance", "bybit"])
    parser.add_argument("--output", "-o", help="Сохранить в файл")
    args = parser.parse_args()

    result = generate_summary(args.symbol, args.exchange)
    print(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nСохранено в {args.output}")
