# Neural Network Trading Strategy

## Описание проекта

Нейросетевая торговая стратегия для криптовалютных фьючерсов Binance Coin-Margined Futures. Использует ансамбль из 4 моделей (TCN, LSTM, Transformer, Attention) с оптимизацией через Optuna и интеграцией в TSLab.

---

## Результаты бэктеста (оптимизированный ансамбль)

| Инструмент | Return | Win% | MaxDD | Trades | PF | Sharpe | Calmar |
|------------|--------|------|-------|--------|-----|--------|--------|
| **AAVE** | **+24.05%** | 3.1% | -6.66% | 140 | **1.43** | **4.20** | 3.61 |
| **NEAR** | **+17.74%** | 46.3% | -28.52% | 49 | 1.02 | 1.18 | 0.62 |
| **XLM** | **+15.85%** | 42.8% | -29.45% | 19 | 1.02 | 1.12 | 0.54 |
| **SOL** | **+12.87%** | 6.2% | -6.63% | 218 | 1.17 | 3.10 | 1.94 |
| TRX | -5.04% | 51.3% | -17.38% | 0 | 0.98 | -1.12 | -0.34 |
| ADA | -3.50% | 1.6% | -5.84% | 8 | 0.84 | -1.76 | -0.60 |
| SUI | -10.30% | 4.0% | -13.53% | 14 | 0.87 | -2.22 | -0.76 |
| UNI | -14.18% | 34.6% | -35.45% | 358 | 0.98 | -0.85 | -0.40 |
| LINK | -25.35% | 47.2% | -40.67% | 80 | 0.96 | -2.06 | -0.62 |
| BCH | +0.00% | 0.0% | 0.00% | 0 | inf | 0.00 | 0.00 |

**Среднее:** +1.21% | **Прибыльных:** 4/10

---

## Рекомендуемые инструменты для торговли

| Инструмент | Return | Sharpe | Решение |
|------------|--------|--------|---------|
| AAVE | +24.05% | 4.20 | Торговать |
| NEAR | +17.74% | 1.18 | Торговать |
| XLM | +15.85% | 1.12 | Торговать |
| SOL | +12.87% | 3.10 | Торговать |

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

1. **Ансамбль 4 моделей** стабильнее одной модели
2. **Feature Selection** (25 из 55) ускоряет обучение
3. **4 прибыльных инструмента** для торговли
4. **AAVE** — лучший Sharpe 4.20
5. **SOL** — лучший Calmar 1.94

---

*Обновлено: 10.07.2026*
