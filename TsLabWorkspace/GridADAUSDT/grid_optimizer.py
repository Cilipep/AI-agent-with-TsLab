"""
Grid Bot — Оптимизация параметров для снижения Max Drawdown
"""

import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product

# Загрузка данных
print("Загрузка данных BTC...")
df = yf.download('BTC-USD', period='60d', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"Данные: {len(df)} баров, ${df['Close'].iloc[0]:.0f} — ${df['Close'].iloc[-1]:.0f}")

def calc_atr(df, p=14):
    h, l, c = df['High'], df['Low'], df['Close'].shift(1)
    return pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1).rolling(p).mean()

df['ATR'] = calc_atr(df)

def run_backtest(df, leverage, risk_pct, grid_mult, stop_mult, reinvest_pct, trailing_up, trailing_down):
    capital = 40.0
    position = None
    trades = []
    equity = []
    grid_lower = None
    grid_upper = None
    total_reinvested = 0
    commission = 0.0005

    for i in range(20, len(df)):
        close = df['Close'].iloc[i]
        low = df['Low'].iloc[i]
        high = df['High'].iloc[i]
        atr = df['ATR'].iloc[i]

        if pd.isna(atr) or atr <= 0:
            equity.append({'equity': capital})
            continue

        # Trailing Up/Down
        gs = atr * grid_mult
        if grid_lower is None:
            grid_lower = close - gs
            grid_upper = close + gs
        if close >= grid_upper:
            nu = grid_upper + gs
            if nu <= trailing_up:
                grid_upper = nu
                grid_lower += gs
        if close <= grid_lower:
            nl = grid_lower - gs
            if nl >= trailing_down:
                grid_lower = nl
                grid_upper -= gs

        # Exit
        if position:
            if position['type'] == 'long':
                if low <= position['stop']:
                    pnl = (position['stop'] - position['entry']) * position['qty']
                    comm = (position['entry'] + position['stop']) * position['qty'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'sl'})
                    position = None
                elif high >= position['tp']:
                    pnl = (position['tp'] - position['entry']) * position['qty']
                    comm = (position['entry'] + position['tp']) * position['qty'] * commission
                    reinvest = (pnl - comm) * reinvest_pct if pnl > comm else 0
                    total_reinvested += reinvest
                    capital += pnl - comm + reinvest
                    trades.append({'pnl': pnl - comm, 'reason': 'tp'})
                    position = None
            else:
                if high >= position['stop']:
                    pnl = (position['entry'] - position['stop']) * position['qty']
                    comm = (position['entry'] + position['stop']) * position['qty'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'sl'})
                    position = None
                elif low <= position['tp']:
                    pnl = (position['entry'] - position['tp']) * position['qty']
                    comm = (position['entry'] + position['tp']) * position['qty'] * commission
                    reinvest = (pnl - comm) * reinvest_pct if pnl > comm else 0
                    total_reinvested += reinvest
                    capital += pnl - comm + reinvest
                    trades.append({'pnl': pnl - comm, 'reason': 'tp'})
                    position = None

        # Entry
        if position is None and capital > 1:
            prev = df['Close'].iloc[i-1]
            stop_dist = atr * stop_mult
            gs = atr * grid_mult
            risk_money = capital * risk_pct
            qty = (risk_money * leverage) / stop_dist if stop_dist > 0 else 0
            if qty > 0:
                mv = qty * close / leverage
                if mv > capital * 0.95:
                    qty = (capital * 0.95 * leverage) / close
                if close < prev:
                    position = {'type': 'long', 'entry': close, 'qty': qty,
                               'stop': close - stop_dist, 'tp': close + gs}
                elif close > prev:
                    position = {'type': 'short', 'entry': close, 'qty': qty,
                               'stop': close + stop_dist, 'tp': close - gs}

        unr = 0
        if position:
            unr = ((close - position['entry']) if position['type'] == 'long'
                   else (position['entry'] - close)) * position['qty']
        equity.append(capital + unr)

    # Close last position
    if position:
        lp = df['Close'].iloc[-1]
        if position['type'] == 'long':
            pnl = (lp - position['entry']) * position['qty']
        else:
            pnl = (position['entry'] - lp) * position['qty']
        comm = (position['entry'] + lp) * position['qty'] * commission
        capital += pnl - comm
        trades.append({'pnl': pnl - comm})

    if not trades:
        return None

    pnl = capital - 40.0
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    gp = sum(t['pnl'] for t in wins) if wins else 0
    gl = abs(sum(t['pnl'] for t in losses)) if losses else 0.001
    pk = 40.0
    mdd = 0
    for e in equity:
        if e > pk: pk = e
        dd = (pk - e) / pk
        if dd > mdd: mdd = dd
    ret = pd.Series(equity).pct_change().dropna()
    sh = (ret.mean() / ret.std() * np.sqrt(48*365)) if len(ret) > 1 and ret.std() > 0 else 0

    return {
        'leverage': leverage, 'risk_pct': risk_pct, 'grid_mult': grid_mult,
        'stop_mult': stop_mult, 'reinvest': reinvest_pct,
        'trailing_up': trailing_up, 'trailing_down': trailing_down,
        'pnl': pnl, 'pnl_pct': pnl/40*100, 'trades': len(trades),
        'wr': len(wins)/len(trades)*100 if trades else 0,
        'pf': gp/gl, 'mdd': mdd*100, 'sharpe': sh,
        'reinvested': total_reinvested
    }

