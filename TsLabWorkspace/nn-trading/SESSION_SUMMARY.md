# Итоги сессии: nn-trading v2

## Дата: 2026-07-11

## Внесённые изменения

### 1. Расширение данных
- Добавлены данные Binance mainnet (1820 свечей)
- 11 инструментов: BTC, ETH, SOL, NEAR, XLM, AAVE, LINK, SUI, ADA, BCH, TRX, UNI
- Мультитаймфрейм: 1d + 1w + 1M для каждого инструмента
- BTC дополнительно: 5m, 15m, 30m, 1h, 4h

### 2. HybridEnsemble (3 NN + 4 sklearn)
- LSTM, Transformer, Attention (3 модели с разными seed)
- XGBoost, CatBoost, LightGBM, RandomForest
- Auto-select топ-50 фичей из 50-170

### 3. Мультитаймфреймовые фичи
- Для каждого ТФ: EMA(10,20,50), RSI, MACD, BB, ATR, ADX, Stoch, Williams, CCI, ROC, Momentum
- Forward-fill к дневным барам
- Автоматический отбор через RF importance + Mutual Information

### 4. DQN RL агент (создан, не обучен)
- Dueling DQN с Replay Buffer
- Actions: Buy/Hold/Sell
- Confidence filter: 0.6+
- Cooldown: 3 бара

### 5. Portfolio + отчёт + 3D
- Portfolio allocation по Sharpe ratio
- Docx отчёт на русском
- 3D визуализация архитектуры (Three.js)

## Результаты (Binance, Multi-Timeframe)

| Инструмент | Return | Drawdown | Win Rate | Sharpe |
|------------|--------|----------|----------|--------|
| Bitcoin | -17.67% | -26.82% | 32.5% | -0.74 |
| **Ethereum** | **+43.03%** | -20.93% | 37.5% | 1.17 |
| **Solana** | **+387.64%** | -11.39% | 38.0% | 3.43 |

### Portfolio
- ETH 50% + SOL 50%
- Expected return: +215.33%

## Файлы

| Файл | Описание |
|------|----------|
| `download_all.py` | Скачивание всех данных |
| `features_all.py` | Мультитаймфрейм фичи |
| `rl_agent.py` | DQN RL агент |
| `run_rl_all.py` | Walk-forward RL |
| `portfolio.py` | Распределение капитала |
| `generate_report.py` | Генерация docx |
| `nn_3d_visualization.py` | 3D визуализация |
| `NN_Trading_Report_v2.docx` | Отчёт |
| `nn_3d_architecture.html` | 3D модель |
