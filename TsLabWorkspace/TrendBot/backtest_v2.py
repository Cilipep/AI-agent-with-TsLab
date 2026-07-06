"""
TrendBot v2 — Backtest with optimized params
EMA(60/150) + RSI(35-55) + OBV + Engulfing
"""
import os, json, glob
import pandas as pd
import numpy as np
from datetime import datetime

CSV_DIR = r"C:\Users\i59400f\Documents\TSLab 3.0"

# Optimized params
EMA_FAST = 60
EMA_SLOW = 150
RSI_PERIOD = 14
RSI_LOW = 35
RSI_HIGH = 55
OBV_SMA = 20
VOL_RATIO = 1.2
TP_LOOKBACK = 20
RR_MIN = 1.5
MIN_SCORE = 4.0

MARGIN_PCT = 5.0; LEVERAGE = 20.0; USDT = 10.0


def ema(a, p): return pd.Series(a).ewm(span=p, adjust=False).mean().values
def sma(a, p): return pd.Series(a).rolling(p, min_periods=p).mean().values
def rsi(c, p=14):
    d = pd.Series(c).diff()
    g = d.where(d > 0, 0).rolling(p).mean()
    l = (-d.where(d < 0, 0)).rolling(p).mean()
    return (100 - (100 / (1 + g/l))).values
def obv_calc(c, v):
    o = np.zeros(len(c))
    for i in range(1, len(c)):
        if c[i] > c[i-1]: o[i] = o[i-1] + v[i]
        elif c[i] < c[i-1]: o[i] = o[i-1] - v[i]
        else: o[i] = o[i-1]
    return o

def resample_1h(df):
    df = df.copy(); df['Date'] = pd.to_datetime(df['Date']); df = df.set_index('Date')
    return df.resample('1h').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna().reset_index()


def backtest(ticker, df):
    c = df['Close'].values; h = df['High'].values; lo = df['Low'].values
    opn = df['Open'].values; v = df['Volume'].values; n = len(c)
    if n < 200: return None

    ef = ema(c, EMA_FAST); es = ema(c, EMA_SLOW)
    rv = rsi(c, RSI_PERIOD)
    ov = obv_calc(c, v); os_ = sma(ov, OBV_SMA); vs = sma(v, 20)

    pos = 0; ep = 0.; sl = 0.; tp = 0.
    eq = USDT; pk = eq; mdd = 0.; trades = []; entry_dir = 0

    for i in range(1, n):
        if np.isnan(ef[i]) or np.isnan(es[i]) or np.isnan(rv[i]): continue

        uptrend = ef[i] > es[i]
        below_e50 = c[i] < ef[i]; above_e200 = c[i] > es[i]
        above_e50 = c[i] > ef[i]; below_e200 = c[i] < es[i]
        rsi_corr = RSI_LOW <= rv[i] <= RSI_HIGH
        obv_up = ov[i] > os_[i] if not np.isnan(os_[i]) else True
        vol_ok = v[i] > vs[i] * VOL_RATIO if not np.isnan(vs[i]) else True
        engulf = i > 0 and c[i-1] <= opn[i-1] and c[i] > opn[i] and c[i] > opn[i-1] and opn[i] < c[i-1]
        strong_bull = c[i] > opn[i] and (c[i]-opn[i]) > (h[i]-lo[i])*0.6

        # Long score
        ls = 0
        if uptrend: ls += 2
        if below_e50 and above_e200: ls += 1.5
        elif above_e50: ls += 0.5
        if rsi_corr: ls += 1
        if obv_up: ls += 0.5
        if engulf: ls += 1.5
        elif strong_bull: ls += 1
        if vol_ok: ls += 0.5

        # Short score
        ss = 0
        if not uptrend: ss += 2
        if above_e50 and below_e200: ss += 1.5
        if rv[i] > 60: ss += 1
        if not obv_up: ss += 0.5
        if c[i] < opn[i]: ss += 1

        # Manage position
        if pos == 1:
            if lo[i] <= sl:
                pnl = (sl-ep)/ep*USDT*LEVERAGE - USDT*LEVERAGE*0.001
                eq += pnl; trades.append({'pnl':pnl,'dir':'L'}); pos=0
            elif h[i] >= tp:
                pnl = (tp-ep)/ep*USDT*LEVERAGE - USDT*LEVERAGE*0.001
                eq += pnl; trades.append({'pnl':pnl,'dir':'L'}); pos=0
            elif ss >= MIN_SCORE:
                pnl = (c[i]-ep)/ep*USDT*LEVERAGE - USDT*LEVERAGE*0.001
                eq += pnl; trades.append({'pnl':pnl,'dir':'L'}); pos=0
        elif pos == -1:
            if h[i] >= sl:
                pnl = (ep-sl)/ep*USDT*LEVERAGE - USDT*LEVERAGE*0.001
                eq += pnl; trades.append({'pnl':pnl,'dir':'S'}); pos=0
            elif lo[i] <= tp:
                pnl = (ep-tp)/ep*USDT*LEVERAGE - USDT*LEVERAGE*0.001
                eq += pnl; trades.append({'pnl':pnl,'dir':'S'}); pos=0
            elif ls >= MIN_SCORE:
                pnl = (ep-c[i])/ep*USDT*LEVERAGE - USDT*LEVERAGE*0.001
                eq += pnl; trades.append({'pnl':pnl,'dir':'S'}); pos=0

        # New entry
        if pos == 0:
            lb = TP_LOOKBACK
            prev_hi = max(h[max(0,i-lb):i]) if i >= lb else h[i-1]
            prev_lo = min(lo[max(0,i-lb):i]) if i >= lb else lo[i-1]

            if ls >= MIN_SCORE and above_e200:
                risk = c[i] - es[i]; reward = prev_hi - c[i]
                rr = reward/risk if risk > 0 else 0
                if rr >= RR_MIN:
                    pos=1; ep=c[i]; sl=es[i]; tp=prev_hi; entry_dir=1
            elif ss >= MIN_SCORE and below_e200:
                pos=-1; ep=c[i]; sl=es[i]; tp=prev_lo; entry_dir=-1

        pk = max(pk, eq); dd = (pk-eq)/pk*100 if pk>0 else 0; mdd = max(mdd, dd)

    if not trades: return None
    w = sum(1 for t in trades if t['pnl']>0)
    gp = sum(t['pnl'] for t in trades if t['pnl']>0)
    gl = abs(sum(t['pnl'] for t in trades if t['pnl']<0))
    pf = gp/gl if gl > 0 else 0

    return {
        'ticker': ticker, 'trades': len(trades), 'wins': w,
        'wr': round(w/len(trades)*100,1),
        'pnl': round(sum(t['pnl'] for t in trades),4),
        'pnl_pct': round((eq-USDT)/USDT*100,2),
        'pf': round(pf,2), 'mdd': round(mdd,2),
        'final': round(eq,4),
    }


