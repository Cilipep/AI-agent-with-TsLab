using System;
using System.Collections.Generic;
using System.Linq;
using TSLab.Script;
using TSLab.Script.Handlers;

namespace TSLab.Sked
{
    /// <summary>
    /// SkSred ATR-Adaptive Strategy
    /// SMA Crossover (10/30) + EMA200 Trend Filter + ATR-based SL/TP
    /// For BTC+BNB on H4
    /// </summary>
    public class SkSredATR : IExternalScript
    {
        // === Parameters ===
        public int SMA_SHORT = 10;
        public int SMA_LONG = 30;
        public int EMA_PERIOD = 200;
        public int ATR_PERIOD = 14;
        public double ATR_SL_MULT = 1.5;   // SL = EntryPrice - ATR * 1.5
        public double ATR_TP_MULT = 3.0;   // TP = EntryPrice + ATR * 3.0
        public double POSITION_SIZE = 1.0;
        public double COMMISSION_PCT = 0.05;

        public void Execute(IContext ctx, ISecurity sec)
        {
            // === Data ===
            var close = ctx.GetData("Close", sec.Bars, () => sec.Close);
            var high = ctx.GetData("High", sec.Bars, () => sec.High);
            var low = ctx.GetData("Low", sec.Bars, () => sec.Low);

            // === Indicators ===
            var smaShort = ctx.GetData("SMA_SHORT", sec.Bars, () => close.SMA(SMA_SHORT));
            var smaLong = ctx.GetData("SMA_LONG", sec.Bars, () => close.SMA(SMA_LONG));
            var ema200 = ctx.GetData("EMA200", sec.Bars, () => close.EMA(EMA_PERIOD));
            var atr = ctx.GetData("ATR", sec.Bars, () => high.AverageTrueRange(low, close, ATR_PERIOD));

            // === Signals ===
            var goldenCross = ctx.GetData("GoldenCross", sec.Bars, () =>
                (smaShort[0] > smaLong[0]) & (smaShort[1] <= smaLong[1]) & (close[0] > ema200[0]));

            var deathCross = ctx.GetData("DeathCross", sec.Bars, () =>
                (smaShort[0] < smaLong[0]) & (smaShort[1] >= smaLong[1]) & (close[0] < ema200[0]));

            // === Position Management ===
            var pos = sec.Position;

            for (int i = ctx.DateFirstTick; i < ctx.DateLastTick; i++)
            {
                // Open Long on Golden Cross
                if (goldenCross[i] && !pos.IsActive)
                {
                    sec.Position.BuyAtMarket(i + 1, POSITION_SIZE);
                }

                // Manage open position with ATR-based SL/TP
                if (pos.IsActive)
                {
                    double entryPrice = pos.GetOpenPrice(i);
                    double currentATR = atr[i];
                    double currentClose = close[i];

                    // ATR-adaptive levels based on ENTRY PRICE
                    double slLevel = entryPrice - (currentATR * ATR_SL_MULT);
                    double tpLevel = entryPrice + (currentATR * ATR_TP_MULT);

                    // Check Stop Loss
                    if (currentClose <= slLevel || low[i] <= slLevel)
                    {
                        sec.Position.CloseAtMarket(i + 1);
                        continue;
                    }

                    // Check Take Profit
                    if (currentClose >= tpLevel || high[i] >= tpLevel)
                    {
                        sec.Position.CloseAtMarket(i + 1);
                        continue;
                    }

                    // Exit on Death Cross
                    if (deathCross[i])
                    {
                        sec.Position.CloseAtMarket(i + 1);
                    }
                }
            }
        }
    }
}
