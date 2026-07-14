"""
Бэктестинг LSTM модели на исторических данных
"""
import torch
import numpy as np
import pandas as pd
import os
import json
from datetime import datetime
import pickle


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

    def predict_batch(self, X):
        """Пакетное предсказание"""
        X_scaled = self.scaler_X.transform(X)
        X_tensor = torch.FloatTensor(X_scaled).unsqueeze(0).to(self.device)

        with torch.no_grad():
            prediction = self.model(X_tensor).cpu().item()

        return self.scaler_y.inverse_transform([[prediction]])[0][0]


def compute_features(df):
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

    return df


class BacktestEngine:
    """Движок бэктестинга"""

    def __init__(self, config):
        self.config = config
        self.initial_capital = config['capital']
        self.current_capital = self.initial_capital
        self.max_capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []

        # Параметры риск-менеджмента
        self.max_position_pct = config.get('max_position_pct', 0.05)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.02)
        self.take_profit_pct = config.get('take_profit_pct', 0.04)
        self.max_trades_per_day = config.get('max_trades_per_day', 10)
        self.commission_pct = config.get('commission_pct', 0.001)

    def run_backtest(self, df, predictor, sequence_length=60):
        """Запуск бэктестинга"""
        df = compute_features(df)
        features = ['close', 'volume', 'rsi', 'macd', 'macd_signal',
                    'bb_width', 'ema_9', 'ema_21', 'volume_ratio', 'volatility']

        df_valid = df.dropna().reset_index(drop=True)

        print(f"Запуск бэктестинга на {len(df_valid)} барах...")
        print(f"Начальный капитал: ${self.initial_capital:.2f}")
        print()

        trades_count = 0
        wins = 0
        losses = 0
        total_pnl = 0

        for i in range(sequence_length, len(df_valid) - 1):
            current_bar = df_valid.iloc[i]
            next_bar = df_valid.iloc[i + 1]

            current_price = current_bar['close']
            next_price = next_bar['close']

            # Получение признаков для предсказания
            X = df_valid[features].iloc[i-sequence_length:i].values
            prediction = predictor.predict_batch(X)

            # Генерация сигнала
            price_change = (prediction - current_price) / current_price

            signal = None
            if price_change > 0.001:
                signal = 'long'
            elif price_change < -0.001:
                signal = 'short'

            # Проверка стоп-лоссов и тейк-профитов
            self._check_positions(current_price)

            # Открытие позиции
            if signal and signal not in self.positions:
                position_size = self._calculate_position_size(current_price)
                if position_size > 0:
                    self._open_position(signal, current_price, position_size)
                    trades_count += 1

            # Закрытие позиции по сигналу
            if signal and signal in self.positions:
                self._close_position(signal, current_price)
                trades_count += 1

            # Запись equity
            unrealized_pnl = 0
            if 'long' in self.positions:
                unrealized_pnl += (current_price - self.positions['long']['entry_price']) * self.positions['long']['size']
            if 'short' in self.positions:
                unrealized_pnl += (self.positions['short']['entry_price'] - current_price) * self.positions['short']['size']

            self.equity_curve.append({
                'timestamp': current_bar.get('timestamp', i),
                'equity': self.current_capital + unrealized_pnl
            })

            self.max_capital = max(self.max_capital, self.current_capital + unrealized_pnl)

        # Закрытие оставшихся позиций
        if 'long' in self.positions:
            self._close_position('long', df_valid.iloc[-1]['close'])
        if 'short' in self.positions:
            self._close_position('short', df_valid.iloc[-1]['close'])

        return self._calculate_metrics(trades_count)

    def _calculate_position_size(self, price):
        """Расчет размера позиции"""
        max_amount = self.current_capital * self.max_position_pct
        size = max_amount / price
        return size

    def _open_position(self, side, price, size):
        """Открытие позиции"""
        commission = size * price * self.commission_pct
        self.current_capital -= commission

        self.positions[side] = {
            'entry_price': price,
            'size': size,
            'entry_time': datetime.now(),
            'stop_loss': price * (1 - self.stop_loss_pct) if side == 'long' else price * (1 + self.stop_loss_pct),
            'take_profit': price * (1 + self.take_profit_pct) if side == 'long' else price * (1 - self.take_profit_pct)
        }

    def _close_position(self, side, price):
        """Закрытие позиции"""
        if side not in self.positions:
            return

        pos = self.positions[side]
        if side == 'long':
            pnl = (price - pos['entry_price']) * pos['size']
        else:
            pnl = (pos['entry_price'] - price) * pos['size']

        commission = pos['size'] * price * self.commission_pct
        pnl -= commission

        self.current_capital += pnl
        self.trades.append({
            'side': side,
            'entry_price': pos['entry_price'],
            'exit_price': price,
            'size': pos['size'],
            'pnl': pnl,
            'entry_time': pos['entry_time'],
            'exit_time': datetime.now()
        })

        del self.positions[side]

    def _check_positions(self, current_price):
        """Проверка стоп-лоссов и тейк-профитов"""
        for side in list(self.positions.keys()):
            pos = self.positions[side]
            if side == 'long':
                if current_price <= pos['stop_loss'] or current_price >= pos['take_profit']:
                    self._close_position(side, current_price)
            else:
                if current_price >= pos['stop_loss'] or current_price <= pos['take_profit']:
                    self._close_position(side, current_price)

    def _calculate_metrics(self, trades_count):
        """Расчет метрик"""
        total_return = (self.current_capital / self.initial_capital) - 1

        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]

        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0

        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t['pnl']) for t in losing_trades]) if losing_trades else 0

        profit_factor = (sum(t['pnl'] for t in winning_trades) /
                        sum(abs(t['pnl']) for t in losing_trades)) if losing_trades else float('inf')

        # Sharpe ratio
        equity_values = [e['equity'] for e in self.equity_curve]
        if len(equity_values) > 1:
            returns = np.diff(equity_values) / equity_values[:-1]
            sharpe = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(365 * 24)
        else:
            sharpe = 0

        # Max drawdown
        equity_series = pd.Series(equity_values)
        rolling_max = equity_series.cummax()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        metrics = {
            'total_return': float(total_return),
            'total_return_pct': float(total_return * 100),
            'final_capital': float(self.current_capital),
            'initial_capital': float(self.initial_capital),
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': float(win_rate),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': float(profit_factor),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_drawdown),
            'max_drawdown_pct': float(max_drawdown * 100)
        }

        return metrics


