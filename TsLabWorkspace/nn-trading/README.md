# Neural Network Trading Strategy

## Описание проекта

Нейросетевая торговая стратегия для криптовалютных фьючерсов Binance Coin-Margined Futures. Использует ансамбль из 4 моделей (TCN, LSTM, Transformer, Attention) с оптимизацией через Optuna и интеграцией в TSLab.

---

## Результаты (Optuna Walk-Forward Оптимизация)

### Финальная валидация (5 folds, embargo=7)

| Инструмент | Return | Sharpe | MaxDD | Trades | WinRate | Статус |
|------------|--------|--------|-------|--------|---------|--------|
| **NEAR** | **+241.78%** | 1.09 | -45.28% | 737 | 35.6% | Торговать |
| **SOL** | **+48.37%** | 0.46 | -32.55% | 733 | 37.0% | Торговать |

**Среднее:** +145.07% | **Прибыльных:** 2/2

### Оптимизированные параметры

#### NEAR/USDT
| Параметр | Значение |
|----------|----------|
| hidden_size | 32 |
| num_layers | 2 |
| dropout | 0.3246 |
| nhead | 4 |
| window | 30 |
| max_features | 50 |
| batch_size | 32 |
| learning_rate | 0.000253 |
| stop_loss_pct | 2.56% |
| take_profit_pct | 11.11% |

#### SOL/USDT
| Параметр | Значение |
|----------|----------|
| hidden_size | 32 |
| num_layers | 1 |
| dropout | 0.4989 |
| nhead | 8 |
| window | 40 |
| max_features | 30 |
| batch_size | 64 |
| learning_rate | 0.000174 |
| stop_loss_pct | 2.24% |
| take_profit_pct | 7.02% |

---

## Архитектура системы

### Модели (ансамбль из 4 штук)
- **TCN** — Temporal Convolutional Network
- **LSTM** — Long Short-Term Memory
- **Transformer** — Multi-head Self-Attention
- **Attention** — Custom Attention Block

### Индикаторы
- 55 технических индикаторов TA-Lib
- Feature Selection: 25 признаков из 55
- Период: 60 дней, 15m свечи

### Интеграция с TSLab
- C# индикатор NNTradingIndicator (без ONNX Runtime)
- Формула: RSI + MACD + EMA
- Protective exits: SL -3%, TP +3%

---

## Манименеджмент

| Параметр | Значение |
|----------|----------|
| Депозит | 70 USDT |
| Risk per trade | 1%-20% |
| Плечо | 1x, 3x, 5x, 10x, 20x, 30x |
| Реинвест | 10%-50% от прибыли |
| Stop Loss | -3% |
| Take Profit | +3% |
| Комиссия | 0.1% |

---

## Структура файлов

`
nn-trading/
├── data/                          # CSV данные (15m свечи)
├── models/                        # Обученные модели
│   ├── final_ensemble.pt          # Финальный ансамбль
│   └── ensemble.pt                # Промежуточный
├── NNTradingIndicator.cs          # C# индикатор для TSLab
├── IndicatorHandlers.csproj       # Проект
├── backtest_final.py              # Скрипт бэктеста
├── model.py                       # LSTM/TCN/Transformer/Attention
├── train.py                       # Обучение моделей
├── features_talib.py              # TA-Lib признаки
├── config.py                      # Конфигурация
├── NN_Trading_Report.docx         # Отчёт
└── requirements.txt               # Зависимости
`

---

## Запуск

### Бэктест
`ash
python backtest_final.py
`

### TSLab индикатор
1. Пересобрать: dotnet build -c Release
2. Загрузить: curl -F "file=@bin\Release\net10.0\IndicatorHandlers.dll" "http://localhost:5000/api/indicator-dlls/NNTradingIndicator.dll"
3. Открыть TSLab → скрипт → Run

---

## Технологии

- **PyTorch** — нейросети
- **TA-Lib** — техничикатические индикаторы (55+)
- **Optuna** — оптимизация гиперпараметров
- **TSLab** — торговая платформа
- **Binance Futures** — биржа

---

## Выводы

1. **Optuna оптимизация** с walk-forward валидацией находит лучшие параметры
2. **NEAR** — лучший инструмент: +241.78% за 5 лет, Sharpe 1.09
3. **SOL** — стабильный: +48.37%, умеренный drawdown -32.55%
4. **HybridEnsemble** (3 NN + 4 sklearn) показывает стабильные результаты
5. **Embargo=7** предотвращает утечку данных между фолдами

---

*Обновлено: 15.07.2026 — Optuna Walk-Forward Оптимизация*
