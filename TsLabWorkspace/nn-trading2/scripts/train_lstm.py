"""
LSTM модель для предсказания движения цены криптовалюты
"""
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os
import json
from datetime import datetime


class LSTMModel(nn.Module):
    """LSTM модель для предсказания цены"""

    def __init__(self, input_size=10, hidden_size=64, num_layers=2, output_size=3):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, output_size)
        )

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


def prepare_data(df, sequence_length=60):
    """Подготовка данных для обучения"""
    features = ['close', 'volume', 'rsi', 'macd', 'macd_signal',
                'bb_width', 'ema_9', 'ema_21', 'volume_ratio', 'volatility']

    df = df.dropna()

    X = df[features].values
    y = df['close'].values

    # Нормализация
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()

    # Создание последовательностей
    X_seq, y_seq = [], []
    for i in range(sequence_length, len(X_scaled)):
        X_seq.append(X_scaled[i-sequence_length:i])
        y_seq.append(y_scaled[i])

    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    return X_seq, y_seq, scaler_X, scaler_y


def train_model(model, X_train, y_train, X_val, y_val, epochs=100, lr=0.001):
    """Обучение модели"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)

    X_train = torch.FloatTensor(X_train).to(device)
    y_train = torch.FloatTensor(y_train).to(device)
    X_val = torch.FloatTensor(X_val).to(device)
    y_val = torch.FloatTensor(y_val).to(device)

    best_val_loss = float('inf')
    best_model_state = None
    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs.squeeze(), y_train)
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val)
            val_loss = criterion(val_outputs.squeeze(), y_val)

        scheduler.step(val_loss)

        train_losses.append(loss.item())
        val_losses.append(val_loss.item())

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = model.state_dict().copy()

        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {loss.item():.6f}, Val Loss: {val_loss.item():.6f}')

    model.load_state_dict(best_model_state)
    return model, train_losses, val_losses


def backtest(model, X_test, y_test, scaler_y, df_test, sequence_length=60):
    """Бэктестинг модели"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.eval()

    X_test_tensor = torch.FloatTensor(X_test).to(device)

    with torch.no_grad():
        predictions = model(X_test_tensor).cpu().numpy()

    predictions = scaler_y.inverse_transform(predictions.reshape(-1, 1)).flatten()
    actual = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()

    # Создаем сигналы: 1 = long, 0 = flat, -1 = short
    signals = []
    for i in range(1, len(predictions)):
        if predictions[i] > actual[i-1] * 1.001:  # Predict > 0.1% up
            signals.append(1)
        elif predictions[i] < actual[i-1] * 0.999:  # Predict > 0.1% down
            signals.append(-1)
        else:
            signals.append(0)

    signals = np.array(signals)

    # Расчет PnL
    returns = df_test['close'].pct_change().values[sequence_length+1:]
    returns = returns[:len(signals)]

    strategy_returns = signals * returns

    # Метрики
    total_return = (1 + strategy_returns).prod() - 1
    sharpe = np.mean(strategy_returns) / (np.std(strategy_returns) + 1e-8) * np.sqrt(365 * 24)
    max_drawdown = (pd.Series(strategy_returns).cumsum() - pd.Series(strategy_returns).cumsum().cummax()).min()
    win_rate = (signals == np.sign(returns)).mean()

    metrics = {
        'total_return': float(total_return),
        'sharpe_ratio': float(sharpe),
        'max_drawdown': float(max_drawdown),
        'win_rate': float(win_rate),
        'num_trades': int(np.sum(signals != 0))
    }

    return metrics, signals


def main():
    # Загрузка данных
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')

    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    symbol = 'BTC_USDT_1h'
    filepath = os.path.join(data_dir, f'{symbol}.csv')

    if not os.path.exists(filepath):
        print(f"Файл {symbol}.csv не найден!")
        return

    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    print(f"Загружено {len(df)} записей")

    # Подготовка данных
    sequence_length = 60
    X, y, scaler_X, scaler_y = prepare_data(df, sequence_length)

    # Разделение данных
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, shuffle=False)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, shuffle=False)

    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Создание и обучение модели
    input_size = X.shape[2]
    model = LSTMModel(input_size=input_size, hidden_size=64, num_layers=2, output_size=1)

    print("\nОбучение модели...")
    model, train_losses, val_losses = train_model(
        model, X_train, y_train, X_val, y_val,
        epochs=100, lr=0.001
    )

    # Сохранение модели
    model_path = os.path.join(models_dir, 'lstm_model.pth')
    torch.save({
        'model_state_dict': model.state_dict(),
        'input_size': input_size,
        'hidden_size': 64,
        'num_layers': 2,
        'sequence_length': sequence_length
    }, model_path)

    # Сохранение скейлеров отдельно
    import pickle
    scaler_path = os.path.join(models_dir, 'scalers.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump({'scaler_X': scaler_X, 'scaler_y': scaler_y}, f)

    print(f"\nМодель сохранена: {model_path}")
    print(f"Скейлеры сохранены: {scaler_path}")

    # Бэктестинг
    print("\nБэктестинг...")
    test_df = df.iloc[-len(X_test)-sequence_length:]
    metrics, signals = backtest(model, X_test, y_test, scaler_y, test_df, sequence_length)

    print(f"\nРезультаты бэктестинга:")
    print(f"Доходность: {metrics['total_return']*100:.2f}%")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
    print(f"Win Rate: {metrics['win_rate']*100:.2f}%")
    print(f"Количество сделок: {metrics['num_trades']}")

    # Сохранение результатов
    results = {
        'symbol': symbol,
        'model': 'LSTM',
        'sequence_length': sequence_length,
        'train_size': len(X_train),
        'val_size': len(X_val),
        'test_size': len(X_test),
        'metrics': metrics,
        'train_losses': train_losses,
        'val_losses': val_losses,
        'timestamp': datetime.now().isoformat()
    }

    results_path = os.path.join(results_dir, f'training_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nРезультаты сохранены: {results_path}")


if __name__ == '__main__':
    main()