# Parameter grid
leverages = [3, 5, 7, 10]
risks = [0.02, 0.03, 0.05, 0.07, 0.10]
grid_mults = [2.0, 2.5, 3.0]
stop_mults = [2.5, 3.0, 3.5]
reinvests = [0.20, 0.30, 0.40]

print(f"\nОптимизация: {len(leverages)*len(risks)*len(grid_mults)*len(stop_mults)*len(reinvests)} комбинаций...")

results = []
for lev, risk, gm, sm, ri in product(leverages, risks, grid_mults, stop_mults, reinvests):
    r = run_backtest(df, lev, risk, gm, sm, ri, 90000, 50000)
    if r:
        results.append(r)

# Filter for DD < 40%
low_dd = [r for r in results if r['mdd'] < 40]

print(f"\nВсего: {len(results)} комбинаций")
print(f"DD < 40%: {len(low_dd)} комбинаций")

# Sort by Sharpe
low_dd.sort(key=lambda x: x['sharpe'], reverse=True)

print(f"\n{'='*100}")
print(f"ТОП-15 (DD < 40%, по Sharpe)")
print(f"{'='*100}")
print(f"{'Lev':>4} {'Risk':>5} {'Grid':>5} {'Stop':>5} {'Reinv':>6} {'PnL$':>8} {'PnL%':>7} {'PF':>5} {'DD%':>6} {'Sharpe':>7} {'Trades':>6}")
print(f"{'-'*90}")
for r in low_dd[:15]:
    print(f"{r['leverage']:>4}x {r['risk_pct']*100:>4.0f}% {r['grid_mult']:>5.1f} {r['stop_mult']:>5.1f} {r['reinvest']*100:>5.0f}% ${r['pnl']:>7.2f} {r['pnl_pct']:>6.1f}% {r['pf']:>5.2f} {r['mdd']:>5.1f}% {r['sharpe']:>7.2f} {r['trades']:>6}")

# Best overall
if low_dd:
    best = low_dd[0]
    print(f"\nЛУЧШАЯ КОНФИГУРАЦИЯ (DD < 40%):")
    print(f"  Leverage: {best['leverage']}x")
    print(f"  Risk: {best['risk_pct']*100:.0f}%")
    print(f"  Grid: {best['grid_mult']}x ATR")
    print(f"  Stop: {best['stop_mult']}x ATR")
    print(f"  Reinvest: {best['reinvest']*100:.0f}%")
    print(f"  PnL: ${best['pnl']:.2f} ({best['pnl_pct']:.1f}%)")
    print(f"  PF: {best['pf']:.2f}")
    print(f"  Max DD: {best['mdd']:.1f}%")
    print(f"  Sharpe: {best['sharpe']:.2f}")
