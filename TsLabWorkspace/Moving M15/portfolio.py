#!/usr/bin/env python3
"""
Portfolio backtest: optimal TF + params per instrument
INJ=D1, FET=M15, DOGE=D1, LINK=H4, SOL=H1, BTC=D1, ETH=M15
"""
import pandas as pd, numpy as np, sys

def smma(s,p):
    r=s.copy(); fv=s.first_valid_index()
    if fv is None: return pd.Series(np.nan,index=s.index)
    st=s.index.get_loc(fv)
    if st+p>len(s): return pd.Series(np.nan,index=s.index)
    r.iloc[:st]=np.nan; r.iloc[st]=s.iloc[st:st+p].mean()
    for i in range(st+p,len(s)): r.iloc[i]=(r.iloc[i-1]*(p-1)+s.iloc[i])/p
    return r

def wr_calc(h,l,c,p=14):
    return -100*(h.rolling(p).max()-c)/(h.rolling(p).max()-l.rolling(p).min())

def fetch(sym, interval, period):
    import yfinance as yf
    for f in [f"{sym}-USD",f"{sym}USD"]:
        try:
            t=yf.Ticker(f); d=t.history(period=period,interval=interval)
            if d.empty: continue
            d=d.reset_index()[['Datetime','Open','High','Low','Close','Volume']]
            d.columns=['ts','o','h','l','c','v']; d['sym']=sym; return d
        except: pass
    return None

def resample(df, rule):
    d=df.copy(); d['ts']=pd.to_datetime(d['ts']); d.set_index('ts',inplace=True)
    d=d.resample(rule).agg({'o':'first','h':'max','l':'min','c':'last','v':'sum'}).dropna()
    return d.reset_index()

def run(df, sl, tp, sp, wp):
    c=df['c']; h=df['h']; l=df['l']
    df['s']=smma(c,sp); df['ss']=smma(c,sp).shift(sp)
    df['w']=wr_calc(h,l,c,wp); df['w8']=smma(df['w'].copy(),8); df['w21']=smma(df['w'].copy(),21)
    df['sig']=0; warm=max(22,sp*2+wp)
    for i in range(warm,len(df)):
        s5=df['s'].iloc[i]; s5s=df['ss'].iloc[i]; w=df['w'].iloc[i]; w8=df['w8'].iloc[i]; w21=df['w21'].iloc[i]
        s5p=df['s'].iloc[i-1]; s5sp=df['ss'].iloc[i-1]; wp_=df['w'].iloc[i-1]; w8p=df['w8'].iloc[i-1]
        if s5>s5s and s5p<=s5sp and w>w8 and wp_<=w8p and w>w21: df.loc[df.index[i],'sig']=1
        elif s5<s5s and s5p>=s5sp and w<w8 and wp_>=w8p and w<w21: df.loc[df.index[i],'sig']=-1
    cap=10000; pos=0; ent=0; trades=[]; eq=[10000]; eq_t=[df['ts'].iloc[0]]
    for i in range(1,len(df)):
        p=df['c'].iloc[i]; hi=df['h'].iloc[i]; lo=df['l'].iloc[i]; sg=df['sig'].iloc[i]; ts=df['ts'].iloc[i]
        if pos==1:
            slp=ent*(1-sl); tpp=ent*(1+tp)
            if lo<=slp: pnl=((slp-ent)/ent-0.002); cap+=pnl*cap; trades.append(pnl*100); pos=0; eq.append(cap); eq_t.append(ts); continue
            elif hi>=tpp: pnl=((tpp-ent)/ent-0.002); cap+=pnl*cap; trades.append(pnl*100); pos=0; eq.append(cap); eq_t.append(ts); continue
        elif pos==-1:
            slp=ent*(1+sl); tpp=ent*(1-tp)
            if hi>=slp: pnl=((ent-slp)/ent-0.002); cap+=pnl*cap; trades.append(pnl*100); pos=0; eq.append(cap); eq_t.append(ts); continue
            elif lo<=tpp: pnl=((ent-tpp)/ent-0.002); cap+=pnl*cap; trades.append(pnl*100); pos=0; eq.append(cap); eq_t.append(ts); continue
        if sg!=0:
            if pos==1 and sg==-1: pnl=((p-ent)/ent-0.002); cap+=pnl*cap; trades.append(pnl*100); pos=0
            elif pos==-1 and sg==1: pnl=((ent-p)/ent-0.002); cap+=pnl*cap; trades.append(pnl*100); pos=0
            if pos==0: pos=sg; ent=p
        eq.append(cap); eq_t.append(ts)
    if pos!=0:
        p=df['c'].iloc[-1]; pnl=((p-ent)/ent-0.002) if pos==1 else ((ent-p)/ent-0.002)
        cap+=pnl*cap; trades.append(pnl*100); eq.append(cap); eq_t.append(df['ts'].iloc[-1])
    if len(trades)<1: return None
    wins=[t for t in trades if t>0]; losses=[t for t in trades if t<=0]
    ret=(cap-10000)/100
    peak=eq[0]; mdd=0
    for v in eq:
        if v>peak: peak=v
        dd=(peak-v)/peak*100
        if dd>mdd: mdd=dd
    gp=sum(wins) if wins else 0; gl=abs(sum(losses)) if losses else 0.001
    return {
        'final':cap,'ret':ret,'trades':len(trades),'wins':len(wins),
        'wr':len(wins)/len(trades)*100 if trades else 0,
        'pf':gp/gl,'mdd':mdd,
        'aw':np.mean(wins) if wins else 0,
        'al':np.mean(losses) if losses else 0
    }

