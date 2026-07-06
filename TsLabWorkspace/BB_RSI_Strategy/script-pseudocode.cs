// =====================================================
// BB_RSI_Strategy - Стратегия на Bollinger Bands + RSI
// TSLab Visual Script (псевдокод)
// =====================================================

// ==================== НАСТРОЙКИ ====================
// Инструмент:    AVAXUSD_PERP
// Таймфрейм:     M15
// Начальный баланс: 30 USDT
// Комиссия:      0.1%

// ==================== ИНДИКАТОРЫ ====================

// Bollinger Bands (Верхняя полоса)
BB_Upper = BollingerBands1(ClosePrice, Period=15, Coef=3)

// Bollinger Bands (Нижняя полоса)
BB_Lower = BollingerBands2(ClosePrice, Period=15, Coef=3)

// Bollinger Bands (Средняя линия - SMA)
BB_Middle = SMA(ClosePrice, Period=35)

// RSI индикатор
RSI = RSI(ClosePrice, Period=15)

// EMA для фильтра тренда
EMA_Trend = EMA(ClosePrice, Period=50)

// ==================== ЦЕНОВЫЕ ДАННЫЕ ====================
ClosePrice = Close(Security)
LowPrice = Low(Security)
HighPrice = High(Security)
OpenPrice = Open(Security)

// ==================== УСЛОВИЯ ВХОДА ====================

// Условие для лонга: цена закрытия ниже нижней полосы Боллинджера
LongCondition = (ClosePrice < BB_Lower)

// Условие для шорта: цена закрытия выше верхней полосы Боллинджера
ShortCondition = (ClosePrice > BB_Upper)

// Фильтр тренда: цена выше EMA (для лонга)
PriceAboveEMA = (ClosePrice > EMA_Trend)

// Фильтр тренда: цена ниже EMA (для шорта)
PriceBelowEMA = (ClosePrice < EMA_Trend)

// ==================== КОМБИНИРОВАННЫЕ УСЛОВИЯ ====================

// Вход в лонг: перепроданность + тренд вверх
AndLong = (LongCondition AND PriceBelowEMA)

// Вход в шорт: перекупленность + тренд вниз
AndShort = (ShortCondition AND PriceAboveEMA)

// ==================== ТОРГОВЫЕ ОПЕРАЦИИ ====================

// Открытие лонга по рынку
OpenLong = OpenPositionByMarket(
    Security,
    Condition = AndLong,
    Long = true,
    Shares = 1
)

// Открытие шорта по рынку
OpenShort = OpenPositionByMarket(
    Security,
    Condition = AndShort,
    Long = false,
    Shares = 1
)

// Закрытие лонга (при сигнале на шорт)
CloseLong = ClosePositionByMarket(
    Position = OpenLong,
    Condition = AndShort
)

// Закрытие шорта (при сигнале на лонг)
CloseShort = ClosePositionByMarket(
    Position = OpenShort,
    Condition = AndLong
)

// ==================== СТОП-ПРИКАЗЫ ====================

// Стоп-лосс для лонга: экстремум свечи (Low)
StopLong = ClosePositionByStop(
    Position = OpenLong,
    Price = LowPrice,
    Slippage = 0
)

// Тейк-профит для лонга: средняя линия Боллинджера
ProfitLong = ClosePositionByProfit(
    Position = OpenLong,
    Price = BB_Middle,
    Slippage = 0
)

// Стоп-лосс для шорта: экстремум свечи (High)
StopShort = ClosePositionByStop(
    Position = OpenShort,
    Price = HighPrice,
    Slippage = 0
)

// Тейк-профит для шорта: средняя линия Боллинджера
ProfitShort = ClosePositionByProfit(
    Position = OpenShort,
    Price = BB_Middle,
    Slippage = 0
)

// ==================== КОМИССИЯ ====================
Commission = RelativeCommission(Security, Value=0.001)

// ==================== ЛОГИКА РАБОТЫ ====================
//
// 1. ВХОД В ЛОНГ:
//    - Цена закрытия ниже нижней полосы Боллинджера (перепроданность)
//    - Цена выше EMA(50) (тренд вверх)
//
// 2. ВХОД В ШОРТ:
//    - Цена закрытия выше верхней полосы Боллинджера (перекупленность)
//    - Цена ниже EMA(50) (тренд вниз)
//
// 3. ВЫХОД:
//    - При достижении противоположной полосы Боллинджера
//    - Или при срабатывании стоп-лосса
//
// 4. СТОП-ЛОСС:
//    - Лонг: Low свечи
//    - Шорт: High свечи
//
// 5. ТЕЙК-ПРОФИТ:
//    - Средняя линия Боллинджера (SMA)
//