def main():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(base_dir, 'data')
    models_dir = os.path.join(base_dir, 'models')
    results_dir = os.path.join(base_dir, 'results')

    os.makedirs(results_dir, exist_ok=True)

    # Конфигурация
    config = {
        'symbol': 'BTC/USDT',
        'capital': 1000,
        'max_position_pct': 0.05,
        'stop_loss_pct': 0.02,
        'take_profit_pct': 0.04,
        'max_trades_per_day': 10,
        'commission_pct': 0.001
    }

    # Загрузка данных
    data_file = os.path.join(data_dir, 'BTC_USDT_1h.csv')
    if not os.path.exists(data_file):
        print(f"Файл данных не найден: {data_file}")
        return

    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"Загружено {len(df)} записей")

    # Загрузка модели
    model_path = os.path.join(models_dir, 'lstm_model.pth')
    scaler_path = os.path.join(models_dir, 'scalers.pkl')

    if not os.path.exists(model_path):
        print(f"Модель не найдена: {model_path}")
        return

    predictor = LSTMPredictor(model_path, scaler_path, sequence_length=60)

    # Запуск бэктестинга
    engine = BacktestEngine(config)
    metrics = engine.run_backtest(df, predictor, sequence_length=60)

    # Вывод результатов
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ БЭКТЕСТИНГА")
    print("=" * 50)
    print(f"Символ: {config['symbol']}")
    print(f"Начальный капитал: ${metrics['initial_capital']:.2f}")
    print(f"Финальный капитал: ${metrics['final_capital']:.2f}")
    print(f"Доходность: {metrics['total_return_pct']:.2f}%")
    print(f"Количество сделок: {metrics['total_trades']}")
    print(f"Выигрышные сделки: {metrics['winning_trades']}")
    print(f"Проигрышные сделки: {metrics['losing_trades']}")
    print(f"Win Rate: {metrics['win_rate']*100:.2f}%")
    print(f"Средний выигрыш: ${metrics['avg_win']:.2f}")
    print(f"Средний проигрыш: ${metrics['avg_loss']:.2f}")
    print(f"Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
    print("=" * 50)

    # Сохранение результатов
    results = {
        'config': config,
        'metrics': metrics,
        'trades': engine.trades[:100],  # Первые 100 сделок
        'equity_curve': engine.equity_curve[::24],  # Каждые 24 бара
        'timestamp': datetime.now().isoformat()
    }

    results_path = os.path.join(results_dir, f'backtest_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nРезультаты сохранены: {results_path}")


if __name__ == '__main__':
    main()
