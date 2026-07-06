#!/usr/bin/env python3
"""
Optimization: Moving M15 Strategy for LINK
"""

import pandas as pd
import numpy as np
from itertools import product

def smma(series, period):
    s = series.copy(); result = s.copy()
    fv = s.first_valid_index()
    if fv is None: return pd.Series(np.nan, index=s.index)
    start = s.index.get_loc(fv)
    if start + period > len(s): return pd.Series(np.nan, index=s.index)
    result.iloc[:start] = np.nan; result.iloc[start] = s.iloc[start:start+period].mean()
    for i in range(start+period, len(s)):
        result.iloc[i] = (result.iloc[i-1]*(period-1)+s.iloc[i])/period
    return result

def wr(h, l, c, p=14):
    return -100*(h.rolling(p).max()-c)/(h.rolling(p).max()-l.rolling(p).min())

def download(symbol):
    import yfinance as yf
    for fmt in [f"{symbol}-USD", f"{symbol}USD"]:
        try:
            t = yf.Ticker(fmt); df = t.history(period="6mo", interval="1h")
            if not df.empty and len(df) > 100:
                df = df.reset_index()[['Datetime','Open','High','Low','Close','Volume']]
                df.columns = ['ts','o','h','l','c','v']; df['sym'] = symbol
                return df
        except: continue
    return None

def backtest(df, sl, tp, smma_p, wr_p, commission=0.001):
    c = df['c']; h = df['h']; l = df['l']
    df['s'] = smma(c, smma_p); df['ss'] = smma(c, smma_p).shift(smma_p)
    df['w'] = wr(h, l, c, wr_p); df['w8'] = smma(df['w'].copy(), 8); df['w21'] = smma(df['w'].copy(), 21)
    df['sig'] = 0; warmup = max(22, smma_p*2+wr_p)
    
    for i in range(warmup, len(df)):
        s5=df['s'].iloc[i]; s5s=df['ss'].iloc[i]; w=df['w'].iloc[i]; w8=df['w8'].iloc[i]; w21=df['w21'].iloc[i]
        s5p=df['s'].iloc[i-1]; s5sp=df['ss'].iloc[i-1]; wp=df['w'].iloc[i-1]; w8p=df['w8'].iloc[i-1]
        if s5>s5s and s5p<=s5sp and w>w8 and wp<=w8p and w>w21: df.loc[df.index[i],'sig']=1
        elif s5<s5s and s5p>=s5sp and w<w8 and wp>=w8p and w<w21: df.loc[df.index[i],'sig']=-1
    
    cap=10000; pos=0; entry=0; trades=[]; eq=[10000]
    
    for i in range(1, len(df)):
        p=df['c'].iloc[i]; hi=df['h'].iloc[i]; lo=df['l'].iloc[i]; sig=df['sig'].iloc[i]
        if pos==1:
            sl_p=entry*(1-sl); tp_p=entry*(1+tp)
            if lo<=sl_p: pnl_pct=((sl_p-entry)/entry-commission*2)*100; cap+=((sl_p-entry)/entry-commission*2)*cap; trades.append(pnl_pct); pos=0; eq.append(cap); continue
            elif hi>=tp_p: pnl_pct=((tp_p-entry)/entry-commission*2)*100; cap+=((tp_p-entry)/entry-commission*2)*cap; trades.append(pnl_pct); pos=0; eq.append(cap); continue
        elif pos==-1:
            sl_p=entry*(1+sl); tp_p=entry*(1-tp)
            if hi>=sl_p: pnl_pct=((entry-sl_p)/entry-commission*2)*100; cap+=((entry-sl_p)/entry-commission*2)*cap; trades.append(pnl_pct); pos=0; eq.append(cap); continue
            elif lo<=tp_p: pnl_pct=((entry-tp_p)/entry-commission*2)*100; cap+=((entry-tp_p)/entry-commission*2)*cap; trades.append(pnl_pct); pos=0; eq.append(cap); continue
        if sig!=0:
            if pos==1 and sig==-1:
                pnl_pct=((p-entry)/entry-commission*2)*100; cap+=((p-entry)/entry-commission*2)*cap; trades.append(pnl_pct); pos=0
            elif pos==-1 and sig==1:
                pnl_pct=((entry-p)/entry-commission*2)*100; cap+=((entry-p)/entry-commission*2)*cap; trades.append(pnl_pct); pos=0
            if pos==0: pos=sig; entry=p
        eq.append(cap)
    
    if pos!=0:
        p=df['c'].iloc[-1]
        pnl_pct=((p-entry)/entry-commission*2)*100 if pos==1 else ((entry-p)/entry-commission*2)*100
        cap+=(pnl_pct/100)*cap; eq.append(cap)
    
    if len(trades)<3: return None
    wins=[t for t in trades if t>0]
    ret=(cap-10000)/100
    peak=eq[0]; mdd=0
    for v in eq:
        if v>peak: peak=v
        dd=(peak-v)/peak*100
        if dd>mdd: mdd=dd
    
    return {
        'trades': len(trades), 'wins': len(wins),
        'win_rate': len(wins)/len(trades)*100, 'return': ret,
        'max_dd': mdd, 'final': cap,
        'avg_win': np.mean([t for t in trades if t>0]) if wins else 0,
        'avg_loss': np.mean([t for t in trades if t<=0]) if len(wins)<len(trades) else 0,
        'sl': sl*100, 'tp': tp*100, 'smma': smma_p, 'wr': wr_p,
        'rr': tp/sl if sl>0 else 0,
    }

