# TSLab Realtime Trading Guide

## Overview

Полная интеграция нейросетевой торговой стратегии с TSLab для real-time трейдинга.

## Компоненты

### 1. PowerShell Helpers
- `tslab-trade.ps1` — утилита для работы с TSLab Web API
- `tslab-nn-agent.ps1` — основной торговый агент
- `demo-nn-agent.ps1` — демо-скрипт для быстрого старта

### 2. WebSocket Streamer (Python)
- `tslab_signal_streamer.py` — streaming сигналов через WebSocket
- `tslab_signal_client.html` — веб-интерфейс для мониторинга

### 3. TSLab Integration
- `NNTradingIndicator.cs` — C# индикатор для TSLab
- `IndicatorHandlers.csproj` — проект индикатора

## Установка

### 1. TSLab API
```powershell
# Запустить TSLab
& "..\start-local-tslab.ps1"

# Проверить API
curl.exe -s http://localhost:5000/api/status
```

### 2. Python зависимости
```bash
pip install -r requirements.txt
```

### 3. Сборка индикатора
```bash
dotnet build -c Release IndicatorHandlers.csproj
```

## Быстрый старт

### Способ 1: PowerShell агент (рекомендуется)

```powershell
# Запустить демо
& ".\demo-nn-agent.ps1"

# Или запустить агент напрямую
& ".\tslab-nn-agent.ps1" `
    -ScriptName "NNSignal" `
    -SecurityId "NEARUSDT" `
    -DryRun  # БезDryRun для реальных ордеров
```

### Способ 2: WebSocket streamer

```bash
# Запустить сервер (в одном терминале)
python tslab_signal_streamer.py

# Открыть клиент (в браузере)
file:///C:/path/to/nn-trading/tslab_signal_client.html
```

## Конфигурация

### Параметры агента
- `ScriptName` — имя скрипта в TSLab
- `SecurityId` — инструмент (например, "NEARUSDT")
- `InitialDeposit` — начальный депозит (по умолчанию 1000)
- `RiskPerTrade` — риск на сделку (по умолчанию 0.05 = 5%)
- `ThresholdBuy` — порог BUY сигнала (по умолчанию 0.55)
- `ThresholdSell` — порог SELL сигнала (по умолчанию 0.45)
- `IntervalMinutes` — интервал проверки (по умолчанию 5)
- `DryRun` — режим тестирования (по умолчанию false)

### Параметры WebSocket
- `WS_HOST` — хост (по умолчанию "localhost")
- `WS_PORT` — порт (по умолчанию 8765)
- `WS_PATH` — путь (по умолчанию "/signal")

## Структура сигнала

WebSocket отправляет JSON:

```json
{
  "timestamp": "2026-07-20T00:00:00+00:00",
  "symbol": "NEAR",
  "signal": "BUY",
  "probability": 0.6234,
  "confidence": 0.75
}
```

## Проверка статуса

### TSLab API
```powershell
# Статус
curl.exe http://localhost:5000/api/status

# Позиции
curl.exe http://localhost:5000/api/trading/own-positions?take=500&skip=0&nonZeroOnly=true

# Ордера
curl.exe http://localhost:5000/api/trading/own-orders?take=200&skip=0&activeOnly=true
```

### PowerShell утилита
```powershell
# Получить позиции
& ".\tslab-trade.ps1" GET "trading/own-positions?take=500&skip=0&nonZeroOnly=true" "" ""

# Получить ордера
& ".\tslab-trade.ps1" GET "trading/own-orders?take=200&skip=0&activeOnly=true" "" ""
```

## Исправление ошибок

### TSLab API не отвечает
1. Проверить, запущен ли TSLab: `Get-Process TSLab*`
2. Запустить: `& "..\start-local-tslab.ps1"`
3. Проверить порт 5000: `netstat -ano | findstr :5000`

### Сигнал не поступает
1. Проверить, создан ли скрипт в TSLab
2. Убедиться, что скрипт содержит необходимые блоки:
   - Close (ISecurity)
   - NNTradingIndicator (DynamicItem)
   - Comparison (greaterThan)
   - BuySell (BuySellItem)
3. Проверить WebSocket сервер: `python -m websockets ws://localhost:8765/signal`

### Ордера не ставятся
1. Проверить API ключи (если auth включен)
2. Убедиться, что позиции открыты
3. Проверить баланс (мин. $5 для тестнета)

## Дополнительно

### Демо WebSocket клиента
Открыть в браузере: `tslab_signal_client.html`

### Логирование
Агент сохраняет логи в `results/trade_log.json`

### Мониторинг
- WebSocket: `ws://localhost:8765/signal`
- Текстовый лог: `results/trade_log.json`
- TSLab график: скрипт → визуализация
