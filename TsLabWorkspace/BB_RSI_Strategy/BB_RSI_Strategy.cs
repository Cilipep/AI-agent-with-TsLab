using System;
using System.Collections.Generic;
using System.Linq;
using TSLab.Script;
using TSLab.Script.Handlers;

namespace TSLab.Script.Strategies
{
    /// <summary>
    /// BB_RSI_Strategy - Стратегия на Bollinger Bands + RSI + EMA фильтр тренда
    /// Таймфрейм: M15
    /// Инструмент: AVAXUSD_PERP
    /// Начальный баланс: 30 USDT
    /// </summary>
    public class BB_RSI_Strategy : IExternalScript
    {
        // ==================== ПАРАМЕТРЫ ====================
        
        // Bollinger Bands
        public int BB_Period { get; set; } = 15;
        public double BB_Coef { get; set; } = 3.0;
        
        // RSI
        public int RSI_Period { get; set; } = 15;
        
        // EMA фильтр тренда
        public int EMA_Period { get; set; } = 50;
        
        // SMA для средней линии BB
        public int SMA_Period { get; set; } = 35;
        
        // Комиссия
        public double Commission { get; set; } = 0.001;
        
        // Размер позиции
        public int Shares { get; set; } = 1;

        public void Execute(IContext ctx, ISecurity sec)
        {
            // ==================== ИНИЦИАЛИЗАЦИЯ ИНДИКАТОРОВ ====================
            
            // Bollinger Bands
            var bb_upper = ctx.GetData("BB_Upper", new[] { BB_Period, BB_Coef }, 
                () => sec.ClosePrices.BollingerBands(BB_Period, BB_Coef, BollingerBounds.Upper));
            
            var bb_lower = ctx.GetData("BB_Lower", new[] { BB_Period, BB_Coef }, 
                () => sec.ClosePrices.BollingerBands(BB_Period, BB_Coef, BollingerBounds.Lower));
            
            var bb_middle = ctx.GetData("BB_Middle", new[] { SMA_Period }, 
                () => sec.ClosePrices.SMA(SMA_Period));
            
            // RSI
            var rsi = ctx.GetData("RSI", new[] { RSI_Period }, 
                () => sec.ClosePrices.RSI(RSI_Period));
            
            // EMA для фильтра тренда
            var ema_trend = ctx.GetData("EMA_Trend", new[] { EMA_Period }, 
                () => sec.ClosePrices.EMA(EMA_Period));
            
            // Ценовые данные
            var close = sec.ClosePrices;
            var low = sec.LowPrices;
            var high = sec.HighPrices;
            var open = sec.OpenPrices;

            // ==================== ОСНОВНОЙ ЦИКЛ ====================
            
            for (int i = 1; i < ctx.BarsCount; i++)
            {
                // Пропускаем начальные бары для прогрева индикаторов
                if (i < Math.Max(BB_Period, Math.Max(RSI_Period, EMA_Period)))
                    continue;

                // ==================== УСЛОВИЯ ВХОДА ====================
                
                // Условие для лонга: цена закрытия ниже нижней полосы Боллинджера
                bool longCondition = close[i] < bb_lower[i];
                
                // Условие для шорта: цена закрытия выше верхней полосы Боллинджера
                bool shortCondition = close[i] > bb_upper[i];
                
                // Фильтр тренда: цена выше EMA (для лонга)
                bool priceAboveEMA = close[i] > ema_trend[i];
                
                // Фильтр тренда: цена ниже EMA (для шорта)
                bool priceBelowEMA = close[i] < ema_trend[i];
                
                // ==================== КОМБИНИРОВАННЫЕ УСЛОВИЯ ====================
                
                // Вход в лонг: перепроданность + тренд вверх
                bool andLong = longCondition && priceBelowEMA;
                
                // Вход в шорт: перекупленность + тренд вниз
                bool andShort = shortCondition && priceAboveEMA;

                // ==================== ТОРГОВЫЕ ОПЕРАЦИИ ====================
                
                // Проверяем текущую позицию
                var position = sec.Positions.GetActivePositionForBar(i);
                
                if (position == null)
                {
                    // Нет позиции - ищем вход
                    
                    if (andLong)
                    {
                        // Открытие лонга по рынку
                        sec.Positions.BuyAtMarket(i + 1, Shares, "LongEntry");
                    }
                    else if (andShort)
                    {
                        // Открытие шорта по рынку
                        sec.Positions.SellAtMarket(i + 1, Shares, "ShortEntry");
                    }
                }
                else
                {
                    // Есть позиция - проверяем выход
                    
                    if (position.IsLong)
                    {
                        // Лонг позиция
                        
                        // Выход при сигнале на шорт
                        if (andShort)
                        {
                            sec.Positions.CloseAtMarket(i + 1, "LongExit_Signal");
                        }
                        // Стоп-лосс: Low свечи
                        else if (low[i] < position.EntryPrice)
                        {
                            sec.Positions.CloseAtMarket(i + 1, "LongExit_StopLoss");
                        }
                        // Тейк-профит: средняя линия Боллинджера
                        else if (close[i] > bb_middle[i])
                        {
                            sec.Positions.CloseAtMarket(i + 1, "LongExit_TakeProfit");
                        }
                    }
                    else
                    {
                        // Шорт позиция
                        
                        // Выход при сигнале на лонг
                        if (andLong)
                        {
                            sec.Positions.CloseAtMarket(i + 1, "ShortExit_Signal");
                        }
                        // Стоп-лосс: High свечи
                        else if (high[i] > position.EntryPrice)
                        {
                            sec.Positions.CloseAtMarket(i + 1, "ShortExit_StopLoss");
                        }
                        // Тейк-профит: средняя линия Боллинджера
                        else if (close[i] < bb_middle[i])
                        {
                            sec.Positions.CloseAtMarket(i + 1, "ShortExit_TakeProfit");
                        }
                    }
                }
            }
        }
    }
}
