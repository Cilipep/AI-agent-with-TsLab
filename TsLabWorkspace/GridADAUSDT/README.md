# GridBot Final — Оптимизированная Grid-стратегия для BTC

## Описание

GridBot Final — это двусторонняя сеточная стратегия для торговли BTC фьючерсами на Binance с оптимизированными параметрами, реинвестированием и трейлингом по логике Bybit.

## Финальная конфигурация

- **Символ**: BTC/USDT Perpetual
- **Таймфрейм**: 30m
- **Капитал**: $40 USDT
- **Плечо**: 20x
- **Реинвест**: 30% прибыли
- **Grid Spacing**: 2.5x ATR(14)
- **Stop Distance**: 3.0x ATR(14)
- **Trailing Up/Down**: Включено

## Результаты бэктеста

| Метрика | Значение |
|---------|----------|
| Прибыль | +$1,562 (+3,904%) |
| Win Rate | 68% |
| Profit Factor | 0.97 |
| Max Drawdown | 59.4% |
| Sharpe Ratio | 9.53 |

## Запуск

```bash
# Бэктест
python GridBot_Final.py

# Live (нужен ccxt)
pip install ccxt
python GridBot_Final.py live
```

## Структура проекта

```
GridADAUSDT/
├── GridBot_Final.py          # Основной код
├── config.json               # Конфигурация
├── FINAL_CONFIG.md           # Документация
├── GridBot_Final_Results.json # Результаты
├── GridBot_EquityCurve.png   # Equity curve
├── GridBot_TradeAnalysis.png # Анализ сделок
└── README.md                 # Этот файл
```
