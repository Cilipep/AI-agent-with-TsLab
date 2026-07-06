#!/usr/bin/env python3
"""
Multi-Instrument Backtest: Moving M15 Strategy
Test on high-volatility crypto pairs
"""

import pandas as pd
import numpy as np

# Parameters
SL_PCT = 0.03; TP_PCT = 0.06; SMMA_P = 7; WR_P = 10; COMMISSION = 0.001; CAPITAL = 10000

INSTRUMENTS = [
    "SOL", "AVAX", "LINK", "MATIC", "PEPE", "WIF", "BONK", "FET", "RNDR", "INJ"
]

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

def backtest(df, sym):
    c = df['c']; h = df['h']; l = df['l']
    df['s'] = smma(c, SMMA_P); df['ss'] = smma(c, SMMA_P).shift(SMMA_P)
    df['w'] = wr(h, l, c, WR_P); df['w8'] = smma(df['w'].copy(), 8); df['w21'] = smma(df['w'].copy(), 21)
    df['sig'] = 0; warmup = max(22, SMMA_P*2+WR_P)
    
    for i in range(warmup, len(df)):
        s5=df['s'].iloc[i]; s5s=df['ss'].iloc[i]; w=df['w'].iloc[i]; w8=df['w8'].iloc[i]; w21=df['w21'].iloc[i]
        s5p=df['s'].iloc[i-1]; s5sp=df['ss'].iloc[i-1]; wp=df['w'].iloc[i-1]; w8p=df['w8'].iloc[i-1]
        if s5>s5s and s5p<=s5sp and w>w8 and wp<=w8p and w>w21: df.loc[df.index[i],'sig']=1
        elif s5<s5s and s5p>=s5sp and w<w8 and wp>=w8p and w<w21: df.loc[df.index[i],'sig']=-1
    
    cap=CAPITAL; pos=0; entry=0; trades=[]; eq=[CAPITAL]
    
    for i in range(1, len(df)):
        p=df['c'].iloc[i]; hi=df['h'].iloc[i]; lo=df['l'].iloc[i]; sig=df['sig'].iloc[i]
        if pos==1:
            sl=entry*(1-SL_PCT); tp=entry*(1+TP_PCT)
            if lo<=sl: pnl_pct=((sl-entry)/entry-COMMISSION*2)*100; cap+=((sl-entry)/entry-COMMISSION*2)*cap; trades.append(pnl_pct); pos=0; eq.append(cap); continue
            elif hi>=tp: pnl_pct=((tp-entry)/entry-COMMISSION*2)*100; cap+=((tp-entry)/entry-COMMISSION*2)*cap; trades.append(pnl_pct); pos=0; eq.append(cap); continue
        elif pos==-1:
            sl=entry*(1+SL_PCT); tp=entry*(1-TP_PCT)
            if hi>=sl: pnl_pct=((entry-sl)/entry-COMMISSION*2)*100; cap+=((entry-sl)/entry-COMMISSION*2)*cap; trades.append(pnl_pct); pos=0; eq.append(cap); continue
            elif lo<=tp: pnl_pct=((entry-tp)/entry-COMMISSION*2)*100; cap+=((entry-tp)/entry-COMMISSION*2)*cap; trades.append(pnl_pct); pos=0; eq.append(cap); continue
        if sig!=0:
            if pos==1 and sig==-1:
                pnl_pct=((p-entry)/entry-COMMISSION*2)*100; cap+=((p-entry)/entry-COMMISSION*2)*cap; trades.append(pnl_pct); pos=0
            elif pos==-1 and sig==1:
                pnl_pct=((entry-p)/entry-COMMISSION*2)*100; cap+=((entry-p)/entry-COMMISSION*2)*cap; trades.append(pnl_pct); pos=0
            if pos==0: pos=sig; entry=p
        eq.append(cap)
    
    if pos!=0:
        p=df['c'].iloc[-1]
        pnl_pct=((p-entry)/entry-COMMISSION*2)*100 if pos==1 else ((entry-p)/entry-COMMISSION*2)*100
        cap+=(pnl_pct/100)*cap; eq.append(cap)
    
    if len(trades)<3: return None
    wins=[t for t in trades if t>0]
    ret=(cap-CAPITAL)/CAPITAL*100
    peak=eq[0]; mdd=0
    for v in eq:
        if v>peak: peak=v
        dd=(peak-v)/peak*100
        if dd>mdd: mdd=dd
    
    return {
        'symbol': sym, 'trades': len(trades), 'wins': len(wins),
        'win_rate': len(wins)/len(trades)*100, 'return': ret,
        'max_dd': mdd, 'final': cap,
        'avg_win': np.mean([t for t in trades if t>0]) if wins else 0,
        'avg_loss': np.mean([t for t in trades if t<=0]) if len(wins)<len(trades) else 0,
    }

def main():
    print("=" * 80)
    print("MULTI-INSTRUMENT BACKTEST: Moving M15 Strategy")
    print("=" * 80)
    print(f"Parameters: SL={SL_PCT*100}% TP={TP_PCT*100}% SMMA={SMMA_P} WR={WR_P}")
    print(f"Instruments: {', '.join(INSTRUMENTS)}")
    print("-" * 80)
    
    results = []
    
    for sym in INSTRUMENTS:
        print(f"\n{sym}...", end=" ")
        df = download(sym)
        if df is None or df.empty:
            print("SKIP (no data)")
            continue
        
        r = backtest(df, sym)
        if r is None:
            print("SKIP (no trades)")
            continue
        
        results.append(r)
        sign = "+" if r['return'] > 0 else ""
        print(f"Trades={r['trades']} WinRate={r['win_rate']:.0f}% Return={sign}{r['return']:.2f}% MDD={r['max_dd']:.1f}%")
    
    if not results:
        print("\nNo valid results!")
        return
    
    results.sort(key=lambda x: x['return'], reverse=True)
    
    print("\n" + "=" * 80)
    print("SUMMARY (sorted by return)")
    print("=" * 80)
    print(f"{'Symbol':<8} {'Trades':>7} {'WinR%':>6} {'Return%':>8} {'MDD%':>6} {'Final$':>10} {'AvgW%':>6} {'AvgL%':>6}")
    print("-" * 80)
    
    for r in results:
        s = "+" if r['return'] > 0 else ""
        print(f"{r['symbol']:<8} {r['trades']:>7} {r['win_rate']:>6.1f} {s}{r['return']:>7.2f} "
              f"{r['max_dd']:>6.1f} ${r['final']:>9,.2f} {r['avg_win']:>6.2f} {r['avg_loss']:>6.2f}")
    
    # Stats
    profitable = [r for r in results if r['return'] > 0]
    avg_return = np.mean([r['return'] for r in results])
    
    print("-" * 80)
    print(f"Total instruments: {len(results)}")
    print(f"Profitable: {len(profitable)} ({len(profitable)/len(results)*100:.0f}%)")
    print(f"Avg Return: {avg_return:.2f}%")
    print(f"Best: {results[0]['symbol']} ({results[0]['return']:.2f}%)")
    print(f"Worst: {results[-1]['symbol']} ({results[-1]['return']:.2f}%)")
    print("=" * 80)
    
    pd.DataFrame(results).to_csv('tmp/moving_m15_multi.csv', index=False)
    print("\nSaved to tmp/moving_m15_multi.csv")

if __name__ == "__main__":
    main()
