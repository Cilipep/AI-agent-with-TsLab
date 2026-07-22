"""
Backtest for Spread Trading Bot
Fetches historical klines from Bybit and simulates the spread strategy
"""

import time
import hmac
import hashlib
import json
import requests
from datetime import datetime
from config import (
    API_KEY, API_SECRET, BASE_URL, PAIR, LOOKBACK,
    ENTRY_Z, EXIT_Z, STOP_Z, POSITION_SIZE_USDT,
    LEVERAGE, KLINE_INTERVAL
)


def sign(params: str) -> str:
    return hmac.new(API_SECRET.encode(), params.encode(), hashlib.sha256).hexdigest()


def api_get(endpoint: str, params: dict = None) -> dict:
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    if params:
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        param_str = f"{timestamp}{API_KEY}{recv_window}{query_string}"
        url = f"{BASE_URL}{endpoint}?{query_string}"
    else:
        param_str = f"{timestamp}{API_KEY}{recv_window}"
        url = f"{BASE_URL}{endpoint}"

    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": sign(param_str),
        "X-BAPI-RECV-WINDOW": recv_window,
        "User-Agent": "bybit-skill/1.5.4"
    }

    response = requests.get(url, headers=headers, timeout=10)
    return response.json()


def fetch_klines(symbol: str, interval: str, limit: int) -> list:
    """Fetch klines in chronological order (oldest first)"""
    all_klines = []
    end_time = None

    # Bybit returns max 200 per request, paginate if needed
    remaining = limit
    while remaining > 0:
        batch = min(remaining, 200)
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": str(batch)
        }
        if end_time:
            params["end"] = str(end_time)

        result = api_get("/v5/market/kline", params)
        if result.get("retCode") != 0:
            raise Exception(f"Failed to fetch klines for {symbol}: {result}")

        klines = result["result"]["list"]
        if not klines:
            break

        # klines are in reverse chronological order
        for k in reversed(klines):
            all_klines.append({
                "time": int(k[0]),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })

        end_time = int(klines[-1][0]) - 1
        remaining -= len(klines)
        time.sleep(0.1)

    return all_klines


def calculate_z_score(spreads: list, current_idx: int) -> float:
    """Calculate z-score at a given index using lookback window"""
    start = max(0, current_idx - LOOKBACK)
    window = spreads[start:current_idx + 1]
    if len(window) < 2:
        return 0.0

    mean = sum(window) / len(window)
    std = (sum((s - mean) ** 2 for s in window) / len(window)) ** 0.5

    if std == 0:
        return 0.0

    return (window[-1] - mean) / std


