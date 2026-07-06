# Chart Analyzer

Python CLI утилита для анализа графиков с данными из Binance/Bybit.

## Установка

```bash
cd chart-analyzer
pip install -r requirements.txt
```

## Использование

```bash
# Анализ BTCUSDT с Binance (по умолчанию)
python analyzer.py

# Указать таймфрейм
python analyzer.py --symbol ETHUSDT --interval 1h

# Указать биржу
python analyzer.py --symbol BTCUSDT --exchange bybit

# Сохранить HTML-отчёт
python analyzer.py --output report.html
```

## Возможности

- Свечные паттерны (доджи, молот, поглощение и др.)
- Уровни поддержки/сопротивления
- Тренд-индикаторы (EMA, RSI, MACD)
- Объёмный анализ
- HTML-отчёт с графиками
