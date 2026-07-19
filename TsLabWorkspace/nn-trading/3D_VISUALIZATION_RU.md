# 3D Visualization of Neural Network Models

## Overview

Это документация по 3D визуализации нейронных сетей проекта nn-trading.

## Созданные файлы

### 1. `export_onnx.py` - Экспорт в ONNX
Экспортирует модели PyTorch в формат ONNX для интеграции с TSLab.

**Возможности:**
- Конвертация модели из PyTorch в ONNX
- Генерация C# обёртки для ONNX Runtime
- Тестирование точности экспорта ONNX

**Использование:**
```bash
python export_onnx.py
```

**Результат:**
- `models/btc_attention_32.onnx` - ONNX модель
- `tslab_scripts/NNTradingIndicator.cs` - C# обёртка

### 2. `train_btc.py` - Тренировка для BTC
Пайплайн тренировки с конфигурируемыми таймфреймами.

**Возможности:**
- Конфигурируемые таймфреймы: 5m, 15m, 30m, 1h, 4h
- Walk-forward валидация
- BTC-специфичные параметры риска
- Мульти-таймфрейм ансамбли

**Конфигурация BTC таймфреймов:**
| Таймфрейм | Суффикс | Max Bars | Window | Epochs |
|-----------|---------|----------|--------|--------|
| 5m | `_5m.csv` | 10000 | 20 | 15 |
| 15m | `_15m.csv` | 8000 | 30 | 15 |
| 30m | `_30m.csv` | 6000 | 30 | 15 |
| 1h | `_1h.csv` | 6000 | 40 | 20 |
| 4h | `_4h.csv` | 4000 | 50 | 20 |

**Использование:**
```bash
python train_btc.py
```

### 3. `train_rl_walkforward.py` - RL с Walk-Forward
DQN reinforcement learning с walk-forward валидацией и интеграцией ансамбля.

**Возможности:**
- Walk-forward валидация для RL агентов
- Гибридная интеграция ансамбля (нейронные + sklearn + DQN)
- Тренировка DQN агента на предсказаниях ансамбля
- Многоэтапный пайплайн обучения

**Использование:**
```bash
python train_rl_walkforward.py
```

### 4. `calibrate_probs.py` & `calibration.py` - Калибровка вероятностей
Platt scaling и isotonic regression для калибровки вероятностей ансамбля.

**Возможности:**
- PlattScaler: Сигмоидная калибровка
- IsotonicCalibrator: Непараметрическая монотонная калибровка
- Сравнение производительности (Brier score, Log loss)
- Сохранение/загрузка параметров калибровки

**Использование:**
```python
from calibration import PlattScaler, IsotonicCalibrator

# Fit calibrator
platt = PlattScaler()
platt.fit(logits, targets)

# Calibrate predictions
calibrated_probs = platt.calibrate(test_logits)
```

### 5. `sensitivity_analysis.py` - Анализ чувствительности к комиссиям
Тестирует производительность модели при разных транзакционных издержках.

**Возможности:**
- Анализ чувствительности к комиссиям
- Анализ чувствительности к проскальзыванию
- Анализ чувствительности к спреду
- Общая оценка устойчивости

**Использование:**
```bash
python sensitivity_analysis.py
```

### 6. `btc_metrics.py` - BTC метрики
Комплексные BTC торговые метрики с сравнением таймфреймов.

**Возможности:**
- Риск-скорректированная прибыль (Sharpe, Sortino, Calmar)
- Анализ просадок
- Статистика по сделкам
- Рекомендации таймфрейма

**Использование:**
```bash
python btc_metrics.py
```

### 7. `tests/` - Модульные тесты
Полный набор тестов для основных модулей.

**Файлы тестов:**
- `test_core.py` - Тесты основной функциональности
- `test_utils.py` - Тесты служебных функций
- `test_features.py` - Тесты инженерии признаков
- `test_dataset.py` - Тесты обработки датасета
- `test_model.py` - Архитектура модели
- `test_train.py` - Пайплайн обучения
- `test_backtest.py` - Метрики бэктеста

**Использование:**
```bash
python -m unittest discover -s tests
```

## Визуализация архитектуры

### Модели нейронных сетей

#### LSTM модель
- Входной слой: 40-50 признаков
- LSTM слои: 2 слоя, hidden=64
- Dropout: 0.35
- Выход: Бинарная классификация (Buy/Hold/Sell)

#### Attention Transformer
- Multi-head attention с 8 head'ами
- Pre-norm архитектура (LayerNorm перед attention)
- Активация GELU
- Feed-forward сеть (4x расширение)

