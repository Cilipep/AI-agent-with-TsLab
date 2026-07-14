# Neural Network Crypto Trading v2

Улучшенная нейросетевая торговая стратегия с ансамблем моделей и walk-forward валидацией.

## Улучшения по сравнению с v1

| Характеристика | v1 (старая) | v2 (новая) |
|----------------|-------------|------------|
| Модели | 1 LSTM | Ансамбль: LSTM + TCN + Transformer + Attention + sklearn |
| Индикаторы | 10 признаков | 55+ TA-Lib индикаторов |
| Валидация | Train/Val/Test split | Walk-forward с embargo |
| Оптимизация | Нет | Feature Selection |
| Risk Management | Базовый | Trailing Stop + Dynamic Sizing |
| Инструменты | BTC, ETH | BTC, ETH, SOL, ADA, XRP |

## Структура проекта

```
nn-trading2/
├── scripts/
│   ├── config.py          # Конфигурация (dataclass)
│   ├── model.py           # Модели: LSTM, TCN, Transformer, Attention + Ensemble
│   ├── features.py        # 55+ TA-Lib индикаторов
│   ├── dataset.py         # TimeSeriesDataset
│   ├── train.py           # Обучение моделей
│   ├── backtest.py        # Движок бэктестинга
│   ├── backtest_3yr.py    # Walk-forward бэктест
│   └── download_data.py   # Загрузка данных
├── data/                  # CSV данные
├── models/                # Обученные модели
├── results/               # Результаты
└── requirements.txt       # Зависимости
```

## Установка

```bash
pip install -r requirements.txt
```

## Использование

### 1. Загрузка данных
```bash
python scripts/download_data.py
```

### 2. Запуск бэктеста
```bash
python scripts/backtest_3yr.py
```

## Архитектура ансамбля

### Нейросетевые модели
- **LSTM** — Long Short-Term Memory
- **TCN** — Temporal Convolutional Network
- **Transformer** — Multi-head Self-Attention
- **Attention** — Custom Attention Block

### sklearn модели
- **XGBoost** — Gradient Boosting
- **CatBoost** — Categorical Boosting
- **LightGBM** — Light Gradient Boosting
- **Random Forest** — Random Forest

### Walk-forward валидация
- 3 фолда с embargo=7 между фолдами
- Scaler.fit только на train данных (без утечки)
- Ансамбль из 3 моделей с разными seed

## Risk Management

| Параметр | Значение |
|----------|----------|
| Stop Loss | 3% |
| Take Profit | 7% |
| Trailing Stop | 1.5% |
| Risk per trade | 2% |
| Комиссия | 0.1% |

## Технологии

- **PyTorch** — нейросети
- **scikit-learn** — ML модели
- **XGBoost/CatBoost/LightGBM** — boosting
- **TA-Lib** — технические индикаторы
