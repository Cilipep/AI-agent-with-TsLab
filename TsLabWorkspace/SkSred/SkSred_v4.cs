using System;
using System.Collections.Generic;
using System.Linq;
using TSLab.Script;
using TSLab.Script.Handlers;

namespace TSLab.Sked
{
    /// <summary>
    /// SkSred v4 — Server-side script
    /// SMA Crossover (5/20) + EMA200 Trend Filter
    /// ATR-based SL/TP + Trailing Stop
    /// Long on instrument 1, Short on instrument 2
    /// Margin: 3-20% (leverage 5x-33x)
    /// </summary>
    public class SkSred_v4 : IExternalScript
    {
        // === SMA Parameters ===
        public int SMA_SHORT = 5;
        public int SMA_LONG = 20;

        // === Trend Filter ===
        public int EMA_PERIOD = 200;

        // === ATR Parameters ===
        public int ATR_PERIOD = 14;
        public double ATR_SL_MULT = 1.5;   // SL = EntryPrice - ATR * 1.5
        public double ATR_TP_MULT = 3.0;   // TP = EntryPrice + ATR * 3.0

        // === Trailing Stop Parameters ===
        public double TRAIL_ACTIVATE_PCT = 0.02;  // Activate at 2% profit
        public double TRAIL_DISTANCE_PCT = 0.015;  // Trail at 1.5% from peak

        // === Position Sizing ===
        public double POSITION_SIZE = 1.0;
        public double COMMISSION_PCT = 0.05;
        public double MARGIN_PCT = 10.0;  // 3-20%

