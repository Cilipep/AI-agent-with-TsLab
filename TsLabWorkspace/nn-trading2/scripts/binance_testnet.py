"""
Подключение к тестовой сети Binance Testnet
"""
import ccxt
import time
import os
import json
from datetime import datetime


class BinanceTestnet:
    """Класс для работы с Binance Testnet"""

    def __init__(self, api_key=None, api_secret=None):
        # Binance Testnet - используем стандартный ccxt с testnet опцией
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
                'testMode': True  # Включаем testnet
            }
        })

    def get_balance(self):
        """Получение баланса"""
        try:
            balance = self.exchange.fetch_balance()
            return {
                'USDT': float(balance.get('USDT', {}).get('free', 0)),
                'BTC': float(balance.get('BTC', {}).get('free', 0)),
                'ETH': float(balance.get('ETH', {}).get('free', 0))
            }
        except Exception as e:
            print(f"Ошибка получения баланса: {e}")
            return None

    def get_ticker(self, symbol='BTC/USDT'):
        """Получение текущей цены"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': float(ticker['last']),
                'bid': float(ticker['bid']),
                'ask': float(ticker['ask']),
                'volume': float(ticker['baseVolume'])
            }
        except Exception as e:
            print(f"Ошибка получения тикера: {e}")
            return None

    def get_ohlcv(self, symbol='BTC/USDT', timeframe='1h', limit=100):
        """Получение свечей"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            print(f"Ошибка получения OHLCV: {e}")
            return None

    def create_order(self, symbol, side, amount, price=None):
        """Создание ордера"""
        try:
            if price:
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            else:
                order = self.exchange.create_market_order(symbol, side, amount)
            return order
        except Exception as e:
            print(f"Ошибка создания ордера: {e}")
            return None

    def cancel_order(self, order_id, symbol):
        """Отмена ордера"""
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            return result
        except Exception as e:
            print(f"Ошибка отмены ордера: {e}")
            return None

    def get_open_orders(self, symbol=None):
        """Получение открытых ордеров"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            print(f"Ошибка получения ордеров: {e}")
            return []


def test_connection():
    """Тест подключения к Testnet"""
    print("=== Тест подключения к Binance Testnet ===\n")

    # Используем основную сеть для публичных данных
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })

    try:
        # Тест публичных данных
        print("1. Тест получения тикера...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"   BTC/USDT: ${float(ticker['last']):,.2f}")

        # Тест получения свечей
        print("\n2. Тест получения свечей...")
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=10)
        print(f"   Получено {len(ohlcv)} свечей")
        print(f"   Последняя свеча: {ohlcv[-1]}")

        # Тест получения стакана
        print("\n3. Тест получения стакана...")
        orderbook = exchange.fetch_order_book('BTC/USDT', limit=5)
        print(f"   Bid: ${float(orderbook['bids'][0][0]):,.2f}")
        print(f"   Ask: ${float(orderbook['asks'][0][0]):,.2f}")

        print("\n✅ Подключение успешно!")
        return True

    except Exception as e:
        print(f"\n❌ Ошибка подключения: {e}")
        return False


def main():
    # Тест подключения
    test_connection()

    # Если нужны API ключи для торговли
    print("\n" + "=" * 50)
    print("Для торговли на Testnet нужны API ключи:")
    print("1. Перейдите на https://testnet.binance.vision/")
    print("2. Нажмите 'Generate HMAC_SHA256 Key'")
    print("3. Скопируйте API Key и Secret Key")
    print("4. Создайте файл .env с:")
    print("   BINANCE_API_KEY=your_key")
    print("   BINANCE_API_SECRET=your_secret")
    print("=" * 50)


if __name__ == '__main__':
    main()
