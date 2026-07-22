"""Full backtest on 4h with optimal parameters"""
from backtest import fetch_klines, run_single_backtest
from config import PAIR, EXIT_Z, POSITION_SIZE_USDT, LEVERAGE
from datetime import datetime

interval = "240"  # 4h
num_candles = 1000

print("=" * 70)
print("FULL BACKTEST: 4h with optimal parameters")
print("=" * 70)
print(f"Pair: {PAIR['long']}/{PAIR['short']}")
print(f"Parameters: ENTRY_Z=1.2, EXIT_Z={EXIT_Z}, STOP_Z=3.5")
print(f"Position: {POSITION_SIZE_USDT} USDT x {LEVERAGE}x leverage")
print(f"Candles: {num_candles} (~{num_candles * 4 / 24:.0f} days)")

print("\nFetching data...")
klines1 = fetch_klines(PAIR["long"], interval, num_candles)
klines2 = fetch_klines(PAIR["short"], interval, num_candles)

times1 = {k["time"]: k for k in klines1}
times2 = {k["time"]: k for k in klines2}
common_times = sorted(set(times1.keys()) & set(times2.keys()))

closes1 = [times1[t]["close"] for t in common_times]
closes2 = [times2[t]["close"] for t in common_times]
spreads = [closes1[i] / closes2[i] for i in range(len(closes1))]

start_date = datetime.fromtimestamp(common_times[0] // 1000).strftime("%Y-%m-%d")
end_date = datetime.fromtimestamp(common_times[-1] // 1000).strftime("%Y-%m-%d")
print(f"Aligned {len(common_times)} candles")
print(f"Period: {start_date} to {end_date}")

r = run_single_backtest(closes1, closes2, spreads, common_times, 1.2, EXIT_Z, 3.5)

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"Start Balance:      $100.00")
print(f"End Balance:        ${r['balance']:.2f}")
print(f"Total PnL:          ${r['total_pnl']:.2f} ({r['total_pnl_pct']:+.1f}%)")
print(f"Max Drawdown:       {r['max_drawdown']:.1f}%")
print(f"Total Trades:       {r['total_trades']}")
print(f"Win Rate:           {r['win_rate']:.1f}%")
print(f"Profit Factor:      {r['profit_factor']:.2f}")
if r['total_trades'] > 0:
    print(f"Avg PnL/Trade:      ${r['total_pnl'] / r['total_trades']:.2f}")
print("=" * 70)
