#!/usr/bin/env python3
"""Detailed Backtest: Moving M15 - ETH"""

import pandas as pd
import numpy as np

SL=0.03; TP=0.08; SP=7; WP=10; COMM=0.001; CAP=10000

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
            t=yf.Ticker(f); d=t.history(period="6mo", interval="1h")
            if not d.empty and len(d)>100:
                d=d.reset_index()[['Datetime','Open','High','Low','Close','Volume']]
                d.columns=['ts','o','h','l','c','v']; d['sym']=sym; return d
        except: pass
    return None

def main():
    print("="*70)
    print("DETAILED BACKTEST: Moving M15 - ETH")
    print("="*70)
    print(f"SL={SL*100}% TP={TP*100}% SMMA={SP} WR={WP}")
    
    df=dl("ETH")
    if df is None: print("Failed!"); return
    print(f"\nData: {len(df)} bars, {df['ts'].iloc[0]} to {df['ts'].iloc[-1]}")
    print(f"Price: ${df['c'].min():.2f} - ${df['c'].max():.2f}")
    
    df['smma']=smma(df['c'],SP); df['smma_s']=smma(df['c'],SP).shift(SP)
    df['wr']=williams(df['h'],df['l'],df['c'],WP)
    df['wr8']=smma(df['wr'].copy(),8); df['wr21']=smma(df['wr'].copy(),21)
    
    df['sig']=0; warm=max(22,SP*2+WP)
    for i in range(warm,len(df)):
        s=df['smma'].iloc[i]; ss=df['smma_s'].iloc[i]; w=df['wr'].iloc[i]; w8=df['wr8'].iloc[i]; w21=df['wr21'].iloc[i]
        sp_=df['smma'].iloc[i-1]; ssp=df['smma_s'].iloc[i-1]; wp_=df['wr'].iloc[i-1]; w8p=df['wr8'].iloc[i-1]
        if s>ss and sp_<=ssp and w>w8 and wp_<=w8p and w>w21: df.loc[df.index[i],'sig']=1
        elif s<ss and sp_>=ssp and w<w8 and wp_>=w8p and w<w21: df.loc[df.index[i],'sig']=-1
    
    print(f"Signals: {int(df['sig'].abs().sum())}")
    
    cap=CAP; pos=0; ent=0; ent_t=None
    trades=[]; dirs=[]; types=[]; entries=[]; exits=[]; pnl_pcts=[]; et_list=[]; xt_list=[]
    eq=[CAP]; eq_t=[df['ts'].iloc[0]]
    
    for i in range(1,len(df)):
        p=df['c'].iloc[i]; hi=df['h'].iloc[i]; lo=df['l'].iloc[i]; sg=df['sig'].iloc[i]; ts=df['ts'].iloc[i]
        
        if pos==1:
            slp=ent*(1-SL); tpp=ent*(1+TP)
            if lo<=slp:
                pnl=((slp-ent)/ent-COMM*2)*100; cap+=((slp-ent)/ent-COMM*2)*cap
                trades.append(pnl); dirs.append('LONG'); types.append('SL'); entries.append(ent); exits.append(slp); pnl_pcts.append(pnl); et_list.append(ent_t); xt_list.append(ts)
                pos=0; eq.append(cap); eq_t.append(ts); continue
            elif hi>=tpp:
                pnl=((tpp-ent)/ent-COMM*2)*100; cap+=((tpp-ent)/ent-COMM*2)*cap
                trades.append(pnl); dirs.append('LONG'); types.append('TP'); entries.append(ent); exits.append(tpp); pnl_pcts.append(pnl); et_list.append(ent_t); xt_list.append(ts)
                pos=0; eq.append(cap); eq_t.append(ts); continue
        elif pos==-1:
            slp=ent*(1+SL); tpp=ent*(1-TP)
            if hi>=slp:
                pnl=((ent-slp)/ent-COMM*2)*100; cap+=((ent-slp)/ent-COMM*2)*cap
                trades.append(pnl); dirs.append('SHORT'); types.append('SL'); entries.append(ent); exits.append(slp); pnl_pcts.append(pnl); et_list.append(ent_t); xt_list.append(ts)
                pos=0; eq.append(cap); eq_t.append(ts); continue
            elif lo<=tpp:
                pnl=((ent-tpp)/ent-COMM*2)*100; cap+=((ent-tpp)/ent-COMM*2)*cap
                trades.append(pnl); dirs.append('SHORT'); types.append('TP'); entries.append(ent); exits.append(tpp); pnl_pcts.append(pnl); et_list.append(ent_t); xt_list.append(ts)
                pos=0; eq.append(cap); eq_t.append(ts); continue
        
        if sg!=0:
            if pos==1 and sg==-1:
                pnl=((p-ent)/ent-COMM*2)*100; cap+=((p-ent)/ent-COMM*2)*cap
                trades.append(pnl); dirs.append('LONG'); types.append('EXIT'); entries.append(ent); exits.append(p); pnl_pcts.append(pnl); et_list.append(ent_t); xt_list.append(ts); pos=0
            elif pos==-1 and sg==1:
                pnl=((ent-p)/ent-COMM*2)*100; cap+=((ent-p)/ent-COMM*2)*cap
                trades.append(pnl); dirs.append('SHORT'); types.append('EXIT'); entries.append(ent); exits.append(p); pnl_pcts.append(pnl); et_list.append(ent_t); xt_list.append(ts); pos=0
            if pos==0: pos=sg; ent=p; ent_t=ts
        eq.append(cap); eq_t.append(ts)
    
    if pos!=0:
        p=df['c'].iloc[-1]
        pnl=((p-ent)/ent-COMM*2)*100 if pos==1 else ((ent-p)/ent-COMM*2)*100
        cap+=(pnl/100)*cap
        trades.append(pnl); dirs.append('LONG' if pos==1 else 'SHORT'); types.append('END')
        entries.append(ent); exits.append(p); pnl_pcts.append(pnl); et_list.append(ent_t); xt_list.append(df['ts'].iloc[-1])
        eq.append(cap); eq_t.append(df['ts'].iloc[-1])
    
    wins=[t for t in trades if t>0]; losses=[t for t in trades if t<=0]
    total_ret=(cap-CAP)/CAP*100
    gp=sum(wins) if wins else 0; gl=abs(sum(losses)) if losses else 0
    pf=gp/gl if gl>0 else float('inf')
    peak=eq[0]; mdd=0
    for v in eq:
        if v>peak: peak=v
        dd=(peak-v)/peak*100
        if dd>mdd: mdd=dd
    rets=[(eq[i]-eq[i-1])/eq[i-1] for i in range(1,len(eq))]
    sharpe=(np.mean(rets)/np.std(rets))*np.sqrt(252*24) if rets and np.std(rets)>0 else 0
    hold=[(xt-et).total_seconds()/3600 for et,xt in zip(et_list,xt_list) if et and xt]
    avg_hold=np.mean(hold) if hold else 0
    
    print("\n"+"="*70)
    print("RESULTS")
    print("="*70)
    print(f"Initial:             ${CAP:,.2f}")
    print(f"Final:               ${cap:,.2f}")
    print(f"Return:              {total_ret:.2f}%")
    print(f"Trades:              {len(trades)}")
    print(f"Wins/Losses:         {len(wins)}/{len(losses)}")
    print(f"Win Rate:            {len(wins)/len(trades)*100:.1f}%")
    print(f"Profit Factor:       {pf:.2f}")
    print(f"Max Drawdown:        {mdd:.1f}%")
    print(f"Sharpe:              {sharpe:.2f}")
    if wins: print(f"Avg Win:             {np.mean(wins):.2f}%")
    if losses: print(f"Avg Loss:            {np.mean(losses):.2f}%")
    print(f"SL:{types.count('SL')} TP:{types.count('TP')} EXIT:{types.count('EXIT')}")
    print(f"Avg Holding:         {avg_hold:.1f}h")
    print("="*70)
    
    print(f"\n{'Time':<22} {'Dir':<7} {'Type':<6} {'Entry':>10} {'Exit':>10} {'PnL%':>8}")
    print("-"*70)
    for i in range(len(trades)):
        et=str(et_list[i])[:19] if et_list[i] else "?"
        s="+" if pnl_pcts[i]>0 else ""
        print(f"{et:<22} {dirs[i]:<7} {types[i]:<6} ${entries[i]:>9.2f} ${exits[i]:>9.2f} {s}{pnl_pcts[i]:.2f}%")
    
    print("\nMONTHLY:")
    tdf=pd.DataFrame({'ts':et_list,'pnl':trades})
    tdf['month']=pd.to_datetime(tdf['ts']).dt.to_period('M')
    for m,g in tdf.groupby('month'):
        w=len(g[g['pnl']>0]); t=len(g); r=sum(g['pnl'])/CAP*100
        print(f"  {m}: {t} trades, {w} wins ({w/t*100:.0f}%), {r:+.2f}%")

if __name__=="__main__":
    main()
