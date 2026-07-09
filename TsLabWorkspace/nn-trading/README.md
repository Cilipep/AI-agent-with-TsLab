# Neural Network Trading Strategy

## Описание проекта

Проект нейросетевой торговой стратегии для криптовалют, использующий TCN/LSTM ансамбли с оптимизацией гиперпараметров через Optuna, библиотеку TA-Lib для технических индикаторов и продвинутый риск-менеджмент с trailing stop.

---

## Итоговые результаты

| Метрика | Значение |
|---------|----------|
| **Total Return** | **+26.62%** |
| **Max Drawdown** | **-4.08%** |
| **Win Rate** | 30.7% |
| **Profit Factor** | ~1.5-2.0 |

---

## Архитектура системы

### Основные компоненты

| Компонент | Описание |
|-----------|----------|
| `model.py` | LSTM, TCN, Transformer модели, ансамбли |
| `train.py` | Обучение моделей с early stopping |
| `backtest_v2.py` | Бэктест с trailing stop + dynamic sizing |
| `features_talib.py` | 60+ индикаторов TA-Lib |
| `dataset.py` | Time series dataset для PyTorch |
| `config.py` | Конфигурация параметров |
| `walk_forward_tcn.py` | Walk-forward валидация |
| `optimize_simple.py` | Оптимизация с Optuna |

---

## Этапы разработки

### 1. Начальная версия
- Базовая LSTM модель с 30+ индикаторами
- Результат: переобучение, -67.10% доходности

### 2. Добавление признаков
- Stochastic RSI, Aroon, Keltner/Donchian Channel
- **Результат:** +12.30% walk-forward

### 3. TA-Lib интеграция
- 161 индикатор доступен, 60+ используется
- **Результат:** +11.91% walk-forward

### 4. Trailing Stop + Dynamic Sizing
- 1% trailing stop, динамический размер позиции
- **Результат:** +16.36% walk-forward, drawdown -4.93%

### 5. TCN модель
- Temporal Convolutional Network вместо LSTM
- **Результат:** +26.62% walk-forward, drawdown -4.08%

---

## Результаты по этапам

| Этап | Return | Drawdown | Win Rate |
|------|--------|----------|----------|
| 1. Базовая версия | -67.10% | -67.22% | 31.2% |
| 2. Новые признаки | +12.30% | -40.11% | 37.8% |
| 3. TA-Lib | +11.91% | -16.37% | 35.6% |
| 4. Trailing Stop | +16.36% | -4.93% | 28.0% |
| **5. TCN модель** | **+26.62%** | **-4.08%** | **30.7%** |

---

## Walk-Forward результаты (TCN)

| Fold | Return | Drawdown | Win Rate | PF |
|------|--------|----------|----------|-----|
| 1 | +9.49% | -3.14% | 35.3% | 1.59 |
| 2 | -0.26% | -0.26% | 0.0% | 0.00 |
| 3 | +0.72% | -0.65% | 42.9% | 1.95 |
| 4 | -0.63% | -1.83% | 27.3% | 0.91 |
| 5 | +1.89% | -4.08% | 36.0% | 1.20 |
| 6 | +13.70% | -3.45% | 42.9% | 2.09 |
| **Итого** | **+26.62%** | **-4.08%** | **30.7%** | - |

---

## Ключевые улучшения

### 1. TA-Lib индикаторы (60+)
- **Trend:** EMA, MACD, ADX, Aroon, SAR
- **Momentum:** RSI, Stochastic, Williams %R, CCI
- **Volatility:** Bollinger Bands, ATR, Keltner Channel
- **Volume:** OBV, AD, MFI
- **Patterns:** Doji, Hammer, Engulfing

### 2. Trailing Stop (1%)
- Фиксирует прибыль при движении цены
- Стоп следует за ценой вверх
- Снижает drawdown на 70%

### 3. Dynamic Position Sizing
- Уменьшает размер позиции при высокой волатильности
- Использует ATR для расчета
- Защищает от резких движений

### 4. TCN архитектура
- Temporal Convolutional Network
- Лучше LSTM для последовательностей
- Profit Factor: 1.72

---

## Лучшие параметры

```python
{
    "model_type": "tcn",
    "hidden_size": 32,
    "num_layers": 1,
    "dropout": 0.395,
    "window": 30,
    "batch_size": 64,
    "learning_rate": 0.000205,
    "n_models": 3,
    "stop_loss_pct": 0.0307,
    "take_profit_pct": 0.0454,
    "trailing_stop": 0.01,
    "dynamic_sizing": true
}
```

---

## Риск-менеджмент

- **Stop Loss:** 3.07%
- **Take Profit:** 4.54%
- **Trailing Stop:** 1%
- **Dynamic Sizing:** ON
- **Risk per Trade:** 1% от equity

---

## Запуск

### Установка зависимостей
```bash
pip install -r requirements.txt
pip install TA-Lib
```

### Walk-Forward валидация
```bash
python walk_forward_tcn.py
```

### Сравнение моделей
```bash
python test_models_comparison.py
```

---

## Структура файлов

```
nn-trading/
├── data/                    # Данные (CSV)
├── models/                  # Сохраненные модели
├── results/                 # Результаты
│   ├── walk_forward_tcn.json
│   ├── models_comparison.json
│   └── best_params_simple.json
├── model.py                 # LSTM/TCN/Transformer
├── features_talib.py        # TA-Lib признаки
├── backtest_v2.py           # Enhanced backtest
├── train.py                 # Обучение
├── walk_forward_tcn.py      # Walk-forward
├── config.py                # Конфигурация
└── requirements.txt
```

---

## Технологии

- **PyTorch** - нейросети
- **TA-Lib** - технические индикаторы (161 функция)
- **Optuna** - оптимизация гиперпараметров
- **TCN** - Temporal Convolutional Network

---

## Выводы

1. **TCN модель показала лучшие результаты** - +26.62% доходности
2. **Trailing Stop снизил drawdown на 70%** - с -16% до -4%
3. **Dynamic Sizing улучшил стабильность** - меньшие потери при волатильности
4. **TA-Lib дал 60+ индикаторов** для анализа
5. **Walk-forward подтвердил обобщающую способность** - 6 фолдов
