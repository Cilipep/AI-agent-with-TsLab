using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using TSLab.Script;
using TSLab.Script.Handlers;
using TSLab.Script.Helpers;

namespace TrendBot
{
    /// <summary>
    /// TrendBot v1 — Trend Following Signal
    /// Returns 1 for uptrend, -1 for downtrend, 0 for neutral
    /// </summary>
    [HandlerCategory(HandlerCategories.Indicators)]
    [Description("TrendBot v1: EMA60/150 crossover signal (1=long, -1=short)")]
    [InputsCount(1)]
    [Input(0, TemplateTypes.SECURITY, false, "Security")]
    [OutputType(TemplateTypes.DOUBLE)]
    public class TrendBotHandler : IStreamHandler, IContextUses
    {
        public IContext Context { get; set; }

        [HandlerParameter(true, "60", Min = "10", Max = "200", Step = "5")]
        public int EMA_FAST { get; set; } = 60;

        [HandlerParameter(true, "150", Min = "50", Max = "300", Step = "10")]
        public int EMA_SLOW { get; set; } = 150;

        public IList<double> Execute(ISecurity sec)
        {
            int barsCount = sec.Bars.Count;
            var result = Context.GetArray<double>(barsCount);

            var close = sec.ClosePrices;

            // Calculate EMAs
            var emaFast = Series.EMA((IReadOnlyList<double>)close.AsReadOnly(), EMA_FAST);
            var emaSlow = Series.EMA((IReadOnlyList<double>)close.AsReadOnly(), EMA_SLOW);

            for (int i = 0; i < barsCount; i++)
            {
                if (double.IsNaN(emaFast[i]) || double.IsNaN(emaSlow[i]))
                {
                    result[i] = 0;
                    continue;
                }

                // Return signal: 1 for uptrend, -1 for downtrend
                if (emaFast[i] > emaSlow[i])
                    result[i] = 1;  // Uptrend - long signal
                else
                    result[i] = -1;  // Downtrend - short/exit signal
            }

            return result;
        }
    }
}