        public void Execute(IContext ctx, ISecurity sec)
        {
            // Get both securities
            ISecurity[] securities = ctx.Securities;
            if (securities.Length < 2)
            {
                ctx.Log("ERROR: Need at least 2 securities (BTC+BNB)", MessageType.Error);
                return;
            }

            ISecurity secBTC = securities[0];  // BTC — Long
            ISecurity secBNB = securities[1];  // BNB — Short

            // === Data for BTC ===
            var closeBTC = ctx.GetData("Close_BTC", secBTC.Bars, () => secBTC.Close);
            var highBTC = ctx.GetData("High_BTC", secBTC.Bars, () => secBTC.High);
            var lowBTC = ctx.GetData("Low_BTC", secBTC.Bars, () => secBTC.Low);

            // === Data for BNB ===
            var closeBNB = ctx.GetData("Close_BNB", secBNB.Bars, () => secBNB.Close);
            var highBNB = ctx.GetData("High_BNB", secBNB.Bars, () => secBNB.High);
            var lowBNB = ctx.GetData("Low_BNB", secBNB.Bars, () => secBNB.Low);

            // === Indicators for BTC ===
            var smaShortBTC = ctx.GetData("SMA_SHORT_BTC", secBTC.Bars, () => closeBTC.SMA(SMA_SHORT));
            var smaLongBTC = ctx.GetData("SMA_LONG_BTC", secBTC.Bars, () => closeBTC.SMA(SMA_LONG));
            var ema200BTC = ctx.GetData("EMA200_BTC", secBTC.Bars, () => closeBTC.EMA(EMA_PERIOD));
            var atrBTC = ctx.GetData("ATR_BTC", secBTC.Bars, () => highBTC.AverageTrueRange(lowBTC, closeBTC, ATR_PERIOD));

            // === Indicators for BNB ===
            var smaShortBNB = ctx.GetData("SMA_SHORT_BNB", secBNB.Bars, () => closeBNB.SMA(SMA_SHORT));
            var smaLongBNB = ctx.GetData("SMA_LONG_BNB", secBNB.Bars, () => closeBNB.SMA(SMA_LONG));
            var ema200BNB = ctx.GetData("EMA200_BNB", secBNB.Bars, () => closeBNB.EMA(EMA_PERIOD));
            var atrBNB = ctx.GetData("ATR_BNB", secBNB.Bars, () => highBNB.AverageTrueRange(lowBNB, closeBNB, ATR_PERIOD));

            // === Signals for BTC (Long) ===
            var longEntryBTC = ctx.GetData("LongEntry_BTC", secBTC.Bars, () =>
                (smaShortBTC[0] > smaLongBTC[0]) & (smaShortBTC[1] <= smaLongBTC[1]) & (closeBTC[0] > ema200BTC[0]));

            var longExitBTC = ctx.GetData("LongExit_BTC", secBTC.Bars, () =>
                (smaShortBTC[0] < smaLongBTC[0]) & (smaShortBTC[1] >= smaLongBTC[1]));

            // === Signals for BNB (Short) ===
            var shortEntryBNB = ctx.GetData("ShortEntry_BNB", secBNB.Bars, () =>
                (smaShortBNB[0] < smaLongBNB[0]) & (smaShortBNB[1] >= smaLongBNB[1]) & (closeBNB[0] < ema200BNB[0]));

            var shortExitBNB = ctx.GetData("ShortExit_BNB", secBNB.Bars, () =>
                (smaShortBNB[0] > smaLongBNB[0]) & (smaShortBNB[1] <= smaLongBNB[1]));

            // Leverage from margin
            double leverage = 100.0 / MARGIN_PCT;

            // ============================
            // LONG MANAGEMENT (BTC)
            // ============================
            var posBTC = secBTC.Position;
            double trailHighBTC = 0;
            bool trailActivatedBTC = false;

            for (int i = ctx.DateFirstTick; i < ctx.DateLastTick; i++)
            {
                double currentPriceBTC = closeBTC[i];
                double highPriceBTC = highBTC[i];
                double lowPriceBTC = lowBTC[i];
                double currentATRBTC = atrBTC[i];

                // === Manage open Long position ===
                if (posBTC.IsActive)
                {
                    double entryPrice = posBTC.GetOpenPrice(i);
                    double slLevel = entryPrice - (currentATRBTC * ATR_SL_MULT);
                    double tpLevel = entryPrice + (currentATRBTC * ATR_TP_MULT);

                    // Update trailing stop
                    if (!trailActivatedBTC)
                    {
                        double unrealizedPct = (highPriceBTC - entryPrice) / entryPrice;
                        if (unrealizedPct >= TRAIL_ACTIVATE_PCT)
                        {
                            trailActivatedBTC = true;
                            trailHighBTC = highPriceBTC;
                        }
                    }
                    else
                    {
                        trailHighBTC = Math.Max(trailHighBTC, highPriceBTC);
                    }

                    // Check Stop Loss (ATR-based, uses Low)
                    if (lowPriceBTC <= slLevel)
                    {
                        posBTC.CloseAtMarket(i + 1);
                        trailActivatedBTC = false;
                        continue;
                    }

                    // Check Take Profit (ATR-based, uses High)
                    if (highPriceBTC >= tpLevel)
                    {
                        posBTC.CloseAtMarket(i + 1);
                        trailActivatedBTC = false;
                        continue;
                    }

                    // Check Trailing Stop
                    if (trailActivatedBTC && lowPriceBTC <= trailHighBTC * (1 - TRAIL_DISTANCE_PCT))
                    {
                        posBTC.CloseAtMarket(i + 1);
                        trailActivatedBTC = false;
                        continue;
                    }

                    // Exit on Death Cross
                    if (longExitBTC[i])
                    {
                        posBTC.CloseAtMarket(i + 1);
                        trailActivatedBTC = false;
                    }
                }

                // === Open Long on Golden Cross ===
                if (!posBTC.IsActive && longEntryBTC[i])
                {
                    posBTC.BuyAtMarket(i + 1, POSITION_SIZE);
                    trailActivatedBTC = false;
                    trailHighBTC = currentPriceBTC;
                }
            }

            // ============================
            // SHORT MANAGEMENT (BNB)
            // ============================
            var posBNB = secBNB.Position;
            double trailLowBNB = double.MaxValue;
            bool trailActivatedBNB = false;

            for (int i = ctx.DateFirstTick; i < ctx.DateLastTick; i++)
            {
                double currentPriceBNB = closeBNB[i];
                double highPriceBNB = highBNB[i];
                double lowPriceBNB = lowBNB[i];
                double currentATRBNB = atrBNB[i];

                // === Manage open Short position ===
                if (posBNB.IsActive)
                {
                    double entryPrice = posBNB.GetOpenPrice(i);
                    double slLevel = entryPrice + (currentATRBNB * ATR_SL_MULT);   // SL above entry for short
                    double tpLevel = entryPrice - (currentATRBNB * ATR_TP_MULT);   // TP below entry for short

                    // Update trailing stop
                    if (!trailActivatedBNB)
                    {
                        double unrealizedPct = (entryPrice - lowPriceBNB) / entryPrice;
                        if (unrealizedPct >= TRAIL_ACTIVATE_PCT)
                        {
                            trailActivatedBNB = true;
                            trailLowBNB = lowPriceBNB;
                        }
                    }
                    else
                    {
                        trailLowBNB = Math.Min(trailLowBNB, lowPriceBNB);
                    }

                    // Check Stop Loss (ATR-based, uses High for short)
                    if (highPriceBNB >= slLevel)
                    {
                        posBNB.CloseAtMarket(i + 1);
                        trailActivatedBNB = false;
                        continue;
                    }

                    // Check Take Profit (ATR-based, uses Low for short)
                    if (lowPriceBNB <= tpLevel)
                    {
                        posBNB.CloseAtMarket(i + 1);
                        trailActivatedBNB = false;
                        continue;
                    }

                    // Check Trailing Stop
                    if (trailActivatedBNB && highPriceBNB >= trailLowBNB * (1 + TRAIL_DISTANCE_PCT))
                    {
                        posBNB.CloseAtMarket(i + 1);
                        trailActivatedBNB = false;
                        continue;
                    }

                    // Exit on Golden Cross
                    if (shortExitBNB[i])
                    {
                        posBNB.CloseAtMarket(i + 1);
                        trailActivatedBNB = false;
                    }
                }

                // === Open Short on Death Cross ===
                if (!posBNB.IsActive && shortEntryBNB[i])
                {
                    posBNB.SellAtMarket(i + 1, POSITION_SIZE);
                    trailActivatedBNB = false;
                    trailLowBNB = currentPriceBNB;
                }
            }

            // === Log summary ===
            ctx.Log($"SkSred v4 | BTC Long: {posBTC.PositionsCount} trades, BNB Short: {posBNB.PositionsCount} trades", MessageType.Info);
            ctx.Log($"Params: SMA({SMA_SHORT}/{SMA_LONG}) EMA{EMA_PERIOD} ATR({ATR_SL_MULT}x/{ATR_TP_MULT}x) Trail({TRAIL_ACTIVATE_PCT*100}%/{TRAIL_DISTANCE_PCT*100}%) Margin={MARGIN_PCT}%", MessageType.Info);
        }
    }
}
