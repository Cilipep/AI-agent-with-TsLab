#!/usr/bin/env python3
"""Multi-instrument backtest on M5 timeframe"""

import pandas as pd
import numpy as np
from itertools import product

INSTRUMENTS = ["SOL","LINK","ETH","DOGE","FET"]

def smma(s, p):
    r=s.copy(); fv=s.first_valid_index()
    if fv is None: return pd.Series(np.nan, index=s.index)
    start=s.index.get_loc(fv)
    if start+p>len(s): return pd.Series(np.nan, index=s.index)
    r.iloc[:start]=np.nan; r.iloc[start]=s.iloc[start:start+p].mean()
    for i in range(start+p, len(s)): r.iloc[i]=(r.iloc[i-1]*(p-1)+s.iloc[i])/p
    return r

def williams(h, l, c, p=14):
    return -100*(h.rolling(p).max()-c)/(h.rolling(p).max()-l.rolling(p).min())

def dl(sym):
    import yfinance as yf
    for f in [f"{sym}-USD", f"{sym}USD"]:
        try:
            t=yf.Ticker(f); d=t.history(period="30d", interval="5m")
            if not d.empty and len(d)>100:
                d=d.reset_index()[['Datetime','Open','High','Low','Close','Volume']]
                d.columns=['ts','o','h','l','c','v']; d['sym']=sym; return d
        except: pass
    return None

def opt(df,sl,tp,sp,wp):
    tmp=df.copy()
    tmp['s']=smma(tmp['c'],sp); tmp['ss']=smma(tmp['c'],sp).shift(sp)
    tmp['w']=williams(tmp['h'],tmp['l'],tmp['c'],wp); tmp['w8']=smma(tmp['w'].copy(),8); tmp['w21']=smma(tmp['w'].copy(),21)
    tmp['sig']=0; warm=max(22,sp*2+wp)
    for i in range(warm,len(tmp)):
        s5=tmp['s'].iloc[i]; s5s=tmp['ss'].iloc[i]; w=tmp['w'].iloc[i]; w8=tmp['w8'].iloc[i]; w21=tmp['w21'].iloc[i]
        s5p=tmp['s'].iloc[i-1]; s5sp=tmp['ss'].iloc[i-1]; wp_=tmp['w'].iloc[i-1]; w8p=tmp['w8'].iloc[i-1]
        if s5>s5s and s5p<=s5sp and w>w8 and wp_<=w8p and w>w21: tmp.loc[tmp.index[i],'sig']=1
        elif s5<s5s and s5p>=s5sp and w<w8 and wp_>=w8p and w<w21: tmp.loc[tmp.index[i],'sig']=-1
    cap=10000; pos=0; ent=0; trades=[]; eq=[10000]
    for i in range(1,len(tmp)):
        p=tmp['c'].iloc[i]; hi=tmp['h'].iloc[i]; lo=tmp['l'].iloc[i]; sg=tmp['sig'].iloc[i]
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
        p=tmp['c'].iloc[-1]; pnl=((p-ent)/ent-0.002)*100 if pos==1 else ((ent-p)/ent-0.002)*100
        cap+=(pnl/100)*cap; eq.append(cap)
    if len(trades)<3: return None
    wins=[t for t in trades if t>0]; ret=(cap-10000)/100
    peak=eq[0]; mdd=0
    for v in eq:
        if v>peak: peak=v
        dd=(peak-v)/peak*100
        if dd>mdd: mdd=dd
    return {'sl':sl*100,'tp':tp*100,'smma':sp,'wrp':wp,'trades':len(trades),
            'wr':len(wins)/len(trades)*100,'ret':ret,'mdd':mdd,
            'aw':np.mean([t for t in trades if t>0]) if wins else 0,
            'al':np.mean([t for t in trades if t<=0]) if len(wins)<len(trades) else 0}

def main():
    print("="*80)
    print("MULTI-INSTRUMENT — M5 TIMEFRAME (30 days)")
    print("="*80)
    
    results=[]
    for sym in INSTRUMENTS:
        print(f"{sym}...", end=" ", flush=True)
        df=dl(sym)
        if df is None or df.empty: print("SKIP"); continue
        best=None
        for sl,tp,sp,wp in product([0.01,0.02],[0.02,0.04,0.06],[3,5,7],[8,10,14]):
            if tp<=sl: continue
            r=opt(df,sl,tp,sp,wp)
            if r and (best is None or r['ret']>best['ret']): best=r
        if best is None: print("no trades"); continue
        best['sym']=sym; results.append(best)
        print(f"Ret={best['ret']:+.2f}% WR={best['wr']:.0f}% MDD={best['mdd']:.1f}%")
    
    if not results: print("No results!"); return
    results.sort(key=lambda x: x['ret'], reverse=True)
    
    print("\n"+"="*80)
    print("M5 RESULTS")
    print("="*80)
    print(f"{'Sym':<7} {'SL':>3} {'TP':>3} {'S':>2} {'WR':>2} {'#':>3} {'WR%':>5} {'Ret%':>7} {'MDD%':>6}")
    print("-"*80)
    for r in results:
        s="+" if r['ret']>0 else ""
        print(f"{r['sym']:<7} {r['sl']:.0f} {r['tp']:.0f} {r['smma']:>2} {r['wrp']:>2} "
              f"{r['trades']:>3} {r['wr']:>5.1f} {s}{r['ret']:>6.2f} {r['mdd']:>6.1f}")
    
    prof=[r for r in results if r['ret']>0]
    print("-"*80)
    print(f"Profitable: {len(prof)}/{len(results)} | Avg: {np.mean([r['ret'] for r in results]):.2f}%")

if __name__=="__main__":
    main()