def main():
    print("=" * 80)
    print("OPTIMIZATION: Moving M15 Strategy - LINK")
    print("=" * 80)
    
    df = download("LINK")
    if df is None or df.empty:
        print("Failed to download!")
        return
    
    print(f"Data: {len(df)} bars, {df['ts'].iloc[0]} to {df['ts'].iloc[-1]}")
    print(f"Price: ${df['c'].min():.2f} - ${df['c'].max():.2f}")
    
    # Parameter ranges
    sl_range = [0.015, 0.02, 0.025, 0.03, 0.04]
    tp_range = [0.03, 0.04, 0.05, 0.06, 0.08]
    smma_range = [3, 5, 7, 10]
    wr_range = [8, 10, 14]
    
    results = []
    total = 0
    
    for sl, tp, smma_p, wr_p in product(sl_range, tp_range, smma_range, wr_range):
        if tp <= sl: continue
        total += 1
        r = backtest(df.copy(), sl, tp, smma_p, wr_p)
        if r: results.append(r)
    
    if not results:
        print("No results!")
        return
    
    results.sort(key=lambda x: x['return'], reverse=True)
    
    print(f"\nTested {total} combinations, {len(results)} valid")
    
    # Top 15
    print("\n" + "=" * 80)
    print("TOP 15:")
    print("=" * 80)
    print(f"{'SL%':>5} {'TP%':>5} {'S':>3} {'WR':>3} {'#':>4} {'WR%':>5} {'Ret%':>7} {'MDD%':>6} {'W%':>6} {'L%':>6} {'R:R':>5}")
    print("-" * 80)
    for r in results[:15]:
        s = "+" if r['return'] > 0 else ""
        print(f"{r['sl']:>5.1f} {r['tp']:>5.1f} {r['smma']:>3} {r['wr']:>3} "
              f"{r['trades']:>4} {r['win_rate']:>5.1f} {s}{r['return']:>6.2f} "
              f"{r['max_dd']:>6.1f} {r['avg_win']:>6.2f} {r['avg_loss']:>6.2f} {r['rr']:>5.1f}")
    
    # Bottom 5
    print("\nWORST 5:")
    print("-" * 80)
    for r in results[-5:]:
        s = "+" if r['return'] > 0 else ""
        print(f"{r['sl']:>5.1f} {r['tp']:>5.1f} {r['smma']:>3} {r['wr']:>3} "
              f"{r['trades']:>4} {r['win_rate']:>5.1f} {s}{r['return']:>6.2f} "
              f"{r['max_dd']:>6.1f} {r['avg_win']:>6.2f} {r['avg_loss']:>6.2f} {r['rr']:>5.1f}")
    
    # Best
    best = results[0]
    print("\n" + "=" * 80)
    print("BEST PARAMETERS:")
    print("=" * 80)
    print(f"Stop Loss:     {best['sl']:.1f}%")
    print(f"Take Profit:   {best['tp']:.1f}%")
    print(f"R:R Ratio:     1:{best['rr']:.1f}")
    print(f"SMMA Period:   {best['smma']}")
    print(f"Williams %R:   {best['wr']}")
    print(f"Trades:        {best['trades']}")
    print(f"Win Rate:      {best['win_rate']:.1f}%")
    print(f"Total Return:  {best['return']:.2f}%")
    print(f"Max Drawdown:  {best['max_dd']:.1f}%")
    print(f"Avg Win:       {best['avg_win']:.2f}%")
    print(f"Avg Loss:      {best['avg_loss']:.2f}%")
    print("=" * 80)
    
    # Save
    pd.DataFrame(results).to_csv('tmp/moving_m15_opt_link.csv', index=False)
    print("\nSaved to tmp/moving_m15_opt_link.csv")

if __name__ == "__main__":
    main()
