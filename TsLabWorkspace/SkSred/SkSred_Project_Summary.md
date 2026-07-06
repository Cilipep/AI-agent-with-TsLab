# SkSred Project Summary

## Текущее состояние проекта

### TSLab Script
- **Имя**: SkSred
- **ID**: a795553c-baea-43f0-be45-25515c4d86c7
- **Блоков**: 14
- **Связей**: 22
- **Датасource**: BinanceCoin-MFutures
- **Таймфрейм**: H1 (60 мин)
- **Период**: 30.04.2026 – 29.06.2026

### Мультивалютность
| Источник | Инструмент | Описание |
|----------|------------|----------|
| Src | DOGEUSD_PERP | Основной инструмент |
| Src1 | NEARUSD_PERP | Второй инструмент |

### Параметры по умолчанию
| Параметр | Значение |
|----------|----------|
| SMA1 (быстрая) | 5 |
| SMA2 (медленная) | 20 |
| Комиссия | 0.05% |

### Структура блоков
```
Цепочка 1 — DOGEUSD_PERP:
Src → SMA1(5) + SMA2(20) → GoldenCross → OpenLong
                              DeathCross → CloseLong
Commission (0.05%)

Цепочка 2 — NEARUSD_PERP:
Src1 → SMA1_1(5) + SMA2_1(20) → GoldenCross_1 → OpenLong_1
                                  DeathCross_1 → CloseLong_1
Commission1 (0.05%)
```

### Формулы
- **GoldenCross**: `SMA1 > SMA2 and SMA1[-1] <= SMA2[-1]`
- **DeathCross**: `SMA1 < SMA2 and SMA1[-1] >= SMA2[-1]`

## История исправлений

### 03.07.2026
1. Удалён пустой блок Close1 (без обработчика)
2. Добавлен блок Close (TSLab.Script.Handlers.Close) между Src и SMA
3. Удалены пустые блоки SL_Level, TP_Level, StopLoss, TakeProfit
4. Удалены пустые блоки SMA2_threshold_1, SMA2_threshold_2
5. Исправлены соединения Close→SMA через десктопный редактор
6. Добавлена мультивалютность: Src1 (NEARUSD_PERP) + Commission1
7. Добавлена торговая цепочка для NEAR: SMA1_1, SMA2_1, GoldenCross_1, DeathCross_1, OpenLong_1, CloseLong_1

### Известные ограничения API
- TSLab API не сохраняет атрибут `ToPort` в XML viewModel при PUT/json и ops
- Соединения типа Src→SMA создаются без `ToPort="Input0"` и не распознаются runtime
- Решение: перетаскивать линии в десктопном редакторе вручную

## Оптимизированные параметры (v4, Python)

### Для NEARUSD_PERP (H4)
| Параметр | Значение |
|----------|----------|
| SMA_SHORT | 7 |
| SMA_LONG | 20 |
| EMA_TREND | 200 |
| ATR_SL_MULT | 1.5 |
| ATR_TP_MULT | 3.0 |

### Для XLMUSD_PERP (H4)
| Параметр | Значение |
|----------|----------|
| SMA_SHORT | 5 |
| SMA_LONG | 15 |
| EMA_TREND | 200 |
| ATR_SL_MULT | 1.5 |
| ATR_TP_MULT | 3.0 |

## Результаты бэктестов (v4, Python)

| Инструмент | Доходность | Сделок | Прибыльных | Profit Factor | Max DD |
|------------|-----------|--------|------------|---------------|--------|
| NEARUSD_PERP (50$×5) | +210.72% | 10 | 90% | 43.31 | 3.03% |
| XLMUSD_PERP (50$×5) | +248.88% | 14 | 85.7% | 7.69 | 17.15% |
| XTZUSD_PERP (60$×5) | +83.90% | 14 | 64.3% | 2.21 | 21.08% |

## Файлы проекта

### TSLab
- `SkSred.tscript` — экспорт скрипта (оригинал)
- `SkSred_TSLab_Graph.json` — текущий граф (после всех правок)
- `SkSred_TSLab_Full.json` — полные настройки с mappings

### Python скрипты
- `skred_backtest_v4.py` — основной бэктест v4
- `skred_optimize_periods.py` — оптимизатор периодов
- `download_binance_data.py` — загрузчик данных

### Отчеты
- `SkSred_Report.docx` — основной отчет
- `SkSred_v4_Report.docx` — отчет по v4

### Данные
- `market_data/ALL_INSTRUMENTS_H1_60d.csv`
- `market_data/ALL_INSTRUMENTS_H4_60d.csv`
- `market_data/ALL_INSTRUMENTS_D1_60d.csv`
- CSV-файлы в `C:\Users\i59400f\Documents\TSLab 3.0\` (20 инструментов, 5м, 60 дней)

## Рекомендации
1. Добавить EMA 200 фильтр и ATR SL/TP (как в v4)
2. Оптимизировать периоды SMA для каждого инструмента
3. Добавить управление рисками

## Дата обновления
04.07.2026
