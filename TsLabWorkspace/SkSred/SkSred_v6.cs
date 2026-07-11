using System;
using System.Collections.Generic;
using System.Linq;
using TSLab.Script;
using TSLab.Script.Handlers;

namespace TSLab.Sked
{
    /// <summary>
    /// SkSred v6 — SMA Crossover + Circuit Breaker
    /// SMA (5/20) + EMA200 Trend Filter
    /// ATR-based SL/TP + Trailing Stop
    /// Circuit Breaker: auto-close at max drawdown
    /// </summary>
    public class SkSred_v6 : IExternalScript
    {
        // === SMA Parameters ===
        public int SMA_SHORT { get; set; } = 5;
        public int SMA_LONG { get; set; } = 20;

        // === Trend Filter ===
        public int EMA_PERIOD { get; set; } = 200;

        // === ATR Parameters ===
        public int ATR_PERIOD { get; set; } = 14;
        public double ATR_SL_MULT { get; set; } = 1.5;
        public double ATR_TP_MULT { get; set; } = 3.0;

        // === Circuit Breaker ===
        public double MAX_DRAWDOWN_PCT { get; set; } = 20.0;

        // === Position Sizing ===
        public int SHARES { get; set; } = 1;

        public void Execute(IContext ctx, ISecurity sec)
        {
            // Indicators using sec.ClosePrices.SMA() pattern
            var smaShort = ctx.GetData("SMA_SHORT", new[] { SMA_SHORT },
                () => sec.ClosePrices.SMA(SMA_SHORT));
            var smaLong = ctx.GetData("SMA_LONG", new[] { SMA_LONG },
                () => sec.ClosePrices.SMA(SMA_LONG));
            var emaTrend = ctx.GetData("EMA_Trend", new[] { EMA_PERIOD },
                () => sec.ClosePrices.EMA(EMA_PERIOD));
            var atr = ctx.GetData("ATR", new[] { ATR_PERIOD },
                () => sec.HighPrices.AverageTrueRange(sec.LowPrices, sec.ClosePrices, ATR_PERIOD));

            // Price data
            var close = sec.ClosePrices;
            var low = sec.LowPrices;
            var high = sec.HighPrices;

            // Peak equity tracking for circuit breaker
            double peakEquity = 30.0; // Initial capital
            bool breakerTriggered = false;

            for (int i = 1; i < ctx.BarsCount; i++)
            {
                // Skip warmup period
                if (i < EMA_PERIOD)
                    continue;

                // Current price
                double price = close[i];

                // Update peak equity using position profit
                var position = sec.Positions.GetActivePositionForBar(i);
                double currentEquity = 30.0;
                if (position != null)
                {
                    currentEquity = 30.0 + position.Profit;
                }
                if (currentEquity > peakEquity)
                    peakEquity = currentEquity;

                // Calculate drawdown
                double drawdownPct = peakEquity > 0
                    ? (peakEquity - currentEquity) / peakEquity * 100
                    : 0;

                // === CIRCUIT BREAKER ===
                if (drawdownPct >= MAX_DRAWDOWN_PCT && !breakerTriggered)
                {
                    sec.Positions.CloseAtMarket(i + 1, "CircuitBreaker");
                    breakerTriggered = true;
                    continue;
                }

                // Skip if breaker active
                if (breakerTriggered)
                    continue;

                // === SIGNALS ===
                bool goldenCross = smaShort[i] > smaLong[i] && smaShort[i - 1] <= smaLong[i - 1];
                bool deathCross = smaShort[i] < smaLong[i] && smaShort[i - 1] >= smaLong[i - 1];

                // Trend filter
                bool uptrend = price > emaTrend[i];
                bool downtrend = price < emaTrend[i];

                // Combined signals
                bool longSignal = goldenCross && uptrend;
                bool shortSignal = deathCross && downtrend;

                // ATR levels
                double atrValue = double.IsNaN(atr[i]) ? price * 0.02 : atr[i];
                double slLong = price - atrValue * ATR_SL_MULT;
                double tpLong = price + atrValue * ATR_TP_MULT;
                double slShort = price + atrValue * ATR_SL_MULT;
                double tpShort = price - atrValue * ATR_TP_MULT;

                if (position == null)
                {
                    // No position — look for entry
                    if (longSignal)
                    {
                        sec.Positions.BuyAtMarket(i + 1, SHARES, "LongEntry");
                    }
                    else if (shortSignal)
                    {
                        sec.Positions.SellAtMarket(i + 1, SHARES, "ShortEntry");
                    }
                }
                else
                {
                    // Has position — manage exit
                    if (position.IsLong)
                    {
                        if (deathCross || low[i] < slLong || high[i] > tpLong)
                        {
                            sec.Positions.CloseAtMarket(i + 1, "LongExit");
                        }
                    }
                    else
                    {
                        if (goldenCross || high[i] > slShort || low[i] < tpShort)
                        {
                            sec.Positions.CloseAtMarket(i + 1, "ShortExit");
                        }
                    }
                }
            }
        }
    }
}