#### TCN модель
- Дилатированные causal свёртки
- Увеличивающиеся уровни дилатации
- Batch normalization
- Остаточные соединения

### Архитектура ансамбля

```
Вход (40-50 признаков)
    ↓
[Нейронные Сети]  [Sklearn Модели]
  LSTM    Attention    XGBoost
  TCN     Transformer  CatBoost
  etc.    etc.         LightGBM
                        RandomForest
    ↓              ↓
    └───→ Взвешенное Усреднение ←┘
               ↓
         Выход (Вероятность)
```

## Обновлённая 3D Визуализация

### `generate_3d.py` - Устаревший
Ранее генерировал 3D визуализацию архитектуры с использованием WebGL.

### Текущий статус:
- Устаревший `nn_3d_architecture.html` удалён
- Устаревший `nn_3d_models.html` удалён
- Обновлённый `nn_3d_visualization.html` сохранён для отображения результатов

## Новые функции

### 1. Улучшения для BTC
- Конфигурация мульти-таймфреймов
- BTC-специфичные параметры риска
- Walk-forward валидация для каждого таймфрейма

### 2. Интеграция RL
- DQN агент с Dueling архитектурой
- Walk-forward валидация для RL
- Гибридный ансамбль (Neural + Sklearn + DQN)

### 3. Калибровка вероятностей
- Platt scaling (сигмоид)
- Isotonic regression
- Brier score и Log loss метрики

### 4. Анализ чувствительности к транзакционным издержкам
- Диапазон комиссий: 0.01% - 0.2%
- Диапазон проскальзывания: 0.005% - 0.1%
- Диапазон спреда: 0.01% - 0.2%
- Общая оценка устойчивости

## Рабочий процесс использования

### Для BTC торговли:
```bash
# 1. Тренировка на BTC мульти-таймфрейме
python train_btc.py

# 2. Анализ метрик
python btc_metrics.py

# 3. Тест чувствительности к транзакционным издержкам
python sensitivity_analysis.py
```

### Для RL тренировки:
```bash
# Обучение RL агента с walk-forward
python train_rl_walkforward.py
```

### Для калибровки вероятностей:
```python
from calibration import PlattScaler
from calibrate_probs import calibrate_ensemble_probs

# Калибровка вероятностей ансамбля
platt, results = calibrate_ensemble_probs(ensemble, val_ds, test_ds)
```

## Тестирование

### Запустить все тесты:
```bash
python -m unittest discover -s tests
```

### Запустить конкретный модуль тестов:
```bash
python -m unittest tests.test_model
python -m unittest tests.test_features
```

## Структура файлов

```
nn-trading/
├── export_onnx.py              # Экспорт ONNX и C# обёртка
├── train_btc.py                # Тренировка BTC мульти-таймфрейм
├── train_rl_walkforward.py     # RL с walk-forward
├── calibration.py              # Классы калибровки вероятностей
├── calibrate_probs.py          # Пайплайн калибровки вероятностей
├── sensitivity_analysis.py     # Анализ чувствительности к комиссиям
├── btc_metrics.py              # BTC-специфичные метрики
├── tests/
│   ├── test_core.py
│   ├── test_utils.py
│   ├── test_features.py
│   ├── test_dataset.py
│   ├── test_model.py
│   ├── test_train.py
│   └── test_backtest.py
└── results/
    └── btc_timeframe_comparison.json
```

## Обновления GitHub

### Коммиты:
- `870957d` - docs: добавлена документация по 3D визуализации и новым функциям
- `9fb003b` - refactor: очистка устаревших файлов
- `f23548c` - refactor: очистка устаревших файлов и добавление новых функций

### Отправлено на:
`https://github.com/Cilipep/AI-agent-with-TsLab.git`

## Резюме

✅ **Завершено:**
- Удалены отладочные, тестовые и дублирующиеся файлы
- Очищены старые скрипты оптимизации
- Удалены книги Gerchik и C# индикаторы
- Удалены скрипты загрузки и проверки
- Очищены дополнительные отчётные файлы
- Добавлена тренировка BTC мульти-таймфрейм
- Добавлена walk-forward валидация для RL
- Добавлена калибровка вероятностей (Platt + Isotonic)
- Добавлен анализ чувствительности к транзакционным издержкам
- Добавлены BTC-специфичные метрики
- Создан набор модульных тестов
- Отправлено на GitHub

## Следующие шаги

1. Запустить `python train_btc.py` для тренировки на BTC
2. Запустить `python sensitivity_analysis.py` для тестирования чувствительности к издержкам
3. Запустить `python calibration.py` для тестирования калибровки вероятностей
4. Запустить `python -m unittest discover -s tests` для проверки тестов