# Portfolio configuration
CFG = [
    {'sym':'INJ',  'tf':'1d',  'period':'2y', 'sl':0.08,'tp':0.15,'sp':7,'wp':14},
    {'sym':'FET',  'tf':'15m', 'period':'60d','sl':0.02,'tp':0.08,'sp':7,'wp':10},
    {'sym':'DOGE', 'tf':'1d',  'period':'2y', 'sl':0.05,'tp':0.10,'sp':5,'wp':10},
    {'sym':'LINK', 'tf':'4h',  'period':'6mo','sl':0.03,'tp':0.06,'sp':5,'wp':10},
    {'sym':'SOL',  'tf':'1h',  'period':'6mo','sl':0.03,'tp':0.08,'sp':7,'wp':10},
    {'sym':'BTC',  'tf':'1d',  'period':'2y', 'sl':0.05,'tp':0.10,'sp':5,'wp':10},
    {'sym':'ETH',  'tf':'15m', 'period':'60d','sl':0.03,'tp':0.08,'sp':7,'wp':10},
]

print("="*80)
print("PORTFOLIO: Optimal strategy per instrument")
print("="*80)
print(f"{'Sym':<6} {'TF':<4} {'SL%':>4} {'TP%':>4} {'#':>3} {'WR%':>5} {'Ret%':>7} {'PF':>5} {'MDD%':>6} {'Final$':>10}")
print("-"*80)

portfolio_returns = []
portfolio_final = 0
INITIAL_PER_POS = 10000

for c in CFG:
    sys.stdout.write(f"{c['sym']:<6} {c['tf']:<4}... "); sys.stdout.flush()
    raw = fetch(c['sym'], c['tf'], c['period'])
    if raw is None or raw.empty: print("SKIP"); continue
    
    # Resample if needed
    if c['tf'] == '4h': raw = resample(raw, '4h')
    elif c['tf'] == '1d': raw = resample(raw, 'D')
    
    if len(raw) < 50: print(f"too short ({len(raw)})"); continue
    
    r = run(raw.copy(), c['sl'], c['tp'], c['sp'], c['wp'])
    if r is None: print("no trades"); continue
    
    r['sym'] = c['sym']; r['tf'] = c['tf']
    portfolio_returns.append(r)
    portfolio_final += r['final']
    
    print(f"{r['trades']:>3} {r['wr']:>5.1f} {r['ret']:>7.2f} {r['pf']:>5.2f} {r['mdd']:>6.1f} ${r['final']:>9,.2f}")

if portfolio_returns:
    n = len(portfolio_returns)
    total_initial = INITIAL_PER_POS * n
    
    print("="*80)
    print("PORTFOLIO SUMMARY")
    print("="*80)
    print(f"Instruments:        {n}")
    print(f"Initial per pos:    ${INITIAL_PER_POS:,}")
    print(f"Total initial:      ${total_initial:,}")
    print(f"Total final:        ${portfolio_final:,.2f}")
    print(f"Portfolio return:   {(portfolio_final-total_initial)/total_initial*100:.2f}%")
    print(f"Avg instrument:     {np.mean([r['ret'] for r in portfolio_returns]):.2f}%")
    print(f"Avg win rate:       {np.mean([r['wr'] for r in portfolio_returns]):.1f}%")
    print(f"Avg profit factor:  {np.mean([r['pf'] for r in portfolio_returns]):.2f}")
    print(f"Total trades:       {sum(r['trades'] for r in portfolio_returns)}")
    worst = min(portfolio_returns, key=lambda x: x['ret'])
    best = max(portfolio_returns, key=lambda x: x['ret'])
    print(f"Best performer:     {best['sym']} ({best['ret']:+.2f}%)")
    print(f"Worst performer:    {worst['sym']} ({worst['ret']:+.2f}%)")
    print("="*80)
    
    pd.DataFrame(portfolio_returns).to_csv('tmp/moving_m15_portfolio.csv', index=False)
    print("Saved to tmp/moving_m15_portfolio.csv")
