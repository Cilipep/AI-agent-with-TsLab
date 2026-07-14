"""
Загрузка исторических данных с Binance для обучения нейросети
"""
import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta
import os


def download_ohlcv(symbol='BTC/USDT', timeframe='1h', days=365):
    """Загрузка OHLCV данных с Binance"""
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })

    since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
    all_ohlcv = []
    limit = 1000

    print(f"Загрузка {symbol} {timeframe} за {days} дней...")

    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
            if not ohlcv:
                break

            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1

            if len(ohlcv) < limit:
                break

            time.sleep(exchange.rateLimit / 1000)

        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
            continue

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.drop_duplicates(subset='timestamp').sort_values('timestamp').reset_index(drop=True)

    return df


def add_indicators(df):
    """Добавление технических индикаторов"""
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * bb_std
    df['bb_lower'] = df['bb_middle'] - 2 * bb_std
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

    # EMA
    df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # Volume indicators
    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma']

    # Price changes
    df['price_change'] = df['close'].pct_change()
    df['price_change_5'] = df['close'].pct_change(5)
    df['price_change_10'] = df['close'].pct_change(10)

    # Volatility
    df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()

    return df


def main():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    symbols = ['BTC/USDT', 'ETH/USDT']
    timeframe = '1h'
    days = 365

    for symbol in symbols:
        filename = symbol.replace('/', '_').replace(' ', '') + f'_{timeframe}.csv'
        filepath = os.path.join(data_dir, filename)

        if os.path.exists(filepath):
            print(f"{filename} уже существует, пропускаем...")
            continue

        df = download_ohlcv(symbol, timeframe, days)
        df = add_indicators(df)
        df.to_csv(filepath, index=False)
        print(f"Сохранено: {filename} ({len(df)} записей)")

    print("\nЗагрузка завершена!")


if __name__ == '__main__':
    main()
