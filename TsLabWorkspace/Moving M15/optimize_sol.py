#!/usr/bin/env python3
"""Optimization: Moving M15 Strategy for SOL"""

import pandas as pd
import numpy as np
from itertools import product

def smma(s, p):
    r = s.copy(); fv = s.first_valid_index()
    if fv is None: return pd.Series(np.nan, index=s.index)
    start = s.index.get_loc(fv)
    if start + p > len(s): return pd.Series(np.nan, index=s.index)
    r.iloc[:start] = np.nan; r.iloc[start] = s.iloc[start:start+p].mean()
    for i in range(start+p, len(s)): r.iloc[i] = (r.iloc[i-1]*(p-1)+s.iloc[i])/p
    return r

def wr(h, l, c, p=14):
    return -100*(h.rolling(p).max()-c)/(h.rolling(p).max()-l.rolling(p).min())

def download(sym):
    import yfinance as yf
    for f in [f"{sym}-USD", f"{sym}USD"]:
        try:
            t = yf.Ticker(f); d = t.history(period="6mo", interval="1h")
            if not d.empty and len(d) > 100:
                d = d.reset_index()[['Datetime','Open','High','Low','Close','Volume']]
                d.columns = ['ts','o','h','l','c','v']; d['sym'] = sym; return d
        except: pass
    return None

def bt(df, sl, tp, sp, wp):
    df['s'] = smma(df['c'], sp); df['ss'] = smma(df['c'], sp).shift(sp)
    df['w'] = wr(df['h'], df['l'], df['c'], wp); df['w8'] = smma(df['w'].copy(), 8); df['w21'] = smma(df['w'].copy(), 21)
    df['sig'] = 0; warm = max(22, sp*2+wp)
    for i in range(warm, len(df)):
        s5=df['s'].iloc[i]; s5s=df['ss'].iloc[i]; w=df['w'].iloc[i]; w8=df['w8'].iloc[i]; w21=df['w21'].iloc[i]
        s5p=df['s'].iloc[i-1]; s5sp=df['ss'].iloc[i-1]; wp_=df['w'].iloc[i-1]; w8p=df['w8'].iloc[i-1]
        if s5>s5s and s5p<=s5sp and w>w8 and wp_<=w8p and w>w21: df.loc[df.index[i],'sig']=1
        elif s5<s5s and s5p>=s5sp and w<w8 and wp_>=w8p and w<w21: df.loc[df.index[i],'sig']=-1
    cap=10000; pos=0; ent=0; trades=[]; eq=[10000]
    for i in range(1, len(df)):
        p=df['c'].iloc[i]; hi=df['h'].iloc[i]; lo=df['l'].iloc[i]; sg=df['sig'].iloc[i]
        if pos==1:
            slp=ent*(1-sl); tpp=ent*(1+tp)
            if lo<=slp: pnl=((slp-ent)/ent-0.002)*100; cap+=((slp-ent)/ent-0.002)*cap; trades.append(pnl); pos=0; eq.append(cap); continue
            elif hi>=tpp: pnl=((tpp-ent)/ent-0.002)*100; cap+=((tpp-ent)/ent-0.002)*cap; trades.append(pnl); pos=0; eq.append(cap); continue
        elif pos==-1:
            slp=ent*(1+sl); tpp=ent*(1-tp)
            if hi>=slp: pnl=((ent-slp)/ent-0.002)*100; cap+=((ent-slp)/ent-0.002)*cap; trades.append(pnl); pos=0; eq.append(cap); continue
            elif lo<=tpp: pnl=((ent-tpp)/ent-0.002)*100; cap+=((ent-tpp)/ent-0.002)*cap; trades.append(pnl); pos=0; eq.append(cap); continue
        if sg!=0:
            if pos==1 and sg==-1: pnl=((p-ent)/ent-0.002)*100; cap+=((p-ent)/ent-0.002)*cap; trades.append(pnl); pos=0
            elif pos==-1 and sg==1: pnl=((ent-p)/ent-0.002)*100; cap+=((ent-p)/ent-0.002)*cap; trades.append(pnl); pos=0
            if pos==0: pos=sg; ent=p
        eq.append(cap)
    if pos!=0:
        p=df['c'].iloc[-1]; pnl=((p-ent)/ent-0.002)*100 if pos==1 else ((ent-p)/ent-0.002)*100
        cap+=(pnl/100)*cap; eq.append(cap)
    if len(trades)<3: return None
    wins=[t for t in trades if t>0]; ret=(cap-10000)/100
    peak=eq[0]; mdd=0
    for v in eq:
        if v>peak: peak=v
        dd=(peak-v)/peak*100
        if dd>mdd: mdd=dd
    return {'trades':len(trades),'wins':len(wins),'wr':len(wins)/len(trades)*100,'ret':ret,'mdd':mdd,'fin':cap,
            'aw':np.mean([t for t in trades if t>0]) if wins else 0,'al':np.mean([t for t in trades if t<=0]) if len(wins)<len(trades) else 0,
            'sl':sl*100,'tp':tp*100,'smma':sp,'wrp':wp,'rr':tp/sl}

def main():
    print("="*80)
    print("OPTIMIZATION: Moving M15 - SOL")
    print("="*80)
    df = download("SOL")
    if df is None: print("Failed!"); return
    print(f"Data: {len(df)} bars, ${df['c'].min():.2f} - ${df['c'].max():.2f}")
    
    results = []
    for sl,tp,sp,wp in product([0.02,0.03,0.04],[0.04,0.06,0.08],[5,7],[10,14]):
        if tp<=sl: continue
        r = bt(df.copy(), sl, tp, sp, wp)
        if r: results.append(r)
    
    if not results: print("No results!"); return
    results.sort(key=lambda x: x['ret'], reverse=True)
    
    print(f"\n{len(results)} valid combinations")
    print(f"\n{'SL%':>5} {'TP%':>5} {'S':>3} {'WR':>3} {'#':>4} {'WR%':>5} {'Ret%':>7} {'MDD%':>6} {'W%':>6} {'L%':>6}")
    print("-"*80)
    for r in results:
        s="+" if r['ret']>0 else ""
        print(f"{r['sl']:>5.1f} {r['tp']:>5.1f} {r['smma']:>3} {r['wrp']:>3} "
              f"{r['trades']:>4} {r['wr']:>5.1f} {s}{r['ret']:>6.2f} "
              f"{r['mdd']:>6.1f} {r['aw']:>6.2f} {r['al']:>6.2f}")
    
    b=results[0]
    print(f"\nBEST: SL={b['sl']:.1f}% TP={b['tp']:.1f}% SMMA={b['smma']} WR={b['wrp']}")
    print(f"Return={b['ret']:.2f}% WinRate={b['wr']:.1f}% MDD={b['mdd']:.1f}% R:R=1:{b['rr']:.1f}")
    
    pd.DataFrame(results).to_csv('tmp/moving_m15_opt_sol.csv', index=False)
    print("Saved to tmp/moving_m15_opt_sol.csv")

if __name__ == "__main__":
    main()
