"""
Grid Bot — Тест подключения к тестнету Bybit
"""

import ccxt
import pandas as pd
import numpy as np

# Подключение к тестнету Bybit
print("Подключение к тестнету Bybit...")
exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'sandbox': True,
    'options': {'defaultType': 'future'}
})

# Загрузка рынков
exchange.load_markets()
print("Рынки загружены!")

# Проверка символа
symbol = 'BTC/USDT:USDT'
ticker = exchange.fetch_ticker(symbol)
print(f"Текущая цена BTC: ${ticker['last']:,.2f}")

# Получение баланса
balance = exchange.fetch_balance()
print(f"Баланс USDT: ${balance['USDT']['free']:.2f}")

# Получение исторических данных
ohlcv = exchange.fetch_ohlcv(symbol, '30m', limit=50)
print(f"Получено {len(ohlcv)} свечей")

# Расчёт ATR
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
h, l, c = df['high'], df['low'], df['close'].shift(1)
tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
df['ATR'] = tr.rolling(14).mean()
atr = df['ATR'].iloc[-1]
print(f"ATR(14): ${atr:.2f}")

# Расчёт уровней сетки
grid_mult = 2.5
stop_mult = 3.0
close = df['close'].iloc[-1]

grid_spacing = atr * grid_mult
stop_dist = atr * stop_mult

print(f"\nУровни сетки:")
print(f"  Grid Spacing: ${grid_spacing:.2f}")
print(f"  Stop Distance: ${stop_dist:.2f}")
print(f"  Long Entry: ${close - grid_spacing:.2f}")
print(f"  Short Entry: ${close + grid_spacing:.2f}")
print(f"  Long Stop: ${close - stop_dist:.2f}")
print(f"  Short Stop: ${close + stop_dist:.2f}")

print("\nПодключение к тестнету успешно!")
print("Для запуска бота: python GridBot_Final.py --testnet")
