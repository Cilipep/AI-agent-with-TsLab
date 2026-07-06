import pandas as pd
import numpy as np

# Параметры
SMA_SHORT = 7
SMA_LONG = 20
EMA_TREND = 200
ATR_PERIOD = 14
ATR_SL_MULT = 1.5
ATR_TP_MULT = 3.0
TRAIL_ACTIVATE_PCT = 0.02
TRAIL_DISTANCE_PCT = 0.015
COMMISSION_PCT = 0.05 / 100

# Леверидж
INITIAL_CAPITAL = 50  # 50 USDT
LEVERAGE = 50         # 50x
POSITION_SIZE_PCT = 1.0  # Используем 100% капитала на сделку

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calculate_atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def run_leveraged_backtest(df):
    df = df.sort_values('timestamp').reset_index(drop=True)

    df['sma_short'] = df['close'].rolling(window=SMA_SHORT).mean()
    df['sma_long'] = df['close'].rolling(window=SMA_LONG).mean()
    df['atr'] = calculate_atr(df, ATR_PERIOD)

    available_bars = len(df)
    ema_period = EMA_TREND if available_bars >= EMA_TREND else min(20, available_bars // 2)
    df['ema_trend'] = calculate_ema(df['close'], ema_period)

    df = df.dropna(subset=['sma_short', 'sma_long', 'ema_trend', 'atr']).reset_index(drop=True)

    if len(df) < SMA_LONG + 2:
        return None

    capital = INITIAL_CAPITAL
    position = 0
    entry_price = 0
    entry_time = None
    position_qty = 0  # Количество единиц актива
    trades = []
    equity_curve = [capital]
    trail_activated = False
    trail_high = 0
    trail_low = float('inf')

    for i in range(1, len(df)):
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

        # LONG
        if position == 1:
            sl_price = entry_price - sl_distance
            tp_price = entry_price + tp_distance

            if low_price <= sl_price:
                exit_price = sl_price
                pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
                commission = COMMISSION_PCT * 2 * LEVERAGE
                net_pnl_pct = pnl_pct - commission
                profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
                capital += profit_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': df.iloc[i]['timestamp'],
                    'direction': 'LONG', 'exit_type': 'SL',
                    'entry_price': entry_price, 'exit_price': exit_price,
                    'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
                    'capital_after': capital, 'qty': position_qty
                })
                position = 0
                trail_activated = False
            elif high_price >= tp_price:
                exit_price = tp_price
                pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
                commission = COMMISSION_PCT * 2 * LEVERAGE
                net_pnl_pct = pnl_pct - commission
                profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
                capital += profit_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': df.iloc[i]['timestamp'],
                    'direction': 'LONG', 'exit_type': 'TP',
                    'entry_price': entry_price, 'exit_price': exit_price,
                    'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
                    'capital_after': capital, 'qty': position_qty
                })
                position = 0
                trail_activated = False
            elif trail_activated:
                if low_price <= trail_high * (1 - TRAIL_DISTANCE_PCT):
                    exit_price = trail_high * (1 - TRAIL_DISTANCE_PCT)
                    pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
                    commission = COMMISSION_PCT * 2 * LEVERAGE
                    net_pnl_pct = pnl_pct - commission
                    profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
                    capital += profit_usd
                    trades.append({
                        'entry_time': entry_time, 'exit_time': df.iloc[i]['timestamp'],
                        'direction': 'LONG', 'exit_type': 'TRAIL',
                        'entry_price': entry_price, 'exit_price': exit_price,
                        'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
                        'capital_after': capital, 'qty': position_qty
                    })
                    position = 0
                    trail_activated = False

        # SHORT
        elif position == -1:
            sl_price = entry_price + sl_distance
            tp_price = entry_price - tp_distance

            if high_price >= sl_price:
                exit_price = sl_price
                pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
                commission = COMMISSION_PCT * 2 * LEVERAGE
                net_pnl_pct = pnl_pct - commission
                profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
                capital += profit_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': df.iloc[i]['timestamp'],
                    'direction': 'SHORT', 'exit_type': 'SL',
                    'entry_price': entry_price, 'exit_price': exit_price,
                    'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
                    'capital_after': capital, 'qty': position_qty
                })
                position = 0
                trail_activated = False
            elif low_price <= tp_price:
                exit_price = tp_price
                pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
                commission = COMMISSION_PCT * 2 * LEVERAGE
                net_pnl_pct = pnl_pct - commission
                profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
                capital += profit_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': df.iloc[i]['timestamp'],
                    'direction': 'SHORT', 'exit_type': 'TP',
                    'entry_price': entry_price, 'exit_price': exit_price,
                    'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
                    'capital_after': capital, 'qty': position_qty
                })
                position = 0
                trail_activated = False
            elif trail_activated:
                if high_price >= trail_low * (1 + TRAIL_DISTANCE_PCT):
                    exit_price = trail_low * (1 + TRAIL_DISTANCE_PCT)
                    pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
                    commission = COMMISSION_PCT * 2 * LEVERAGE
                    net_pnl_pct = pnl_pct - commission
                    profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
                    capital += profit_usd
                    trades.append({
                        'entry_time': entry_time, 'exit_time': df.iloc[i]['timestamp'],
                        'direction': 'SHORT', 'exit_type': 'TRAIL',
                        'entry_price': entry_price, 'exit_price': exit_price,
                        'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
                        'capital_after': capital, 'qty': position_qty
                    })
                    position = 0
                    trail_activated = False

        # Trailing update
        if position == 1:
            if not trail_activated:
                unrealized_pct = (high_price - entry_price) / entry_price
                if unrealized_pct >= TRAIL_ACTIVATE_PCT:
                    trail_activated = True
                    trail_high = high_price
            else:
                trail_high = max(trail_high, high_price)
        elif position == -1:
            if not trail_activated:
                unrealized_pct = (entry_price - low_price) / entry_price
                if unrealized_pct >= TRAIL_ACTIVATE_PCT:
                    trail_activated = True
                    trail_low = low_price
            else:
                trail_low = min(trail_low, low_price)

        # Signal exits
        if position == 1 and death_cross:
            exit_price = current_price
            pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
            commission = COMMISSION_PCT * 2 * LEVERAGE
            net_pnl_pct = pnl_pct - commission
            profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
            capital += profit_usd
            trades.append({
                'entry_time': entry_time, 'exit_time': df.iloc[i]['timestamp'],
                'direction': 'LONG', 'exit_type': 'SIGNAL',
                'entry_price': entry_price, 'exit_price': exit_price,
                'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
                'capital_after': capital, 'qty': position_qty
            })
            position = 0
            trail_activated = False
        elif position == -1 and golden_cross:
            exit_price = current_price
            pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
            commission = COMMISSION_PCT * 2 * LEVERAGE
            net_pnl_pct = pnl_pct - commission
            profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
            capital += profit_usd
            trades.append({
                'entry_time': entry_time, 'exit_time': df.iloc[i]['timestamp'],
                'direction': 'SHORT', 'exit_type': 'SIGNAL',
                'entry_price': entry_price, 'exit_price': exit_price,
                'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
                'capital_after': capital, 'qty': position_qty
            })
            position = 0
            trail_activated = False

        # Entries
        if position == 0 and capital > 0:
            if golden_cross and current_price > ema_trend:
                position = 1
                entry_price = current_price
                entry_time = df.iloc[i]['timestamp']
                position_qty = (capital * POSITION_SIZE_PCT * LEVERAGE) / current_price
                trail_activated = False
                trail_high = current_price
            elif death_cross and current_price < ema_trend:
                position = -1
                entry_price = current_price
                entry_time = df.iloc[i]['timestamp']
                position_qty = (capital * POSITION_SIZE_PCT * LEVERAGE) / current_price
                trail_activated = False
                trail_low = current_price

        equity_curve.append(capital)

        # Ликвидация при нулевом капитале
        if capital <= 0:
            print("\n!!! ЛИКВИДАЦИЯ — капитал = 0 !!!")
            break

    # Close open
    if position != 0 and capital > 0:
        exit_price = df.iloc[-1]['close']
        if position == 1:
            pnl_pct = (exit_price - entry_price) / entry_price * LEVERAGE
        else:
            pnl_pct = (entry_price - exit_price) / entry_price * LEVERAGE
        commission = COMMISSION_PCT * 2 * LEVERAGE
        net_pnl_pct = pnl_pct - commission
        profit_usd = capital * POSITION_SIZE_PCT * net_pnl_pct
        capital += profit_usd
        trades.append({
            'entry_time': entry_time, 'exit_time': df.iloc[-1]['timestamp'],
            'direction': 'LONG' if position == 1 else 'SHORT', 'exit_type': 'EOD',
            'entry_price': entry_price, 'exit_price': exit_price,
            'pnl_pct': net_pnl_pct * 100, 'profit_usd': profit_usd,
            'capital_after': capital, 'qty': position_qty
        })

    return trades, equity_curve


