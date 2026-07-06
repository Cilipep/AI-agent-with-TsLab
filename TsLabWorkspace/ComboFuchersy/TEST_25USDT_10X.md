# Итоговый бэктест: 25 USDT + 10x плечо

## SOL 1h: 25 USDT + 10x (Shares=1.67)

| Параметр | Значение |
|---|---|
| Начальный депозит | 25 USDT |
| Плечо | 10x |
| Net Profit | +0.06% |
| Сделок | 27 |
| Win Rate | 66.7% |
| Profit Factor | 2.72 |
| Max Drawdown | -0.02% |

## ETH 1h: Проблема

Оптимизация повредила параметры скрипта ETH. Для восстановления нужно:
1. Пересоздать скрипт из JSON-файла
2. Или вручную задать параметры: RSI=16, Threshold=25, ATR=7

## Настройки

| Параметр | Значение |
|---|---|
| RSI Period | 16 |
| RSI Threshold | 25 |
| ATR Period | 7 |
| ATR Multiplier | 2 |
| Commission | 0.01% |
| Stop-loss | динамический (Close) |
| Take-profit | Close + ATR × 2 |

## Дата тестирования
28.06.2026
