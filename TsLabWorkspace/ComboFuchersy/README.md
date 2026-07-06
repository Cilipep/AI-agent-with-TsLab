# ETH Combo Momentum Reversion Bot

## Параметры стратегии
- RSI Period: 16
- RSI Threshold: 25
- ATR Period: 7
- ATR Multiplier: 2 (для Take-Profit)
- Stop Loss: 2%
- Commission: 0.01%
- Shares: 1

## Условия входа
- Long: RSI(16) < 25 (mean reversion)

## Условия выхода
- Stop-loss: 2% от входа
- Take-profit: Close + ATR(7) × 2

## Метрики (3 месяца, 5m)
- Net Profit: +9.75%
- Всего сделок: 538
- Win Rate: 54.1%
- Profit Factor: 1.17
- Max Drawdown: -7.38%
- Recovery Factor: 1.17

## Индикаторы на графике
- RSI(16)
- MACD(12, 26, 9)
- EMA(50)
- EMA(200)
- ATR(7)
- Volume
- SMA(Volume, 20)

## Дата создания
28.06.2026