def main():
    symbol = 'NEARUSD_PERP'
    csv_path = r"C:\Users\i59400f\Desktop\ai-agent\tmp\market_data\ALL_INSTRUMENTS_H4_60d.csv"

    df_all = pd.read_csv(csv_path)
    df = df_all[df_all['symbol'] == symbol].copy()

    print("=" * 95)
    print(f"БЭКТЕСТ С ПЛЕЧОМ: {symbol} | H4 | SMA({SMA_SHORT}/{SMA_LONG}) | EMA{EMA_TREND}")
    print(f"Капитал: {INITIAL_CAPITAL} USDT | Плечо: {LEVERAGE}x | Объём позиции: {INITIAL_CAPITAL * LEVERAGE} USDT")
    print(f"ATR SL:{ATR_SL_MULT}x TP:{ATR_TP_MULT}x | Trailing:{TRAIL_ACTIVATE_PCT*100:.0f}%/{TRAIL_DISTANCE_PCT*100:.1f}%")
    print("=" * 95)
    print(f"Данные: {len(df)} баров (H4) | {df['timestamp'].min()} — {df['timestamp'].max()}")
    print(f"Цена NEAR: {df.iloc[0]['close']:.4f} → {df.iloc[-1]['close']:.4f}")
    print(f"Рост актива: {((df.iloc[-1]['close'] / df.iloc[0]['close']) - 1) * 100:+.2f}%")

    result = run_leveraged_backtest(df)
    if result is None:
        print("Недостаточно данных")
        return

    trades, equity_curve = result

    # Таблица сделок
    print(f"\n{'='*95}")
    print("ВСЕ СДЕЛКИ")
    print(f"{'='*95}")
    print(f"{'#':>3} {'Направл':>7} {'Вход':>10} {'Выход':>10} {'PnL%':>9} {'USDT':>10} {'Тип':>7} {'Капитал':>10}")
    print("-" * 95)

    for idx, t in enumerate(trades, 1):
        entry_str = f"{t['entry_price']:.4f}"
        exit_str = f"{t['exit_price']:.4f}"
        pnl_str = f"{t['pnl_pct']:+.2f}%"
        usdt_str = f"{t['profit_usd']:+.2f}"
        cap_str = f"{t['capital_after']:.2f}"
        print(f"{idx:>3} {t['direction']:>7} {entry_str:>10} {exit_str:>10} {pnl_str:>9} {usdt_str:>10} {t['exit_type']:>7} {cap_str:>10}")

    # Статистика
    print(f"\n{'='*95}")
    print("СТАТИСТИКА")
    print(f"{'='*95}")

    total_trades = len(trades)
    if total_trades == 0:
        print("Нет сделок")
        return

    wins = [t for t in trades if t['pnl_pct'] > 0]
    losses = [t for t in trades if t['pnl_pct'] <= 0]
    long_trades = [t for t in trades if t['direction'] == 'LONG']
    short_trades = [t for t in trades if t['direction'] == 'SHORT']
    sl_trades = [t for t in trades if t['exit_type'] == 'SL']
    tp_trades = [t for t in trades if t['exit_type'] == 'TP']
    trail_trades = [t for t in trades if t['exit_type'] == 'TRAIL']
    signal_trades = [t for t in trades if t['exit_type'] == 'SIGNAL']

    win_rate = len(wins) / total_trades * 100
    avg_win = np.mean([t['pnl_pct'] for t in wins]) if wins else 0
    avg_loss = np.mean([t['pnl_pct'] for t in losses]) if losses else 0
    total_profit = sum(t['profit_usd'] for t in trades)
    best_trade = max(trades, key=lambda x: x['pnl_pct'])
    worst_trade = min(trades, key=lambda x: x['pnl_pct'])

    gross_profit = sum(t['profit_usd'] for t in wins) if wins else 0
    gross_loss = abs(sum(t['profit_usd'] for t in losses)) if losses else 0.0001
    profit_factor = gross_profit / gross_loss

    total_return = ((equity_curve[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    equity = np.array(equity_curve)
    peak = np.maximum.accumulate(equity)
    drawdown = (peak - equity) / peak
    max_drawdown = drawdown.max() * 100

    print(f"Начальный капитал:     {INITIAL_CAPITAL:.2f} USDT")
    print(f"Конечный капитал:      {equity_curve[-1]:.2f} USDT")
    print(f"Чистая прибыль:        {equity_curve[-1] - INITIAL_CAPITAL:+.2f} USDT")
    print(f"Доходность:            {total_return:+.2f}%")
    print(f"")
    print(f"Всего сделок:          {total_trades}")
    print(f"  Long:                {len(long_trades)}")
    print(f"  Short:               {len(short_trades)}")
    print(f"Прибыльных:            {len(wins)} ({win_rate:.1f}%)")
    print(f"Убыточных:             {len(losses)}")
    print(f"")
    print(f"Средняя прибыль:       {avg_win:+.2f}% ({avg_win/LEVERAGE:+.2f}% без плеча)")
    print(f"Средний убыток:        {avg_loss:+.2f}% ({avg_loss/LEVERAGE:+.2f}% без плеча)")
    print(f"Лучшая сделка:         {best_trade['pnl_pct']:+.2f}% = {best_trade['profit_usd']:+.2f} USDT")
    print(f"Худшая сделка:         {worst_trade['pnl_pct']:+.2f}% = {worst_trade['profit_usd']:+.2f} USDT")
    print(f"")
    print(f"Profit Factor:         {profit_factor:.2f}")
    print(f"Макс. просадка:        {max_drawdown:.2f}% ({max_drawdown/LEVERAGE:.2f}% без плеча)")
    print(f"")
    print(f"Типы выходов:")
    print(f"  Trailing Stop:       {len(trail_trades)} ({len(trail_trades)/total_trades*100:.0f}%)")
    print(f"  Take Profit:         {len(tp_trades)} ({len(tp_trades)/total_trades*100:.0f}%)")
    print(f"  Signal:              {len(signal_trades)} ({len(signal_trades)/total_trades*100:.0f}%)")
    print(f"  Stop Loss:           {len(sl_trades)} ({len(sl_trades)/total_trades*100:.0f}%)")

    # Сравнение с без плеча
    print(f"\n{'='*95}")
    print("СРАВНЕНИЕ: С ПЛЕЧОМ vs БЕЗ ПЛЕЧА")
    print(f"{'='*95}")
    no_lev = total_return / LEVERAGE
    print(f"  С плечом {LEVERAGE}x:     {total_return:+.2f}%  →  {equity_curve[-1]:.2f} USDT")
    print(f"  Без плеча:           {no_lev:+.2f}%  →  {INITIAL_CAPITAL * (1 + no_lev/100):.2f} USDT")
    print(f"  Множитель дохода:    {LEVERAGE}x")
    print(f"  Множитель просадки: {LEVERAGE}x")

    # Кривая капитала
    print(f"\n{'='*95}")
    print("КРИВАЯ КАПИТАЛА")
    print(f"{'='*95}")
    step = max(1, len(equity_curve) // 25)
    for j in range(0, len(equity_curve), step):
        bar_date = df.iloc[min(j, len(df)-1)]['timestamp'] if j < len(df) else df.iloc[-1]['timestamp']
        val = equity_curve[j]
        change = ((val - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
        bar_len = max(0, int(abs(change) / 1.5))
        bar = '+' * bar_len if change >= 0 else '-' * bar_len
        print(f"  {str(bar_date)[:16]} | {val:>10.2f} USDT | {change:>+8.2f}% | {bar}")

    print(f"\n  {'ФИНАЛ':>16} | {equity_curve[-1]:>10.2f} USDT | {total_return:>+8.2f}%")


if __name__ == "__main__":
    main()
