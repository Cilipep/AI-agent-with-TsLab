"""
Улучшенный бэктестинг с оптимизированными сигналами
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

    # ATR (Average True Range)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = tr.rolling(window=14).mean()

    return df


class ImprovedBacktestEngine:
    """Улучшенный движок бэктестинга"""

    def __init__(self, config):
        self.config = config
        self.initial_capital = config['capital']
        self.current_capital = self.initial_capital
        self.max_capital = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = []

        # Параметры
        self.position_size_pct = config.get('position_size_pct', 0.02)
        self.stop_loss_atr_mult = config.get('stop_loss_atr_mult', 2.0)
        self.take_profit_atr_mult = config.get('take_profit_atr_mult', 3.0)
        self.min_confidence = config.get('min_confidence', 0.002)
        self.cooldown_bars = config.get('cooldown_bars', 5)
        self.commission_pct = config.get('commission_pct', 0.001)

        self.last_trade_bar = -self.cooldown_bars

    def run_backtest(self, df, predictor, sequence_length=60):
        """Запуск бэктестинга"""
        df = compute_features(df)
        features = ['close', 'volume', 'rsi', 'macd', 'macd_signal',
                    'bb_width', 'ema_9', 'ema_21', 'volume_ratio', 'volatility']

        df_valid = df.dropna().reset_index(drop=True)

        print(f"Запуск бэктестинга на {len(df_valid)} барах...")
        print(f"Начальный капитал: ${self.initial_capital:.2f}")
        print()

        for i in range(sequence_length, len(df_valid) - 1):
            current_bar = df_valid.iloc[i]
            next_bar = df_valid.iloc[i + 1]

            current_price = current_bar['close']
            next_price = next_bar['close']
            atr = current_bar.get('atr', current_price * 0.02)

            # Проверка стоп-лосса и тейк-профита
            if self.position:
                if self.position['side'] == 'long':
                    if current_price <= self.position['stop_loss']:
                        self._close_position(current_price, 'stop_loss')
                    elif current_price >= self.position['take_profit']:
                        self._close_position(current_price, 'take_profit')
                else:
                    if current_price >= self.position['stop_loss']:
                        self._close_position(current_price, 'stop_loss')
                    elif current_price <= self.position['take_profit']:
                        self._close_position(current_price, 'take_profit')

            # Получение предсказания
            X = df_valid[features].iloc[i-sequence_length:i].values
            prediction = predictor.predict_batch(X)

            # Расчет сигнала
            price_change_pct = (prediction - current_price) / current_price

            # Генерация сигнала с учетом условий
            signal = None
            if price_change_pct > self.min_confidence:
                signal = 'long'
            elif price_change_pct < -self.min_confidence:
                signal = 'short'

            # Дополнительные фильтры
            rsi = current_bar.get('rsi', 50)
            volume_ratio = current_bar.get('volume_ratio', 1)

            # Фильтр по RSI
            if signal == 'long' and rsi > 70:
                signal = None  # Перекупленность
            elif signal == 'short' and rsi < 30:
                signal = None  # Перепроданность

            # Фильтр по объему
            if volume_ratio < 0.5:
                signal = None  # Низкий объем

            # Открытие позиции
            if signal and not self.position and (i - self.last_trade_bar) >= self.cooldown_bars:
                self._open_position(signal, current_price, atr)

            # Запись equity
            unrealized_pnl = 0
            if self.position:
                if self.position['side'] == 'long':
                    unrealized_pnl = (current_price - self.position['entry_price']) * self.position['size']
                else:
                    unrealized_pnl = (self.position['entry_price'] - current_price) * self.position['size']

            self.equity_curve.append({
                'bar': i,
                'equity': self.current_capital + unrealized_pnl
            })

            self.max_capital = max(self.max_capital, self.current_capital + unrealized_pnl)

        # Закрытие оставшейся позиции
        if self.position:
            self._close_position(df_valid.iloc[-1]['close'], 'end_of_backtest')

        return self._calculate_metrics()

    def _open_position(self, side, price, atr):
        """Открытие позиции"""
        position_value = self.current_capital * self.position_size_pct
        size = position_value / price

        commission = position_value * self.commission_pct
        self.current_capital -= commission

        if side == 'long':
            stop_loss = price - atr * self.stop_loss_atr_mult
            take_profit = price + atr * self.take_profit_atr_mult
        else:
            stop_loss = price + atr * self.stop_loss_atr_mult
            take_profit = price - atr * self.take_profit_atr_mult

        self.position = {
            'side': side,
            'entry_price': price,
            'size': size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_bar': len(self.equity_curve)
        }

    def _close_position(self, price, reason):
        """Закрытие позиции"""
        if not self.position:
            return

        if self.position['side'] == 'long':
            pnl = (price - self.position['entry_price']) * self.position['size']
        else:
            pnl = (self.position['entry_price'] - price) * self.position['size']

        commission = self.position['size'] * price * self.commission_pct
        pnl -= commission

        self.current_capital += pnl

        self.trades.append({
            'side': self.position['side'],
            'entry_price': self.position['entry_price'],
            'exit_price': price,
            'size': self.position['size'],
            'pnl': pnl,
            'reason': reason,
            'entry_bar': self.position['entry_bar'],
            'exit_bar': len(self.equity_curve)
        })

        self.last_trade_bar = len(self.equity_curve)
        self.position = None

    def _calculate_metrics(self):
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

        # Profit factor по сделкам
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = sum(abs(t['pnl']) for t in losing_trades)

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
            'total_wins': float(total_wins),
            'total_losses': float(total_losses),
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
        'position_size_pct': 0.02,
        'stop_loss_atr_mult': 2.0,
        'take_profit_atr_mult': 3.0,
        'min_confidence': 0.002,
        'cooldown_bars': 5,
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
    engine = ImprovedBacktestEngine(config)
    metrics = engine.run_backtest(df, predictor, sequence_length=60)

    # Вывод результатов
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ БЭКТЕСТИНГА (УЛУЧШЕННАЯ ВЕРСИЯ)")
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
    print(f"Общий выигрыш: ${metrics['total_wins']:.2f}")
    print(f"Общий проигрыш: ${metrics['total_losses']:.2f}")
    print(f"Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
    print("=" * 50)

    # Сохранение результатов
    results = {
        'config': config,
        'metrics': metrics,
        'trades': engine.trades[:100],
        'equity_curve': engine.equity_curve[::24],
        'timestamp': datetime.now().isoformat()
    }

    results_path = os.path.join(results_dir, f'backtest_improved_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nРезультаты сохранены: {results_path}")


if __name__ == '__main__':
    main()