def run_backtest():
    """Main backtest loop"""
    print("=" * 60)
    print("Spread Trading Bot - BACKTEST")
    print(f"Pair: {PAIR['long']}/{PAIR['short']}")
    print(f"Interval: {KLINE_INTERVAL}h, Lookback: {LOOKBACK}")
    print(f"Entry Z: {ENTRY_Z}, Exit Z: {EXIT_Z}, Stop Z: {STOP_Z}")
    print(f"Position Size: {POSITION_SIZE_USDT} USDT per leg")
    print(f"Leverage: {LEVERAGE}x")
    print("=" * 60)

    # Fetch historical data
    num_candles = 500  # ~20 days of hourly data
    print(f"\nFetching {num_candles} candles...")

    klines1 = fetch_klines(PAIR["long"], KLINE_INTERVAL, num_candles)
    klines2 = fetch_klines(PAIR["short"], KLINE_INTERVAL, num_candles)

    # Align to same timestamps
    times1 = {k["time"]: k for k in klines1}
    times2 = {k["time"]: k for k in klines2}
    common_times = sorted(set(times1.keys()) & set(times2.keys()))

    print(f"Aligned {len(common_times)} common candles")

    closes1 = [times1[t]["close"] for t in common_times]
    closes2 = [times2[t]["close"] for t in common_times]

    # Calculate spread history
    spreads = [closes1[i] / closes2[i] for i in range(len(closes1))]

    # Simulation state
    balance = 100.0  # Starting balance USDT
    initial_balance = balance
    position = None  # {"side": "long"/"short", "entry_spread": ..., "entry_idx": ...}
    trades = []
    equity_curve = [balance]

    # Metrics
    peak_balance = balance
    max_drawdown = 0.0
    winning_trades = 0
    losing_trades = 0
    total_pnl = 0.0

    print("\nRunning simulation...")

    # Start after enough lookback
    start_idx = LOOKBACK + 5

    for i in range(start_idx, len(spreads)):
        z_score = calculate_z_score(spreads, i)

        if position is None:
            # Check for entry
            if z_score > ENTRY_Z:
                position = {
                    "side": "short",  # Spread high -> short it (expect reversion)
                    "entry_spread": spreads[i],
                    "entry_idx": i,
                    "entry_z": z_score,
                    "size_usdt": POSITION_SIZE_USDT * LEVERAGE
                }
            elif z_score < -ENTRY_Z:
                position = {
                    "side": "long",  # Spread low -> long it
                    "entry_spread": spreads[i],
                    "entry_idx": i,
                    "entry_z": z_score,
                    "size_usdt": POSITION_SIZE_USDT * LEVERAGE
                }
        else:
            # Check for exit
            exit_reason = None

            if abs(z_score) < EXIT_Z:
                exit_reason = "Z-Score normalized"
            elif abs(z_score) > STOP_Z:
                exit_reason = "Stop loss"
            elif (position["side"] == "short" and z_score < -ENTRY_Z) or \
                 (position["side"] == "long" and z_score > ENTRY_Z):
                exit_reason = "Spread reversed"

            if exit_reason:
                # Calculate PnL
                current_spread = spreads[i]
                entry_spread = position["entry_spread"]

                if position["side"] == "long":
                    # Long spread: profit when spread increases
                    pnl_pct = (current_spread - entry_spread) / entry_spread
                else:
                    # Short spread: profit when spread decreases
                    pnl_pct = (entry_spread - current_spread) / entry_spread

                pnl = position["size_usdt"] * pnl_pct
                balance += pnl
                total_pnl += pnl

                trade = {
                    "entry_idx": position["entry_idx"],
                    "exit_idx": i,
                    "side": position["side"],
                    "entry_spread": entry_spread,
                    "exit_spread": current_spread,
                    "entry_z": position["entry_z"],
                    "exit_z": z_score,
                    "pnl": pnl,
                    "reason": exit_reason
                }
                trades.append(trade)

                if pnl > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1

                position = None

        # Track equity
        equity_curve.append(balance)
        peak_balance = max(peak_balance, balance)
        dd = (peak_balance - balance) / peak_balance
        max_drawdown = max(max_drawdown, dd)

    # Close any open position at end
    if position:
        current_spread = spreads[-1]
        entry_spread = position["entry_spread"]
        if position["side"] == "long":
            pnl_pct = (current_spread - entry_spread) / entry_spread
        else:
            pnl_pct = (entry_spread - current_spread) / entry_spread

        pnl = position["size_usdt"] * pnl_pct
        balance += pnl
        total_pnl += pnl

        trade = {
            "entry_idx": position["entry_idx"],
            "exit_idx": len(spreads) - 1,
            "side": position["side"],
            "entry_spread": entry_spread,
            "exit_spread": current_spread,
            "entry_z": position["entry_z"],
            "exit_z": calculate_z_score(spreads, len(spreads) - 1),
            "pnl": pnl,
            "reason": "End of data"
        }
        trades.append(trade)
        if pnl > 0:
            winning_trades += 1
        else:
            losing_trades += 1

    # Print results
    total_trades = len(trades)
    win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0

    print("\n" + "=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    print(f"Period:             {len(common_times)} candles")
    print(f"Start Balance:      ${initial_balance:.2f}")
    print(f"End Balance:        ${balance:.2f}")
    print(f"Total PnL:          ${total_pnl:.2f} ({total_pnl / initial_balance * 100:.1f}%)")
    print(f"Max Drawdown:       {max_drawdown * 100:.1f}%")
    print(f"Total Trades:       {total_trades}")
    print(f"Winning Trades:     {winning_trades}")
    print(f"Losing Trades:      {losing_trades}")
    print(f"Win Rate:           {win_rate:.1f}%")

    if total_trades > 0:
        avg_pnl = total_pnl / total_trades
        winning_pnl = sum(t["pnl"] for t in trades if t["pnl"] > 0)
        losing_pnl = sum(t["pnl"] for t in trades if t["pnl"] < 0)
        avg_win = winning_pnl / winning_trades if winning_trades > 0 else 0
        avg_loss = losing_pnl / losing_trades if losing_trades > 0 else 0
        profit_factor = abs(winning_pnl / losing_pnl) if losing_pnl != 0 else float("inf")

        print(f"\nAvg PnL/Trade:      ${avg_pnl:.2f}")
        print(f"Avg Win:            ${avg_win:.2f}")
        print(f"Avg Loss:           ${avg_loss:.2f}")
        print(f"Profit Factor:      {profit_factor:.2f}")

    print("\n" + "-" * 60)
    print("TRADE LOG")
    print("-" * 60)
    for i, t in enumerate(trades):
        entry_time = datetime.fromtimestamp(common_times[t["entry_idx"]] // 1000).strftime("%m-%d %H:%M")
        exit_time = datetime.fromtimestamp(common_times[t["exit_idx"]] // 1000).strftime("%m-%d %H:%M")
        print(f"#{i+1:3d} | {t['side']:5s} | {entry_time} -> {exit_time} | "
              f"Z: {t['entry_z']:+.2f} -> {t['exit_z']:+.2f} | "
              f"PnL: ${t['pnl']:+.2f} | {t['reason']}")

    print("=" * 60)

    return {
        "balance": balance,
        "total_pnl": total_pnl,
        "max_drawdown": max_drawdown,
        "total_trades": total_trades,
        "win_rate": win_rate,
        "trades": trades,
        "equity_curve": equity_curve
    }


def run_single_backtest(closes1, closes2, spreads, common_times,
                        entry_z, exit_z, stop_z):
    """Run one backtest with given parameters, return metrics"""
    balance = 100.0
    initial_balance = balance
    position = None
    trades = []
    peak_balance = balance
    max_drawdown = 0.0
    winning_trades = 0
    losing_trades = 0
    total_pnl = 0.0

    start_idx = LOOKBACK + 5

    for i in range(start_idx, len(spreads)):
        z_score = calculate_z_score(spreads, i)

        if position is None:
            if z_score > entry_z:
                position = {
                    "side": "short",
                    "entry_spread": spreads[i],
                    "entry_idx": i,
                    "entry_z": z_score,
                    "size_usdt": POSITION_SIZE_USDT * LEVERAGE
                }
            elif z_score < -entry_z:
                position = {
                    "side": "long",
                    "entry_spread": spreads[i],
                    "entry_idx": i,
                    "entry_z": z_score,
                    "size_usdt": POSITION_SIZE_USDT * LEVERAGE
                }
        else:
            exit_reason = None
            if abs(z_score) < exit_z:
                exit_reason = "Z-Score normalized"
            elif abs(z_score) > stop_z:
                exit_reason = "Stop loss"
            elif (position["side"] == "short" and z_score < -entry_z) or \
                 (position["side"] == "long" and z_score > entry_z):
                exit_reason = "Spread reversed"

            if exit_reason:
                current_spread = spreads[i]
                entry_spread = position["entry_spread"]
                if position["side"] == "long":
                    pnl_pct = (current_spread - entry_spread) / entry_spread
                else:
                    pnl_pct = (entry_spread - current_spread) / entry_spread

                pnl = position["size_usdt"] * pnl_pct
                balance += pnl
                total_pnl += pnl

                trades.append({"pnl": pnl, "reason": exit_reason})
                if pnl > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
                position = None

        peak_balance = max(peak_balance, balance)
        dd = (peak_balance - balance) / peak_balance
        max_drawdown = max(max_drawdown, dd)

    # Close open position at end
    if position:
        current_spread = spreads[-1]
        entry_spread = position["entry_spread"]
        if position["side"] == "long":
            pnl_pct = (current_spread - entry_spread) / entry_spread
        else:
            pnl_pct = (entry_spread - current_spread) / entry_spread
        pnl = position["size_usdt"] * pnl_pct
        balance += pnl
        total_pnl += pnl
        trades.append({"pnl": pnl, "reason": "End of data"})
        if pnl > 0:
            winning_trades += 1
        else:
            losing_trades += 1

    total_trades = len(trades)
    win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
    winning_pnl = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    losing_pnl = sum(t["pnl"] for t in trades if t["pnl"] < 0)
    profit_factor = abs(winning_pnl / losing_pnl) if losing_pnl != 0 else 99.0

    # Score: reward profit factor and return, penalize few trades
    trade_penalty = 1.0 if total_trades >= 5 else total_trades / 5
    score = (total_pnl / initial_balance) * profit_factor * trade_penalty

    return {
        "entry_z": entry_z, "exit_z": exit_z, "stop_z": stop_z,
        "balance": balance, "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl / initial_balance * 100,
        "max_drawdown": max_drawdown * 100,
        "total_trades": total_trades, "win_rate": win_rate,
        "profit_factor": profit_factor, "score": score
    }


def optimize(interval=None, num_candles=None):
    """Grid search over ENTRY_Z and STOP_Z"""
    interval = interval or KLINE_INTERVAL
    num_candles = num_candles or (1000 if interval in ("1", "5") else 500)

    tf_label = {"1": "1m", "5": "5m", "15": "15m", "60": "1h", "240": "4h", "D": "1D"}.get(interval, interval)
    print("=" * 70)
    print(f"PARAMETER OPTIMIZATION: ENTRY_Z x STOP_Z  [{tf_label}]")
    print("=" * 70)

    print(f"\nFetching {num_candles} candles ({tf_label})...")
    klines1 = fetch_klines(PAIR["long"], interval, num_candles)
    klines2 = fetch_klines(PAIR["short"], interval, num_candles)

    times1 = {k["time"]: k for k in klines1}
    times2 = {k["time"]: k for k in klines2}
    common_times = sorted(set(times1.keys()) & set(times2.keys()))

    closes1 = [times1[t]["close"] for t in common_times]
    closes2 = [times2[t]["close"] for t in common_times]
    spreads = [closes1[i] / closes2[i] for i in range(len(closes1))]

    print(f"Aligned {len(common_times)} candles\n")

    # Finer grid for 1m, standard for others
    if interval == "1":
        entry_z_range = [0.5, 0.7, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0]
        stop_z_range = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]
    elif interval == "5":
        entry_z_range = [0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5]
        stop_z_range = [2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
    else:
        entry_z_range = [1.0, 1.2, 1.5, 1.8, 2.0, 2.5]
        stop_z_range = [2.5, 3.0, 3.5, 4.0, 5.0]

    results = []
    total_combos = len(entry_z_range) * len(stop_z_range)
    print(f"Testing {total_combos} combinations (EXIT_Z={EXIT_Z})...\n")
    print(f"{'ENTRY_Z':>8} {'STOP_Z':>8} {'PnL%':>8} {'Trades':>7} {'WinRate':>8} {'MaxDD':>7} {'PF':>6} {'Score':>8}")
    print("-" * 70)

    count = 0
    for entry_z in entry_z_range:
        for stop_z in stop_z_range:
            if stop_z <= entry_z:
                continue
            count += 1

            result = run_single_backtest(
                closes1, closes2, spreads, common_times,
                entry_z, EXIT_Z, stop_z
            )
            results.append(result)

            marker = " <--" if result["total_pnl"] > 0 else ""
            print(f"{entry_z:>8.1f} {stop_z:>8.1f} "
                  f"{result['total_pnl_pct']:>+7.1f}% "
                  f"{result['total_trades']:>7} "
                  f"{result['win_rate']:>7.1f}% "
                  f"{result['max_drawdown']:>6.1f}% "
                  f"{result['profit_factor']:>6.2f} "
                  f"{result['score']:>+7.3f}{marker}")

    print(f"\nTested {count} valid combinations")

    results.sort(key=lambda x: x["score"], reverse=True)

    print("\n" + "=" * 70)
    print("TOP 5 PARAMETER SETS (by score)")
    print("=" * 70)
    print(f"{'Rank':>4} {'ENTRY_Z':>8} {'STOP_Z':>8} {'PnL%':>8} {'Trades':>7} {'WinRate':>8} {'MaxDD':>7} {'PF':>6}")
    print("-" * 70)

    for i, r in enumerate(results[:5]):
        print(f"#{i+1:>3} {r['entry_z']:>8.1f} {r['stop_z']:>8.1f} "
              f"{r['total_pnl_pct']:>+7.1f}% "
              f"{r['total_trades']:>7} "
              f"{r['win_rate']:>7.1f}% "
              f"{r['max_drawdown']:>6.1f}% "
              f"{r['profit_factor']:>6.2f}")

    best = results[0]
    print(f"\nBest: ENTRY_Z={best['entry_z']}, STOP_Z={best['stop_z']}")
    print(f"  PnL: {best['total_pnl_pct']:+.1f}% | "
          f"Trades: {best['total_trades']} | "
          f"Win Rate: {best['win_rate']:.1f}% | "
          f"Max DD: {best['max_drawdown']:.1f}% | "
          f"PF: {best['profit_factor']:.2f}")

    print(f"\nSuggested config.py update:")
    print(f"  ENTRY_Z = {best['entry_z']}")
    print(f"  EXIT_Z  = {EXIT_Z}")
    print(f"  STOP_Z  = {best['stop_z']}")

    return results


def test_timeframes():
    """Test the best parameters across multiple timeframes"""
    print("=" * 70)
    print("MULTI-TIMEFRAME TEST")
    print("=" * 70)

    # Best params from optimization
    entry_z = 2.5
    exit_z = 0.5
    stop_z = 5.0

    # Timeframes to test: (interval, label, num_candles)
    timeframes = [
        ("1",   "1m",   1000),
        ("5",   "5m",   1000),
        ("15",  "15m",  1000),
        ("60",  "1h",   500),
        ("240", "4h",   300),
        ("D",   "1D",   200),
    ]

    print(f"\nParameters: ENTRY_Z={entry_z}, EXIT_Z={exit_z}, STOP_Z={stop_z}")
    print(f"Position: {POSITION_SIZE_USDT} USDT x {LEVERAGE}x leverage\n")

    results = []

    for interval, label, num_candles in timeframes:
        print(f"Testing {label} ({interval})...", end=" ", flush=True)
        try:
            klines1 = fetch_klines(PAIR["long"], interval, num_candles)
            klines2 = fetch_klines(PAIR["short"], interval, num_candles)

            times1 = {k["time"]: k for k in klines1}
            times2 = {k["time"]: k for k in klines2}
            common_times = sorted(set(times1.keys()) & set(times2.keys()))

            if len(common_times) < LOOKBACK + 20:
                print(f"SKIP (only {len(common_times)} candles)")
                continue

            closes1 = [times1[t]["close"] for t in common_times]
            closes2 = [times2[t]["close"] for t in common_times]
            spreads = [closes1[i] / closes2[i] for i in range(len(closes1))]

            r = run_single_backtest(closes1, closes2, spreads, common_times,
                                    entry_z, exit_z, stop_z)
            r["interval"] = interval
            r["label"] = label
            r["candles"] = len(common_times)
            results.append(r)

            status = "+" if r["total_pnl"] > 0 else "-"
            print(f"{r['total_pnl_pct']:>+6.1f}% | "
                  f"{r['total_trades']:>3} trades | "
                  f"WR {r['win_rate']:>5.1f}% | "
                  f"DD {r['max_drawdown']:>5.1f}% | "
                  f"PF {r['profit_factor']:>5.2f}")
        except Exception as e:
            print(f"ERROR: {e}")

    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'TF':>5} {'Candles':>8} {'PnL%':>8} {'Trades':>7} {'WinRate':>8} {'MaxDD':>7} {'PF':>6}")
    print("-" * 70)

    for r in sorted(results, key=lambda x: x["total_pnl_pct"], reverse=True):
        marker = "+" if r["total_pnl"] > 0 else ""
        print(f"{r['label']:>5} {r['candles']:>8} "
              f"{r['total_pnl_pct']:>+7.1f}% "
              f"{r['total_trades']:>7} "
              f"{r['win_rate']:>7.1f}% "
              f"{r['max_drawdown']:>6.1f}% "
              f"{r['profit_factor']:>6.2f}")

    profitable = [r for r in results if r["total_pnl"] > 0]
    print(f"\nProfitable timeframes: {len(profitable)}/{len(results)}")

    if profitable:
        best_tf = max(profitable, key=lambda x: x["total_pnl_pct"])
        print(f"Best: {best_tf['label']} ({best_tf['total_pnl_pct']:+.1f}%, "
              f"PF {best_tf['profit_factor']:.2f})")

    return results


def test_instruments():
    """Test the strategy on different instrument pairs"""
    print("=" * 70)
    print("MULTI-INSTRUMENT TEST")
    print("=" * 70)

    # Best params from optimization
    entry_z = 1.2
    exit_z = 0.5
    stop_z = 3.5
    interval = "240"  # 4h
    num_candles = 1000

    # Pairs to test: (long, short)
    pairs = [
        ("BTCUSDT", "ETHUSDT"),   # Original
        ("ETHUSDT", "BTCUSDT"),   # Reversed
        ("BTCUSDT", "SOLUSDT"),   # BTC vs SOL
        ("ETHUSDT", "SOLUSDT"),   # ETH vs SOL
        ("SOLUSDT", "BTCUSDT"),   # SOL vs BTC
        ("SOLUSDT", "ETHUSDT"),   # SOL vs ETH
        ("BTCUSDT", "DOGEUSDT"),  # BTC vs DOGE
        ("ETHUSDT", "DOGEUSDT"),  # ETH vs DOGE
        ("DOGEUSDT", "BTCUSDT"),  # DOGE vs BTC
        ("DOGEUSDT", "ETHUSDT"),  # DOGE vs ETH
    ]

    print(f"\nParameters: ENTRY_Z={entry_z}, EXIT_Z={exit_z}, STOP_Z={stop_z}")
    print(f"Interval: 4h, Candles: {num_candles}\n")

    results = []

    for long_sym, short_sym in pairs:
        pair_label = f"{long_sym}/{short_sym}"
        print(f"Testing {pair_label}...", end=" ", flush=True)
        try:
            klines1 = fetch_klines(long_sym, interval, num_candles)
            klines2 = fetch_klines(short_sym, interval, num_candles)

            times1 = {k["time"]: k for k in klines1}
            times2 = {k["time"]: k for k in klines2}
            common_times = sorted(set(times1.keys()) & set(times2.keys()))

            if len(common_times) < LOOKBACK + 20:
                print(f"SKIP (only {len(common_times)} candles)")
                continue

            closes1 = [times1[t]["close"] for t in common_times]
            closes2 = [times2[t]["close"] for t in common_times]
            spreads = [closes1[i] / closes2[i] for i in range(len(closes1))]

            r = run_single_backtest(closes1, closes2, spreads, common_times,
                                    entry_z, exit_z, stop_z)
            r["pair"] = pair_label
            r["candles"] = len(common_times)
            results.append(r)

            print(f"{r['total_pnl_pct']:>+6.1f}% | "
                  f"{r['total_trades']:>3} trades | "
                  f"WR {r['win_rate']:>5.1f}% | "
                  f"DD {r['max_drawdown']:>5.1f}% | "
                  f"PF {r['profit_factor']:>5.2f}")
        except Exception as e:
            print(f"ERROR: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Pair':<20} {'PnL%':>8} {'Trades':>7} {'WinRate':>8} {'MaxDD':>7} {'PF':>6}")
    print("-" * 70)

    for r in sorted(results, key=lambda x: x["total_pnl_pct"], reverse=True):
        marker = "+" if r["total_pnl"] > 0 else ""
        print(f"{r['pair']:<20} {r['total_pnl_pct']:>+7.1f}% "
              f"{r['total_trades']:>7} "
              f"{r['win_rate']:>7.1f}% "
              f"{r['max_drawdown']:>6.1f}% "
              f"{r['profit_factor']:>6.2f}")

    profitable = [r for r in results if r["total_pnl"] > 0]
    print(f"\nProfitable pairs: {len(profitable)}/{len(results)}")

    if profitable:
        best = max(profitable, key=lambda x: x["total_pnl_pct"])
        print(f"Best: {best['pair']} ({best['total_pnl_pct']:+.1f}%, PF {best['profit_factor']:.2f})")

    return results


if __name__ == "__main__":
    import sys

    tf_map = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "4h": "240", "1d": "D"}

    if len(sys.argv) > 1 and sys.argv[1] == "--optimize":
        interval = None
        candles = None
        if "--tf" in sys.argv:
            idx = sys.argv.index("--tf")
            if idx + 1 < len(sys.argv):
                tf_raw = sys.argv[idx + 1].lower()
                interval = tf_map.get(tf_raw, tf_raw)
        if "--candles" in sys.argv:
            idx = sys.argv.index("--candles")
            if idx + 1 < len(sys.argv):
                candles = int(sys.argv[idx + 1])
        optimize(interval=interval, num_candles=candles)
    elif len(sys.argv) > 1 and sys.argv[1] == "--timeframes":
        test_timeframes()
    elif len(sys.argv) > 1 and sys.argv[1] == "--instruments":
        test_instruments()
    else:
        result = run_backtest()
