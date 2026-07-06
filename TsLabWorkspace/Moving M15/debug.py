#!/usr/bin/env python3
"""
Backtest: Moving M15 Strategy (debug version)
"""

import pandas as pd
import numpy as np

# =================== PARAMETERS ===================
SYMBOL = "GBPUSD"
TIMEFRAME = "M15"
INITIAL_CAPITAL = 10000
COMMISSION_PCT = 0.0002
SL_PCT = 0.003
TP_PCT = 0.006

# =================== INDICATORS ===================
def smma(series, period):
    """Smoothed Moving Average (SMMA)"""
    result = series.copy()
    result.iloc[:period] = np.nan
    result.iloc[period - 1] = series.iloc[:period].mean()
    for i in range(period, len(series)):
        result.iloc[i] = (result.iloc[i - 1] * (period - 1) + series.iloc[i]) / period
    return result

def williams_r(high, low, close, period=14):
    """Williams %R indicator"""
    hh = high.rolling(window=period).max()
    ll = low.rolling(window=period).min()
    wr = -100 * (hh - close) / (hh - ll)
    return wr

def weighted_close(high, low, close):
    """Weighted Close = (H + L + C*2) / 4"""
    return (high + low + close * 2) / 4

# =================== DATA DOWNLOAD ===================
def download_data(symbol, timeframe):
    """Download M15 data from yfinance"""
    try:
        import yfinance as yf
        
        yf_symbol = f"{symbol}=X"
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="60d", interval="15m")
        
        if df.empty:
            print(f"yfinance returned empty data for {yf_symbol}")
            return None
        
        df = df.reset_index()
        # yfinance returns datetime with timezone, keep it simple
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df['symbol'] = symbol
        
        print(f"Downloaded {len(df)} M15 bars for {symbol}")
        return df
    except Exception as e:
        print(f"Download failed: {e}")
        return None

# =================== MAIN ===================
def main():
    print("=" * 60)
    print("Moving M15 Strategy - Debug")
    print("=" * 60)
    
    # Download data
    df = download_data(SYMBOL, TIMEFRAME)
    
    if df is None or df.empty:
        print("Failed to download data!")
        return
    
    print(f"\nData range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Price range: {df['close'].min():.5f} to {df['close'].max():.5f}")
    
    # Calculate indicators
    close = df['close'].copy()
    high = df['high'].copy()
    low = df['low'].copy()
    wc = weighted_close(high, low, close)
    
    df['smma5'] = smma(close, 5)
    df['smma5_shifted'] = smma(close, 5).shift(5)
    df['wr14'] = williams_r(high, low, close, 14)
    df['smma8_w'] = smma(wc, 8)
    df['smma21_w'] = smma(wc, 21)
    
    # Debug: show indicator ranges
    print("\n--- Indicator Ranges (after warm-up) ---")
    print(f"SMMA5: {df['smma5'].dropna().min():.5f} to {df['smma5'].dropna().max():.5f}")
    print(f"SMMA5 shifted: {df['smma5_shifted'].dropna().min():.5f} to {df['smma5_shifted'].dropna().max():.5f}")
    print(f"Williams %R: {df['wr14'].dropna().min():.1f} to {df['wr14'].dropna().max():.1f}")
    print(f"SMMA8 W: {df['smma8_w'].dropna().min():.5f} to {df['smma8_w'].dropna().max():.5f}")
    print(f"SMMA21 W: {df['smma21_w'].dropna().min():.5f} to {df['smma21_w'].dropna().max():.5f}")
    
    # Count crossovers
    valid = df.dropna(subset=['smma5', 'smma5_shifted', 'wr14', 'smma8_w', 'smma21_w'])
    
    # MA crossovers (strict: line must cross)
    ma_cross_up = ((valid['smma5'] > valid['smma5_shifted']) & 
                   (valid['smma5'].shift(1) <= valid['smma5_shifted'].shift(1))).sum()
    ma_cross_down = ((valid['smma5'] < valid['smma5_shifted']) & 
                     (valid['smma5'].shift(1) >= valid['smma5_shifted'].shift(1))).sum()
    
    # Williams crossovers
    wr_cross_up = ((valid['wr14'] > valid['smma8_w']) & 
                   (valid['wr14'].shift(1) <= valid['smma8_w'].shift(1))).sum()
    wr_cross_down = ((valid['wr14'] < valid['smma8_w']) & 
                     (valid['wr14'].shift(1) >= valid['smma8_w'].shift(1))).sum()
    
    # Filter conditions
    wr_above_21 = (valid['wr14'] > valid['smma21_w']).sum()
    wr_below_21 = (valid['wr14'] < valid['smma21_w']).sum()
    
    print(f"\n--- Signal Components ---")
    print(f"MA crossover UP:   {ma_cross_up}")
    print(f"MA crossover DOWN: {ma_cross_down}")
    print(f"WR crossover UP:   {wr_cross_up}")
    print(f"WR crossover DOWN: {wr_cross_down}")
    print(f"WR above MA21:     {wr_above_21} ({wr_above_21/len(valid)*100:.1f}%)")
    print(f"WR below MA21:     {wr_below_21} ({wr_below_21/len(valid)*100:.1f}%)")
    
    # Combined signals (all 3 conditions must align)
    buy_signals = ((valid['smma5'] > valid['smma5_shifted']) & 
                   (valid['smma5'].shift(1) <= valid['smma5_shifted'].shift(1)) &
                   (valid['wr14'] > valid['smma8_w']) & 
                   (valid['wr14'].shift(1) <= valid['smma8_w'].shift(1)) &
                   (valid['wr14'] > valid['smma21_w'])).sum()
    
    sell_signals = ((valid['smma5'] < valid['smma5_shifted']) & 
                    (valid['smma5'].shift(1) >= valid['smma5_shifted'].shift(1)) &
                    (valid['wr14'] < valid['smma8_w']) & 
                    (valid['wr14'].shift(1) >= valid['smma8_w'].shift(1)) &
                    (valid['wr14'] < valid['smma21_w'])).sum()
    
    print(f"\nCombined BUY signals:  {buy_signals}")
    print(f"Combined SELL signals: {sell_signals}")
    
    # Try relaxed version: MA cross + Williams filter (no exact WR cross required)
    buy_relaxed = ((valid['smma5'] > valid['smma5_shifted']) & 
                   (valid['smma5'].shift(1) <= valid['smma5_shifted'].shift(1)) &
                   (valid['wr14'] > valid['smma8_w']) &
                   (valid['wr14'] > valid['smma21_w'])).sum()
    
    sell_relaxed = ((valid['smma5'] < valid['smma5_shifted']) & 
                    (valid['smma5'].shift(1) >= valid['smma5_shifted'].shift(1)) &
                    (valid['wr14'] < valid['smma8_w']) &
                    (valid['wr14'] < valid['smma21_w'])).sum()
    
    print(f"\n--- Relaxed (MA cross + WR filter) ---")
    print(f"BUY signals:  {buy_relaxed}")
    print(f"SELL signals: {sell_relaxed}")

if __name__ == "__main__":
    main()
