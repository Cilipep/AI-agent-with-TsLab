# Результаты проекта NN Trading

## Текущий статус: ✅ Базовая система готова

## Результаты бэктестинга

### Базовая LSTM модель
| Метрика | Значение |
|---------|----------|
| Доходность | -14.19% |
| Sharpe Ratio | -2.02 |
| Win Rate | 49.23% |
| Max Drawdown | -24.58% |

### Улучшенная модель (с фильтрами)
| Метрика | Значение |
|---------|----------|
| Доходность | -0.74% |
| Sharpe Ratio | -0.87 |
| Win Rate | 43.95% |
| Profit Factor | 0.98 |
| Max Drawdown | -1.27% |
| Количество сделок | 314 |

## Что сделано

1. **Настройка окружения**
   - Python 3.13.5
   - PyTorch 2.12.1
   - TensorFlow 2.21.0
   - ONNX Runtime

2. **Сбор данных**
   - 8760 записей BTC/USDT (1h, 365 дней)
   - 8760 записей ETH/USDT (1h, 365 дней)

3. **Обучение LSTM модели**
   - Архитектура: 2 слоя LSTM, hidden_size=64
   - Признаки: close, volume, RSI, MACD, Bollinger Bands, EMA, volatility
   - Экспорт в ONNX для C# инференса

4. **Бэктестинг**
   - Улучшенная модель с фильтрами (RSI, объем, cooldown)
   - Управление рисками: stop-loss, take-profit, position sizing

5. **Подключение к Binance**
   - Тест публичных данных успешен
   - Текущая цена BTC: ~$62,000

## Структура файлов

```
TsLabWorkspace/nn-trading/
├── data/
│   ├── BTC_USDT_1h.csv
│   └── ETH_USDT_1h.csv
├── models/
│   ├── lstm_model.pth
│   ├── lstm_model.onnx
│   ├── scalers.pkl
│   └── lstm_model_metadata.json
├── scripts/
│   ├── download_data.py
│   ├── train_lstm.py
│   ├── export_onnx.py
│   ├── backtest_historical.py
│   ├── backtest_improved.py
│   ├── trading_bot.py
│   └── binance_testnet.py
├── csharp-inference/
│   ├── NNInference.csproj
│   └── Program.cs
├── results/
│   └── backtest_*.json
├── requirements.txt
└── README.md
```

## Следующие шаги

### Приоритет 1: Оптимизация модели
- [ ] Подбор гиперпараметров (learning rate, hidden size, sequence length)
- [ ] Добавление Attention механизма
- [ ] Использование Transformer архитектуры
- [ ] Walk-forward validation

### Приоритет 2: Подключение к Testnet
- [ ] Получить API ключи Testnet
- [ ] Тестирование на реальных данных
- [ ] Paper trading

### Приоритет 3: Интеграция с TsLab
- [ ] Создание C# индикатора для TsLab
- [ ] Передача сигналов из Python в TsLab
- [ ] Автоматическое исполнение ордеров

### Приоритет 4: Дополнительные функции
- [ ] Мониторинг в реальном времени
- [ ] Уведомления (Telegram)
- [ ] Dashboard для визуализации

## Как запустить

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Загрузка данных
python scripts/download_data.py

# 3. Обучение модели
python scripts/train_lstm.py

# 4. Бэктестинг
python scripts/backtest_improved.py

# 5. Тест подключения к Binance
python scripts/binance_testnet.py
```

## Технологии

- Python 3.13.5
- PyTorch 2.12.1
- TensorFlow 2.21.0
- ONNX Runtime
- C# .NET 8.0
- ccxt (Binance API)
- scikit-learn
- pandas, numpy
