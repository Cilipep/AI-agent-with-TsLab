import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ============================================================
# SkSred v4 — XLMUSD_PERP Backtest
# Оптимизированные параметры для XLM
# ============================================================

SMA_SHORT = 5       # Оптимизировано для XLM
SMA_LONG = 15       # Оптимизировано для XLM
EMA_TREND = 200     # Фильтр тренда
ATR_PERIOD = 14     # Период ATR
ATR_SL_MULT = 1.5   # SL = 1.5 × ATR
ATR_TP_MULT = 3.0   # TP = 3.0 × ATR
TRAIL_ACTIVATE_PCT = 0.02   # Активация trailing при +2%
TRAIL_DISTANCE_PCT = 0.015  # Трейл 1.5% от пика
COMMISSION_PCT = 0.05 / 100 # Комиссия 0.05%

# Параметры торговли
INITIAL_CAPITAL = 50  # Начальный капитал USDT
LEVERAGE = 5          # Кредитное плечо


def calculate_ema(series, period):
    """Экспоненциальная скользящая средняя"""
    return series.ewm(span=period, adjust=False).mean()


def calculate_atr(df, period=14):
    """Average True Range — волатильность"""
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def run_backtest(df):
    """Основной цикл бэктеста"""
    df = df.sort_values('timestamp').reset_index(drop=True)
    df['sma_short'] = df['close'].rolling(window=SMA_SHORT).mean()
    df['sma_long'] = df['close'].rolling(window=SMA_LONG).mean()
    df['atr'] = calculate_atr(df, ATR_PERIOD)
    available_bars = len(df)
    ema_period = EMA_TREND if available_bars >= EMA_TREND else min(20, available_bars // 2)
    df['ema_trend'] = calculate_ema(df['close'], ema_period)
    df = df.dropna(subset=['sma_short', 'sma_long', 'ema_trend', 'atr']).reset_index(drop=True)

    capital = INITIAL_CAPITAL
    position = 0
    entry_price = 0
    entry_time = None
    trail_activated = False
    trail_high = 0
    trail_low = float('inf')
    trades = []
    equity_curve = [{'timestamp': df.iloc[0]['timestamp'], 'equity': capital, 'price': df.iloc[0]['close']}]

    for i in range(1, len(df)):
        ts = df.iloc[i]['timestamp']
        current_price = df.iloc[i]['close']
        high_price = df.iloc[i]['high']
        low_price = df.iloc[i]['low']
        sma1_t = df.iloc[i]['sma_short']
        sma2_t = df.iloc[i]['sma_long']
        sma1_y = df.iloc[i-1]['sma_short']
        sma2_y = df.iloc[i-1]['sma_long']
        ema_trend = df.iloc[i]['ema_trend']
        atr = df.iloc[i]['atr']
        golden_cross = (sma1_t > sma2_t) and (sma1_y <= sma2_y)
        death_cross = (sma1_t < sma2_t) and (sma1_y >= sma2_y)
        sl_distance = atr * ATR_SL_MULT
        tp_distance = atr * ATR_TP_MULT

        # === LONG ===
        if position == 1:
            sl_price = entry_price - sl_distance
            tp_price = entry_price + tp_distance
            if low_price <= sl_price:
                exit_price = sl_price
                pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
                net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
                profit_usd = capital * net_pnl_pct
                capital += profit_usd
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'direction': 'LONG', 'exit_type': 'SL',
                              'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                              'profit_usd': profit_usd, 'capital_after': capital})
                position = 0
                trail_activated = False
            elif high_price >= tp_price:
                exit_price = tp_price
                pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
                net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
                profit_usd = capital * net_pnl_pct
                capital += profit_usd
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'direction': 'LONG', 'exit_type': 'TP',
                              'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                              'profit_usd': profit_usd, 'capital_after': capital})
                position = 0
                trail_activated = False
            elif trail_activated:
                if low_price <= trail_high * (1 - TRAIL_DISTANCE_PCT):
                    exit_price = trail_high * (1 - TRAIL_DISTANCE_PCT)
                    pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
                    net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
                    profit_usd = capital * net_pnl_pct
                    capital += profit_usd
                    trades.append({'entry_time': entry_time, 'exit_time': ts, 'direction': 'LONG', 'exit_type': 'TRAIL',
                                  'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                                  'profit_usd': profit_usd, 'capital_after': capital})
                    position = 0
                    trail_activated = False

        # === SHORT ===
        elif position == -1:
            sl_price = entry_price + sl_distance
            tp_price = entry_price - tp_distance
            if high_price >= sl_price:
                exit_price = sl_price
                pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
                net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
                profit_usd = capital * net_pnl_pct
                capital += profit_usd
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'direction': 'SHORT', 'exit_type': 'SL',
                              'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                              'profit_usd': profit_usd, 'capital_after': capital})
                position = 0
                trail_activated = False
            elif low_price <= tp_price:
                exit_price = tp_price
                pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
                net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
                profit_usd = capital * net_pnl_pct
                capital += profit_usd
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'direction': 'SHORT', 'exit_type': 'TP',
                              'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                              'profit_usd': profit_usd, 'capital_after': capital})
                position = 0
                trail_activated = False
            elif trail_activated:
                if high_price >= trail_low * (1 + TRAIL_DISTANCE_PCT):
                    exit_price = trail_low * (1 + TRAIL_DISTANCE_PCT)
                    pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
                    net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
                    profit_usd = capital * net_pnl_pct
                    capital += profit_usd
                    trades.append({'entry_time': entry_time, 'exit_time': ts, 'direction': 'SHORT', 'exit_type': 'TRAIL',
                                  'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                                  'profit_usd': profit_usd, 'capital_after': capital})
                    position = 0
                    trail_activated = False

        # === Trailing Stop Update ===
        if position == 1:
            if not trail_activated:
                if (high_price - entry_price) / entry_price >= TRAIL_ACTIVATE_PCT:
                    trail_activated = True
                    trail_high = high_price
            else:
                trail_high = max(trail_high, high_price)
        elif position == -1:
            if not trail_activated:
                if (entry_price - low_price) / entry_price >= TRAIL_ACTIVATE_PCT:
                    trail_activated = True
                    trail_low = low_price
            else:
                trail_low = min(trail_low, low_price)

        # === Signal Exits ===
        if position == 1 and death_cross:
            exit_price = current_price
            pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
            net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
            profit_usd = capital * net_pnl_pct
            capital += profit_usd
            trades.append({'entry_time': entry_time, 'exit_time': ts, 'direction': 'LONG', 'exit_type': 'SIGNAL',
                          'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                          'profit_usd': profit_usd, 'capital_after': capital})
            position = 0
            trail_activated = False
        elif position == -1 and golden_cross:
            exit_price = current_price
            pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
            net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
            profit_usd = capital * net_pnl_pct
            capital += profit_usd
            trades.append({'entry_time': entry_time, 'exit_time': ts, 'direction': 'SHORT', 'exit_type': 'SIGNAL',
                          'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                          'profit_usd': profit_usd, 'capital_after': capital})
            position = 0
            trail_activated = False

        # === Entries ===
        if position == 0 and capital > 0:
            if golden_cross and current_price > ema_trend:
                position = 1
                entry_price = current_price
                entry_time = ts
                trail_activated = False
                trail_high = current_price
            elif death_cross and current_price < ema_trend:
                position = -1
                entry_price = current_price
                entry_time = ts
                trail_activated = False
                trail_low = current_price

        equity_curve.append({'timestamp': ts, 'equity': capital, 'price': current_price})
        if capital <= 0:
            break

    # Close open position
    if position != 0 and capital > 0:
        exit_price = df.iloc[-1]['close']
        pnl_pct = ((exit_price - entry_price) / entry_price * LEVERAGE) if position == 1 else ((entry_price - exit_price) / entry_price * LEVERAGE)
        net_pnl_pct = pnl_pct - COMMISSION_PCT * 2 * LEVERAGE
        profit_usd = capital * net_pnl_pct
        capital += profit_usd
        trades.append({'entry_time': entry_time, 'exit_time': df.iloc[-1]['timestamp'],
                      'direction': 'LONG' if position == 1 else 'SHORT', 'exit_type': 'EOD',
                      'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': net_pnl_pct * 100,
                      'profit_usd': profit_usd, 'capital_after': capital})

    return trades, equity_curve


def plot_results(trades, equity_curve, symbol):
    """Построение графика equity curve"""
    dates = [d['timestamp'] for d in equity_curve]
    equities = [d['equity'] for d in equity_curve]
    prices = [d['price'] for d in equity_curve]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[3, 1], sharex=True)
    fig.suptitle(f'SkSred v4 — {symbol} H4 | {INITIAL_CAPITAL} USDT × {LEVERAGE}x\n'
                 f'SMA({SMA_SHORT}/{SMA_LONG}) | EMA{EMA_TREND} | ATR SL:{ATR_SL_MULT}x TP:{ATR_TP_MULT}x',
                 fontsize=13, fontweight='bold')

    # Equity curve
    ax1.fill_between(dates, INITIAL_CAPITAL, equities, where=[e >= INITIAL_CAPITAL for e in equities],
                     alpha=0.3, color='#2ecc71', interpolate=True)
    ax1.fill_between(dates, INITIAL_CAPITAL, equities, where=[e < INITIAL_CAPITAL for e in equities],
                     alpha=0.3, color='#e74c3c', interpolate=True)
    ax1.plot(dates, equities, color='#2c3e50', linewidth=2, label='Equity')
    ax1.axhline(y=INITIAL_CAPITAL, color='gray', linestyle='--', alpha=0.5)

    # Mark trades
    for t in trades:
        if t['direction'] == 'LONG':
            marker, color = '^', '#27ae60'
        else:
            marker, color = 'v', '#c0392b'

        idx = next((j for j, d in enumerate(equity_curve) if d['timestamp'] == t['entry_time']), None)
        if idx is not None:
            ax1.scatter(t['entry_time'], equities[idx], color=color, marker=marker, s=80, zorder=5)

        idx = next((j for j, d in enumerate(equity_curve) if d['timestamp'] == t['exit_time']), None)
        if idx is not None:
            exit_color = '#27ae60' if t['pnl_pct'] > 0 else '#c0392b'
            ax1.scatter(t['exit_time'], equities[idx], color=exit_color, marker='x', s=60, zorder=5)

    # Stats
    total_return = ((equities[-1] / INITIAL_CAPITAL) - 1) * 100
    win_trades = len([t for t in trades if t['pnl_pct'] > 0])
    stats_text = f"Итого: {INITIAL_CAPITAL} → {equities[-1]:.2f} USDT ({total_return:+.1f}%)\n" \
                 f"Сделок: {len(trades)} | Прибыльных: {win_trades}/{len(trades)} ({win_trades/len(trades)*100:.0f}%)"
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax1.set_ylabel('Equity (USDT)', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')

    # Price
    ax2.plot(dates, prices, color='#3498db', linewidth=1.5, label=f'{symbol} Price')
    ax2.set_ylabel('Price (USDT)', fontsize=11)
    ax2.set_xlabel('Date', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left')

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path = rf"C:\Users\i59400f\Desktop\ai-agent\TsLabWorkspace\SkSred\skred_{symbol.lower()}_equity.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"График: {output_path}")
    return output_path


def main():
    symbol = 'XLMUSD_PERP'
    csv_path = r"C:\Users\i59400f\Desktop\ai-agent\tmp\market_data\ALL_INSTRUMENTS_H4_60d.csv"
    df_all = pd.read_csv(csv_path)
    df = df_all[df_all['symbol'] == symbol].copy()

    print("=" * 90)
    print(f"БЭКТЕСТ: {symbol} | H4 | SMA({SMA_SHORT}/{SMA_LONG}) | EMA{EMA_TREND}")
    print(f"Капитал: {INITIAL_CAPITAL} USDT | Плечо: {LEVERAGE}x | Объём: {INITIAL_CAPITAL * LEVERAGE} USDT")
    print(f"ATR SL:{ATR_SL_MULT}x TP:{ATR_TP_MULT}x | Trailing:{TRAIL_ACTIVATE_PCT*100:.0f}%/{TRAIL_DISTANCE_PCT*100:.1f}%")
    print("=" * 90)
    print(f"Данные: {len(df)} баров (H4) | {df['timestamp'].min()} — {df['timestamp'].max()}")
    print(f"Цена: {df.iloc[0]['close']:.4f} → {df.iloc[-1]['close']:.4f}")
    print(f"Рост актива: {((df.iloc[-1]['close'] / df.iloc[0]['close']) - 1) * 100:+.2f}%")

    trades, equity_curve = run_backtest(df)

    # Таблица сделок
    print(f"\n{'='*90}")
    print("ВСЕ СДЕЛКИ")
    print(f"{'='*90}")
    print(f"{'#':>3} {'Направл':>7} {'Вход':>10} {'Выход':>10} {'PnL%':>9} {'USDT':>10} {'Тип':>7} {'Капитал':>10}")
    print("-" * 90)

    for idx, t in enumerate(trades, 1):
        print(f"{idx:>3} {t['direction']:>7} {t['entry_price']:>10.4f} {t['exit_price']:>10.4f} "
              f"{t['pnl_pct']:>+8.2f}% {t['profit_usd']:>+10.2f} {t['exit_type']:>7} {t['capital_after']:>10.2f}")

    # Статистика
    total_trades = len(trades)
    if total_trades == 0:
        print("Нет сделок")
        return

    wins = [t for t in trades if t['pnl_pct'] > 0]
    losses = [t for t in trades if t['pnl_pct'] <= 0]
    win_rate = len(wins) / total_trades * 100
    avg_win = np.mean([t['pnl_pct'] for t in wins]) if wins else 0
    avg_loss = np.mean([t['pnl_pct'] for t in losses]) if losses else 0
    best = max(trades, key=lambda x: x['pnl_pct'])
    worst = min(trades, key=lambda x: x['pnl_pct'])
    gross_profit = sum(t['profit_usd'] for t in wins) if wins else 0
    gross_loss = abs(sum(t['profit_usd'] for t in losses)) if losses else 0.0001
    pf = gross_profit / gross_loss
    final_equity = equity_curve[-1]['equity']
    total_return = ((final_equity / INITIAL_CAPITAL) - 1) * 100
    equity_arr = np.array([d['equity'] for d in equity_curve])
    peak = np.maximum.accumulate(equity_arr)
    dd = (peak - equity_arr) / peak
    max_dd = dd.max() * 100

    print(f"\n{'='*90}")
    print("СТАТИСТИКА")
    print(f"{'='*90}")
    print(f"Начало:          {INITIAL_CAPITAL:.2f} USDT")
    print(f"Конец:           {final_equity:.2f} USDT")
    print(f"Прибыль:         {final_equity - INITIAL_CAPITAL:+.2f} USDT")
    print(f"Доходность:      {total_return:+.2f}%")
    print(f"")
    print(f"Сделок:          {total_trades}")
    print(f"Прибыльных:      {len(wins)} ({win_rate:.1f}%)")
    print(f"Убыточных:       {len(losses)}")
    print(f"")
    print(f"Средняя прибыль: {avg_win:+.2f}%")
    print(f"Средний убыток:  {avg_loss:+.2f}%")
    print(f"Лучшая:          {best['pnl_pct']:+.2f}% = {best['profit_usd']:+.2f} USDT ({best['exit_type']})")
    print(f"Худшая:          {worst['pnl_pct']:+.2f}% = {worst['profit_usd']:+.2f} USDT ({worst['exit_type']})")
    print(f"")
    print(f"Profit Factor:   {pf:.2f}")
    print(f"Макс. просадка:  {max_dd:.2f}%")

    # Exit types
    sl = len([t for t in trades if t['exit_type'] == 'SL'])
    tp = len([t for t in trades if t['exit_type'] == 'TP'])
    trail = len([t for t in trades if t['exit_type'] == 'TRAIL'])
    sig = len([t for t in trades if t['exit_type'] == 'SIGNAL'])
    print(f"\nТипы выходов:")
    print(f"  Trailing Stop: {trail} ({trail/total_trades*100:.0f}%)")
    print(f"  Take Profit:   {tp} ({tp/total_trades*100:.0f}%)")
    print(f"  Signal:        {sig} ({sig/total_trades*100:.0f}%)")
    print(f"  Stop Loss:     {sl} ({sl/total_trades*100:.0f}%)")

    # Plot
    chart_path = plot_results(trades, equity_curve, symbol)

    # Save CSV
    df_trades = pd.DataFrame(trades)
    csv_out = r"C:\Users\i59400f\Desktop\ai-agent\TsLabWorkspace\SkSred\skred_xlm_trades.csv"
    df_trades.to_csv(csv_out, index=False)
    print(f"\nСделки: {csv_out}")


if __name__ == "__main__":
    main()
