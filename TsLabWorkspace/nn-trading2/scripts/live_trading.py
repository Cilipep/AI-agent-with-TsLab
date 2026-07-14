"""
Живая торговля на Binance Testnet
"""
import ccxt
import torch
import numpy as np
import pandas as pd
import time
import os
import json
from datetime import datetime
import pickle
from config import get_config, is_testnet


class LSTMPredictor:
    """Предсказание на основе LSTM модели"""

    def __init__(self, model_path, scaler_path, sequence_length=60):
        self.sequence_length = sequence_length
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
        self.input_size = checkpoint['input_size']
        self.hidden_size = checkpoint['hidden_size']
        self.num_layers = checkpoint['num_layers']

        from train_lstm import LSTMModel
        self.model = LSTMModel(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            output_size=1
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        with open(scaler_path, 'rb') as f:
            scalers = pickle.load(f)
            self.scaler_X = scalers['scaler_X']
            self.scaler_y = scalers['scaler_y']

        self.data_buffer = []

    def add_data(self, ohlcv):
        """Добавление новых данных"""
        self.data_buffer.append(ohlcv)
        if len(self.data_buffer) > self.sequence_length:
            self.data_buffer.pop(0)

    def predict(self):
        """Предсказание"""
        if len(self.data_buffer) < self.sequence_length:
            return None

        df = pd.DataFrame(self.data_buffer)
        features = self._compute_features(df)

        X = features.values[-self.sequence_length:]
        X_scaled = self.scaler_X.transform(X)
        X_tensor = torch.FloatTensor(X_scaled).unsqueeze(0).to(self.device)

        with torch.no_grad():
            prediction = self.model(X_tensor).cpu().item()

        prediction = self.scaler_y.inverse_transform([[prediction]])[0][0]
        return prediction

    def _compute_features(self, df):
        """Вычисление признаков"""
        df = df.copy()

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

        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + 2 * bb_std
        df['bb_lower'] = df['bb_middle'] - 2 * bb_std
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

        # EMA
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()

        # Volume
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']

        # Volatility
        df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()

        features = ['close', 'volume', 'rsi', 'macd', 'macd_signal',
                    'bb_width', 'ema_9', 'ema_21', 'volume_ratio', 'volatility']

        return df[features].dropna()


class LiveTrader:
    """Живой трейдер"""

    def __init__(self, config):
        self.config = config
        self.setup_exchange()
        self.setup_model()
        self.position = None
        self.trades = []

    def setup_exchange(self):
        """Настройка биржи"""
        if is_demo():
            # Demo Trading
            self.exchange = ccxt.binance({
                'apiKey': self.config['api_key'],
                'secret': self.config['api_secret'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                },
                'urls': {
                    'api': {
                        'public': 'https://demo.binance.com/api/v3',
                        'private': 'https://demo.binance.com/api/v3',
                    }
                }
            })
            print("✅ Подключено к Binance Demo Trading")
        elif is_testnet():
            # Testnet
            self.exchange = ccxt.binance({
                'apiKey': self.config['api_key'],
                'secret': self.config['api_secret'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'testMode': True
                }
            })
            print("✅ Подключено к Binance Testnet")
        else:
            # Реальная биржа
            self.exchange = ccxt.binance({
                'apiKey': self.config['api_key'],
                'secret': self.config['api_secret'],
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            print("⚠️  Подключено к Binance PRODUCTION")

    def setup_model(self):
        """Настройка модели"""
        base_dir = self.config['base_dir']
        model_path = base_dir / 'models' / 'lstm_model.pth'
        scaler_path = base_dir / 'models' / 'scalers.pkl'

        if not model_path.exists():
            print(f"❌ Модель не найдена: {model_path}")
            return

        self.predictor = LSTMPredictor(str(model_path), str(scaler_path))
        print(f"✅ Модель загружена")

    def get_balance(self):
        """Получение баланса"""
        try:
            balance = self.exchange.fetch_balance()
            usdt = float(balance.get('USDT', {}).get('free', 0))
            btc = float(balance.get('BTC', {}).get('free', 0))
            print(f"💰 Баланс: {usdt:.2f} USDT | {btc:.6f} BTC")
            return {'USDT': usdt, 'BTC': btc}
        except Exception as e:
            print(f"❌ Ошибка баланса: {e}")
            return None

    def get_ticker(self):
        """Получение текущей цены"""
        try:
            ticker = self.exchange.fetch_ticker(self.config['symbol'])
            return float(ticker['last'])
        except Exception as e:
            print(f"❌ Ошибка тикера: {e}")
            return None

    def load_historical_data(self, limit=100):
        """Загрузка исторических данных"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                self.config['symbol'],
                self.config['timeframe'],
                limit=limit
            )
            for candle in ohlcv:
                self.predictor.add_data({
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            print(f"✅ Загружено {len(ohlcv)} свечей")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            return False

    def generate_signal(self, prediction, current_price):
        """Генерация сигнала"""
        if prediction is None:
            return None

        price_change = (prediction - current_price) / current_price

        if price_change > 0.002:
            return 'long'
        elif price_change < -0.002:
            return 'short'
        return None

    def calculate_position_size(self, price):
        """Расчет размера позиции"""
        balance = self.get_balance()
        if not balance:
            return 0

        position_value = balance['USDT'] * self.config['max_position_pct']
        size = position_value / price
        return size

    def open_position(self, side, price):
        """Открытие позиции"""
        size = self.calculate_position_size(price)
        if size <= 0:
            return None

        try:
            if side == 'long':
                order = self.exchange.create_market_order(
                    self.config['symbol'], 'buy', size
                )
            else:
                order = self.exchange.create_market_order(
                    self.config['symbol'], 'sell', size
                )

            self.position = {
                'side': side,
                'entry_price': price,
                'size': size,
                'order_id': order['id']
            }

            print(f"📈 Открыта позиция: {side.upper()} {size:.6f} @ ${price:.2f}")
            return order

        except Exception as e:
            print(f"❌ Ошибка открытия позиции: {e}")
            return None

    def close_position(self, price):
        """Закрытие позиции"""
        if not self.position:
            return None

        try:
            side = 'sell' if self.position['side'] == 'long' else 'buy'
            order = self.exchange.create_market_order(
                self.config['symbol'], side, self.position['size']
            )

            pnl = 0
            if self.position['side'] == 'long':
                pnl = (price - self.position['entry_price']) * self.position['size']
            else:
                pnl = (self.position['entry_price'] - price) * self.position['size']

            self.trades.append({
                'side': self.position['side'],
                'entry_price': self.position['entry_price'],
                'exit_price': price,
                'size': self.position['size'],
                'pnl': pnl,
                'timestamp': datetime.now().isoformat()
            })

            print(f"📉 Закрыта позиция: PnL ${pnl:.2f}")
            self.position = None
            return order

        except Exception as e:
            print(f"❌ Ошибка закрытия позиции: {e}")
            return None

    def run(self, iterations=100):
        """Основной цикл"""
        print("\n" + "=" * 50)
        print("🚀 ЗАПУСК ЖИВОЙ ТОРГОВЛИ")
        print("=" * 50)
        print(f"Символ: {self.config['symbol']}")
        print(f"Таймфрейм: {self.config['timeframe']}")
        print(f"Режим: {'Testnet' if is_testnet() else 'PRODUCTION'}")
        print("=" * 50 + "\n")

        # Загрузка исторических данных
        if not self.load_historical_data(100):
            print("❌ Не удалось загрузить данные")
            return

        self.get_balance()

        for i in range(iterations):
            try:
                current_price = self.get_ticker()
                if not current_price:
                    continue

                # Добавление данных
                ticker = self.exchange.fetch_ticker(self.config['symbol'])
                self.predictor.add_data({
                    'open': float(ticker.get('open', current_price)),
                    'high': float(ticker.get('high', current_price)),
                    'low': float(ticker.get('low', current_price)),
                    'close': current_price,
                    'volume': float(ticker.get('baseVolume', 0))
                })

                # Предсказание
                prediction = self.predictor.predict()
                signal = self.generate_signal(prediction, current_price)

                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Цена: ${current_price:,.2f} | "
                      f"Предсказание: ${prediction:,.2f if prediction else 'N/A'} | "
                      f"Сигнал: {signal or 'NONE'}")

                # Торговля
                if signal and not self.position:
                    self.open_position(signal, current_price)
                elif not signal and self.position:
                    self.close_position(current_price)

                time.sleep(10)  # Ждем 10 секунд

            except KeyboardInterrupt:
                print("\n⚠️  Остановка по Ctrl+C")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                time.sleep(5)

        # Закрытие позиции при завершении
        if self.position:
            price = self.get_ticker()
            if price:
                self.close_position(price)

        print("\n" + "=" * 50)
        print("📊 ИТОГИ")
        print("=" * 50)
        print(f"Количество сделок: {len(self.trades)}")
        if self.trades:
            total_pnl = sum(t['pnl'] for t in self.trades)
            print(f"Общий PnL: ${total_pnl:.2f}")
        print("=" * 50)


def main():
    config = get_config()

    if not config['api_key'] or config['api_key'] == 'your_api_key_here':
        print("❌ API ключи не установлены!")
        print("Отредактируйте файл .env в корне проекта")
        return

    trader = LiveTrader(config)
    trader.run(iterations=50)


if __name__ == '__main__':
    main()
