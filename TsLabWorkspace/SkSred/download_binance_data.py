import pandas as pd
import requests
import time
import os

# List of instruments to download
INSTRUMENTS = [
    'AAVEUSDT', 'ADAUSDT', 'APEUSDT', 'AVAXUSDT', 'BCHUSDT',
    'BNBUSDT', 'BTCUSDT', 'DOGEUSDT', 'DOTUSDT', 'ETCUSDT',
    'ETHUSDT', 'FILUSDT', 'GALAUSDT', 'ICXUSDT', 'KNCUSDT',
    'LINKUSDT', 'LTCUSDT', 'NEARUSDT', 'ROSEUSDT', 'SOLUSDT',
    'SUIUSDT', 'TRXUSDT', 'UNIUSDT', 'VETUSDT', 'XLMUSDT',
    'XRPUSDT', 'XTZUSDT', 'ZILUSDT'
]

# Map to perpetual contract names
PERP_MAP = {s: s.replace('USDT', 'USD_PERP') for s in INSTRUMENTS}

def get_klines(symbol, interval, days=60):
    """Download klines from Binance API"""
    url = 'https://fapi.binance.com/fapi/v1/klines'
    
    end_time = int(time.time() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    all_klines = []
    current_start = start_time
    
    while current_start < end_time:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': current_start,
            'limit': 1500
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if not data:
                break
                
            all_klines.extend(data)
            current_start = data[-1][0] + 1
            
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"  Error downloading {symbol} {interval}: {e}")
            time.sleep(1)
            continue
    
    return all_klines

def klines_to_df(klines, symbol):
    """Convert klines to DataFrame"""
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'
    ])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['symbol'] = PERP_MAP.get(symbol, symbol)
    
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    
    df = df[['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
    
    return df

def download_and_save(interval, output_name):
    """Download data for all instruments and save to CSV"""
    output_path = rf"C:\Users\i59400f\Desktop\ai-agent\tmp\market_data\ALL_INSTRUMENTS_{output_name}_60d.csv"
    
    print(f"\n{'='*60}")
    print(f"Downloading {output_name} data for {len(INSTRUMENTS)} instruments...")
    print(f"{'='*60}\n")
    
    all_data = []
    
    for i, symbol in enumerate(INSTRUMENTS, 1):
        print(f"[{i:2d}/{len(INSTRUMENTS)}] Downloading {symbol} {interval}...", end=" ")
        
        klines = get_klines(symbol, interval, days=60)
        
        if klines:
            df = klines_to_df(klines, symbol)
            all_data.append(df)
            print(f"OK ({len(df)} bars)")
        else:
            print("FAILED (no data)")
    
    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)
        df_all = df_all.sort_values(['symbol', 'timestamp']).reset_index(drop=True)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_all.to_csv(output_path, index=False)
        
        print(f"\nSaved {len(df_all)} total bars to {output_path}")
        print(f"Instruments: {df_all['symbol'].nunique()}")
        
        # Summary per instrument
        print(f"\n{'Symbol':<16} {'Bars':>6} {'From':<12} {'To':<12}")
        print("-" * 50)
        for sym in sorted(df_all['symbol'].unique()):
            df_sym = df_all[df_all['symbol'] == sym]
            print(f"{sym:<16} {len(df_sym):>6} {df_sym['timestamp'].min().strftime('%Y-%m-%d'):<12} {df_sym['timestamp'].max().strftime('%Y-%m-%d'):<12}")
    else:
        print("\nNo data downloaded!")
    
    return output_path

if __name__ == "__main__":
    # Download H4 data
    download_and_save('4h', 'H4')
    
    # Download D1 data
    download_and_save('1d', 'D1')
    
    print("\n\nDone!")
