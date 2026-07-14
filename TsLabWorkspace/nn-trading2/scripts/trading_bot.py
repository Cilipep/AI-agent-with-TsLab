"""
Полный торговый бот с LSTM моделью и управлением рисками
"""
import torch
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os
from sklearn.preprocessing import StandardScaler
import pickle


class LSTMPredictor:
    """Предсказание на основе LSTM модели"""

    def __init__(self, model_path, scaler_path, sequence_length=60):
        self.sequence_length = sequence_length
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Загрузка модели
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

        # Загрузка скейлеров
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


class RiskManager:
    """Управление рисками"""

    def __init__(self, config):
        self.max_position_pct = config.get('max_position_pct', 0.05)
        self.max_daily_loss_pct = config.get('max_daily_loss_pct', 0.02)
        self.max_drawdown_pct = config.get('max_drawdown_pct', 0.10)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.02)
        self.take_profit_pct = config.get('take_profit_pct', 0.04)
        self.max_trades_per_day = config.get('max_trades_per_day', 10)

        self.initial_capital = config.get('capital', 1000)
        self.current_capital = self.initial_capital
        self.daily_pnl = 0
        self.max_capital = self.initial_capital
        self.trades_today = 0
        self.positions = {}

    def can_open_position(self, symbol, side, size):
        """Проверка возможности открытия позиции"""
        # Проверка дневного лимита
        if self.trades_today >= self.max_trades_per_day:
            return False, "Достигнут дневной лимит сделок"

        # Проверка дневного лимита убытков
        if self.daily_pnl < -self.max_daily_loss_pct * self.current_capital:
            return False, "Достигнут дневной лимит убытков"

        # Проверка максимального drawdown
        if self.current_capital < self.max_capital * (1 - self.max_drawdown_pct):
            return False, "Достигнут максимальный drawdown"

        # Проверка размера позиции
        max_size = self.current_capital * self.max_position_pct
        if size > max_size:
            return False, f"Размер позиции превышает максимум: {max_size:.2f}"

        return True, "OK"

    def calculate_position_size(self, price, risk_pct=0.01):
        """Расчет размера позиции"""
        risk_amount = self.current_capital * risk_pct
        stop_distance = price * self.stop_loss_pct
        size = risk_amount / stop_distance
        return min(size, self.current_capital * self.max_position_pct / price)

    def update_after_trade(self, pnl):
        """Обновление после сделки"""
        self.current_capital += pnl
        self.daily_pnl += pnl
        self.max_capital = max(self.max_capital, self.current_capital)
        self.trades_today += 1

    def get_stop_loss(self, entry_price, side):
        """Расчет стоп-лосса"""
        if side == 'long':
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)

    def get_take_profit(self, entry_price, side):
        """Расчет тейк-профита"""
        if side == 'long':
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)


class TradingBot:
    """Торговый бот"""

    def __init__(self, config):
        self.config = config
        self.predictor = LSTMPredictor(
            config['model_path'],
            config['scaler_path'],
            config.get('sequence_length', 60)
        )
        self.risk_manager = RiskManager(config)
        self.symbol = config['symbol']
        self.timeframe = config.get('timeframe', '1h')
        self.log_file = config.get('log_file', 'trading_log.json')

    def generate_signal(self, prediction, current_price):
        """Генерация торгового сигнала"""
        if prediction is None:
            return None, 0

        price_change = (prediction - current_price) / current_price

        if price_change > 0.001:  # Предсказание > 0.1% вверх
            return 'long', price_change
        elif price_change < -0.001:  # Предсказание > 0.1% вниз
            return 'short', abs(price_change)
        else:
            return None, 0

    def execute_trade(self, side, size, price):
        """Исполнение сделки (заглушка)"""
        # В реальной торговле здесь будет API вызов к Binance
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'side': side,
            'size': size,
            'price': price,
            'status': 'executed'
        }

        self.log_trade(trade)
        return trade

    def log_trade(self, trade):
        """Логирование сделки"""
        trades = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                trades = json.load(f)

        trades.append(trade)

        with open(self.log_file, 'w') as f:
            json.dump(trades, f, indent=2)

    def run(self, iterations=100):
        """Основной цикл бота"""
        print(f"=== Запуск Trading Bot ===")
        print(f"Символ: {self.symbol}")
        print(f"Таймфрейм: {self.timeframe}")
        print(f"Капитал: ${self.risk_manager.current_capital:.2f}")
        print()

        # Симуляция данных (в реальности будет API)
        for i in range(iterations):
            current_price = 50000 + np.random.randn() * 1000  # Симуляция
            volume = np.random.rand() * 1000

            ohlcv = {
                'open': current_price - np.random.rand() * 100,
                'high': current_price + np.random.rand() * 200,
                'low': current_price - np.random.rand() * 200,
                'close': current_price,
                'volume': volume
            }

            self.predictor.add_data(ohlcv)
            prediction = self.predictor.predict()

            signal, confidence = self.generate_signal(prediction, current_price)

            if signal:
                size = self.risk_manager.calculate_position_size(current_price)
                can_trade, reason = self.risk_manager.can_open_position(
                    self.symbol, signal, size * current_price
                )

                if can_trade:
                    trade = self.execute_trade(signal, size, current_price)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {signal.upper()} "
                          f"{size:.4f} @ ${current_price:.2f}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {reason}")

            time.sleep(0.1)

        print(f"\n=== Завершено ===")
        print(f"Финальный капитал: ${self.risk_manager.current_capital:.2f}")
        print(f"Доходность: {((self.risk_manager.current_capital / self.risk_manager.initial_capital) - 1) * 100:.2f}%")


def main():
    # Конфигурация
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    config = {
        'symbol': 'BTC/USDT',
        'timeframe': '1h',
        'model_path': os.path.join(base_dir, 'models', 'lstm_model.pth'),
        'scaler_path': os.path.join(base_dir, 'models', 'scalers.pkl'),
        'sequence_length': 60,
        'capital': 1000,
        'max_position_pct': 0.05,
        'max_daily_loss_pct': 0.02,
        'max_drawdown_pct': 0.10,
        'stop_loss_pct': 0.02,
        'take_profit_pct': 0.04,
        'max_trades_per_day': 10,
        'log_file': os.path.join(base_dir, 'results', 'trading_log.json')
    }

    bot = TradingBot(config)
    bot.run(iterations=50)


if __name__ == '__main__':
    main()