def main():
    csvs = sorted(glob.glob(os.path.join(CSV_DIR, "*_PERP.csv")))
    results = []

    print(f"TrendBot v2 — Optimized Backtest")
    print(f"{'='*80}")
    print(f"Strategy: EMA({EMA_FAST}/{EMA_SLOW}) + RSI({RSI_LOW}-{RSI_HIGH}) + OBV + Engulfing")
    print(f"SL: EMA200 | TP: Prev {TP_LOOKBACK} bars high | RR >= {RR_MIN}")
    print(f"{'='*80}")

    for csv_path in csvs:
        ticker = os.path.basename(csv_path).replace('.csv','').replace('USD_PERP','')
        try:
            df = pd.read_csv(csv_path)
            df_1h = resample_1h(df)
            r = backtest(ticker, df_1h)
            if r:
                results.append(r)
                s = "+" if r['pnl_pct'] > 0 else ""
                print(f"{ticker:<8} {s}{r['pnl_pct']:>8}%  T={r['trades']:>3}  PF={r['pf']:<6}  WR={r['wr']}%  MaxDD={r['mdd']}%")
        except Exception as e:
            print(f"{ticker}: Error - {e}")

    profitable = [r for r in results if r['pnl_pct'] > 0]
    print(f"\n{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}")
    print(f"Pairs: {len(results)} | Profitable: {len(profitable)}/{len(results)} ({len(profitable)/len(results)*100:.0f}%)")

    ti = USDT * len(results)
    tf = sum(r['final'] for r in results)
    tr = (tf - ti) / ti * 100
    avg_pf = np.mean([r['pf'] for r in results if r['pf'] > 0]) if any(r['pf'] > 0 for r in results) else 0

    print(f"Invested: {ti:.0f} USDT | Final: {tf:.2f} USDT | Return: {tr:+.2f}%")
    print(f"Avg PF: {avg_pf:.2f}")

    if profitable:
        best = max(profitable, key=lambda x: x['pnl_pct'])
        print(f"Best: {best['ticker']} +{best['pnl_pct']}% (PF={best['pf']})")
    losers = [r for r in results if r['pnl_pct'] < 0]
    if losers:
        worst = min(losers, key=lambda x: x['pnl_pct'])
        print(f"Worst: {worst['ticker']} {worst['pnl_pct']}% (PF={worst['pf']})")

    # Filtered portfolio (PF>1, MaxDD<100)
    filtered = [r for r in results if r['pf'] >= 1.0 and r['mdd'] <= 100]
    if filtered:
        fti = USDT * len(filtered)
        ftf = sum(r['final'] for r in filtered)
        ftr = (ftf - fti) / fti * 100
        print(f"\nFILTERED (PF>=1, MaxDD<=100): {len(filtered)} pairs")
        print(f"Return: {ftr:+.2f}% | Avg PF: {np.mean([r['pf'] for r in filtered]):.2f}")

    out = os.path.join(os.path.dirname(__file__), "backtest_v2_results.json")
    with open(out, 'w') as f:
        json.dump({'timestamp': datetime.now().isoformat(),
                   'params': {'ema_fast': EMA_FAST, 'ema_slow': EMA_SLOW, 'rsi_low': RSI_LOW, 'rsi_high': RSI_HIGH},
                   'results': results,
                   'portfolio': {'invested': ti, 'final': tf, 'return_pct': tr}}, f, indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
