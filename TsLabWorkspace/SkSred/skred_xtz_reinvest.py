import pandas as pd
import numpy as np

# Параметры
SMA_SHORT, SMA_LONG = 3, 15
EMA_TREND, ATR_PERIOD = 200, 14
ATR_SL_MULT, ATR_TP_MULT = 1.5, 3.0
TRAIL_ACTIVATE, TRAIL_DIST = 0.02, 0.015
COMMISSION = 0.0005
INITIAL, LEVERAGE = 60, 5
REINVEST_PCT = 0.20  # 20% от NET-прибыли реинвестируется

def calc_ema(s, p): return s.ewm(span=p, adjust=False).mean()
def calc_atr(df, p=14):
    tr = pd.concat([df['high']-df['low'], abs(df['high']-df['close'].shift(1)), abs(df['low']-df['close'].shift(1))], axis=1).max(axis=1)
    return tr.rolling(p).mean()

df = pd.read_csv(r"C:\Users\i59400f\Desktop\ai-agent\tmp\market_data\ALL_INSTRUMENTS_H4_60d.csv")
df = df[df['symbol']=='XTZUSD_PERP'].sort_values('timestamp').reset_index(drop=True)
df['sma_s'] = df['close'].rolling(SMA_SHORT).mean()
df['sma_l'] = df['close'].rolling(SMA_LONG).mean()
df['atr'] = calc_atr(df)
df['ema'] = calc_ema(df['close'], min(EMA_TREND, max(20, len(df)//2)))
df = df.dropna().reset_index(drop=True)

# Переменные состояния
cap, pos, ep, et = INITIAL, 0, 0, None
th_on, th, tl = False, 0, float('inf')
net_profit = 0  # Накопленная NET-прибыль
position_size = INITIAL  # Размер текущей позиции
trades, eq = [], [{'t': df.iloc[0]['timestamp'], 'e': cap, 'p': df.iloc[0]['close']}]

for i in range(1, len(df)):
    ts = df.iloc[i]['timestamp']
    cp, hp, lp = df.iloc[i]['close'], df.iloc[i]['high'], df.iloc[i]['low']
    s1t, s2t = df.iloc[i]['sma_s'], df.iloc[i]['sma_l']
    s1y, s2y = df.iloc[i-1]['sma_s'], df.iloc[i-1]['sma_l']
    ema_val, atr_val = df.iloc[i]['ema'], df.iloc[i]['atr']
    gc = (s1t>s2t) and (s1y<=s2y)
    dc = (s1t<s2t) and (s1y>=s2y)
    sl_d, tp_d = atr_val*ATR_SL_MULT, atr_val*ATR_TP_MULT
    exit_reason = None
    exit_px = None

    # Проверка SL/TP/Trail для Long
    if pos==1:
        sl_p, tp_p = ep-sl_d, ep+tp_d
        if lp<=sl_p: exit_reason, exit_px = 'SL', sl_p
        elif hp>=tp_p: exit_reason, exit_px = 'TP', tp_p
        elif th_on and lp<=th*(1-TRAIL_DIST): exit_reason, exit_px = 'TRAIL', th*(1-TRAIL_DIST)
    # Проверка для Short
    elif pos==-1:
        sl_p, tp_p = ep+sl_d, ep-tp_d
        if hp>=sl_p: exit_reason, exit_px = 'SL', sl_p
        elif lp<=tp_p: exit_reason, exit_px = 'TP', tp_p
        elif th_on and hp>=tl*(1+TRAIL_DIST): exit_reason, exit_px = 'TRAIL', tl*(1+TRAIL_DIST)

    # Сигнальные выходы
    if pos==1 and dc and not exit_reason: exit_reason, exit_px = 'SIGNAL', cp
    elif pos==-1 and gc and not exit_reason: exit_reason, exit_px = 'SIGNAL', cp

    # Исполнение выхода
    if exit_reason and pos!=0:
        pnl = ((exit_px-ep)/ep*LEVERAGE) if pos==1 else ((ep-exit_px)/ep*LEVERAGE)
        net = pnl - COMMISSION*2*LEVERAGE
        profit = position_size * net  # Прибыль от размера позиции
        cap += profit
        net_profit += profit  # Увеличиваем накопленную NET-прибыль

        trades.append({
            'entry_time': et, 'exit_time': ts,
            'dir': 'LONG' if pos==1 else 'SHORT',
            'exit': exit_reason,
            'entry': ep, 'exit_px': exit_px,
            'pnl': net*100, 'profit': profit,
            'pos_size': position_size,
            'net_profit': net_profit,
            'cap': cap
        })
        pos, th_on = 0, False

    # Обновление Trailing Stop
    if pos==1:
        if not th_on and (hp-ep)/ep>=TRAIL_ACTIVATE: th_on, th = True, hp
        elif th_on: th = max(th, hp)
    elif pos==-1:
        if not th_on and (ep-lp)/ep>=TRAIL_ACTIVATE: th_on, tl = True, lp
        elif th_on: tl = min(tl, lp)

    # Вход в позицию с реинвестированием
    if pos==0 and cap>0:
        # Размер позиции = текущий капитал + 10% от накопленной NET-прибыли
        reinvest_amount = max(0, net_profit * REINVEST_PCT)
        position_size = cap + reinvest_amount

        if gc and cp>ema_val:
            pos, ep, et, th_on, th = 1, cp, ts, False, cp
        elif dc and cp<ema_val:
            pos, ep, et, th_on, tl = -1, cp, ts, False, cp

    eq.append({'t':ts, 'e':cap, 'p':cp})
    if cap<=0: break

# Закрытие открытой позиции
if pos!=0 and cap>0:
    xp = df.iloc[-1]['close']
    pnl = ((xp-ep)/ep*LEVERAGE) if pos==1 else ((ep-xp)/ep*LEVERAGE)
    net = pnl - COMMISSION*2*LEVERAGE
    profit = position_size * net
    cap += profit
    net_profit += profit
    trades.append({
        'entry_time': et, 'exit_time': df.iloc[-1]['timestamp'],
        'dir': 'LONG' if pos==1 else 'SHORT', 'exit': 'EOD',
        'entry': ep, 'exit_px': xp,
        'pnl': net*100, 'profit': profit,
        'pos_size': position_size,
        'net_profit': net_profit,
        'cap': cap
    })

# Статистика
n = len(trades)
wins = [t for t in trades if t['pnl']>0]
losses = [t for t in trades if t['pnl']<=0]
wr = len(wins)/n*100 if n else 0
gp = sum(t['profit'] for t in wins) if wins else 0
gl = abs(sum(t['profit'] for t in losses)) or 0.0001
pf = gp/gl
eq_arr = np.array([d['e'] for d in eq])
ret = ((eq_arr[-1]/INITIAL)-1)*100
dd = ((np.maximum.accumulate(eq_arr)-eq_arr)/np.maximum.accumulate(eq_arr)).max()*100
final = eq_arr[-1]

# Вывод результатов
print("="*95)
print(f"БЭКТЕСТ С РЕИНВЕСТИРОВАНИЕМ: XTZUSD_PERP | H4 | SMA({SMA_SHORT}/{SMA_LONG})")
print(f"Капитал: {INITIAL} USDT | Плечо: {LEVERAGE}x | Реинвест: {REINVEST_PCT*100:.0f}% от NET-прибыли")
print("="*95)
print(f"Данные: {len(df)} баров | {df.iloc[0]['timestamp']} — {df.iloc[-1]['timestamp']}")
print(f"Цена: {df.iloc[0]['close']:.4f} → {df.iloc[-1]['close']:.4f}")
print(f"Рост актива: {((df.iloc[-1]['close']/df.iloc[0]['close'])-1)*100:+.2f}%")

print(f"\n{'='*95}")
print("СДЕЛКИ")
print(f"{'='*95}")
print(f"{'#':>3} {'Направл':>7} {'Вход':>10} {'Выход':>10} {'PnL%':>9} {'Позиция':>10} {'Прибыль':>10} {'Тип':>7} {'Капитал':>10}")
print("-"*95)

for i,t in enumerate(trades,1):
    print(f"{i:>3} {t['dir']:>7} {t['entry']:>10.4f} {t['exit_px']:>10.4f} "
          f"{t['pnl']:>+8.2f}% {t['pos_size']:>10.2f} {t['profit']:>+10.2f} {t['exit']:>7} {t['cap']:>10.2f}")

print(f"\n{'='*95}")
print("СТАТИСТИКА")
print(f"{'='*95}")
print(f"Начало:              {INITIAL:.2f} USDT")
print(f"Конец:               {final:.2f} USDT")
print(f"Прибыль:             {final-INITIAL:+.2f} USDT")
print(f"Доходность:          {ret:+.2f}%")
print(f"")
print(f"Сделок:              {n}")
print(f"Прибыльных:          {len(wins)} ({wr:.1f}%)")
print(f"Убыточных:           {len(losses)}")
print(f"")
if wins: print(f"Средняя прибыль:     {np.mean([t['pnl'] for t in wins]):+.2f}%")
if losses: print(f"Средний убыток:      {np.mean([t['pnl'] for t in losses]):+.2f}%")
print(f"Лучшая сделка:       {max(trades,key=lambda x:x['pnl'])['pnl']:+.2f}% = {max(trades,key=lambda x:x['profit'])['profit']:+.2f} USDT")
print(f"Худшая сделка:       {min(trades,key=lambda x:x['pnl'])['pnl']:+.2f}% = {min(trades,key=lambda x:x['profit'])['profit']:+.2f} USDT")
print(f"")
print(f"Profit Factor:       {pf:.2f}")
print(f"Макс. просадка:      {dd:.2f}%")
print(f"")
print(f"Накопленная NET:     {net_profit:+.2f} USDT")
print(f"Реинвестировано:     {net_profit*REINVEST_PCT:+.2f} USDT (10%)")

# Типы выходов
sl_c = len([t for t in trades if t['exit']=='SL'])
tp_c = len([t for t in trades if t['exit']=='TP'])
tr_c = len([t for t in trades if t['exit']=='TRAIL'])
sg_c = len([t for t in trades if t['exit']=='SIGNAL'])
print(f"\nТипы выходов:")
if n:
    print(f"  Trailing Stop: {tr_c} ({tr_c/n*100:.0f}%)")
    print(f"  Take Profit:   {tp_c} ({tp_c/n*100:.0f}%)")
    print(f"  Signal:        {sg_c} ({sg_c/n*100:.0f}%)")
    print(f"  Stop Loss:     {sl_c} ({sl_c/n*100:.0f}%)")

# Сравнение с без реинвестирования
print(f"\n{'='*95}")
print("СРАВНЕНИЕ: С РЕИНВЕСТОМ vs БЕЗ")
print(f"{'='*95}")
print(f"  Без реинвеста:  60 → 109.88 USDT (+83.13%)")
print(f"  С реинвестом:   60 → {final:.2f} USDT ({ret:+.2f}%)")
print(f"  Дополнительная доходность: {ret-83.13:+.2f} п.п.")
