using System;
using System.Collections.Generic;
using TSLab.Script;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(1)]
[Input(0, TemplateTypes.SECURITY)]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class NNTradingIndicator : IBar2DoubleHandler
{
    [HandlerParameter(true, "30", Min = "10", Max = "100", Step = "1")]
    public int Window { get; set; } = 30;

    [HandlerParameter(true, "0.5", Min = "0.1", Max = "0.9", Step = "0.05")]
    public double Threshold { get; set; } = 0.5;

    public IList<double> Execute(ISecurity source)
    {
        if (source == null || source.Bars == null || source.Bars.Count < Window)
            return Array.Empty<double>();

        var bars = source.Bars;
        var count = bars.Count;
        var result = new double[count];

        var closes = new double[count];
        for (int i = 0; i < count; i++)
            closes[i] = bars[i].Close;

        var rsi = ComputeRSI(closes, 14);
        var ema12 = ComputeEMA(closes, 12);
        var ema26 = ComputeEMA(closes, 26);
        var macd = new double[count];
        for (int i = 0; i < count; i++)
            macd[i] = ema12[i] - ema26[i];
        var macdSignal = ComputeEMA(macd, 9);

        for (int i = Window; i < count; i++)
        {
            double rsiScore = rsi[i] < 30 ? 1.0 : (rsi[i] > 70 ? 0.0 : 0.5);
            double macdScore = macd[i] > macdSignal[i] ? 0.7 : 0.3;
            double trendScore = ema12[i] > ema26[i] ? 0.6 : 0.4;
            result[i] = rsiScore * 0.4 + macdScore * 0.3 + trendScore * 0.3;
        }
        return result;
    }

    private double[] ComputeRSI(double[] closes, int period)
    {
        var rsi = new double[closes.Length];
        if (closes.Length < period + 1) return rsi;
        double avgGain = 0, avgLoss = 0;
        for (int i = 1; i <= period; i++)
        {
            double change = closes[i] - closes[i - 1];
            if (change > 0) avgGain += change; else avgLoss -= change;
        }
        avgGain /= period; avgLoss /= period;
        rsi[period] = avgLoss == 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);
        for (int i = period + 1; i < closes.Length; i++)
        {
            double change = closes[i] - closes[i - 1];
            avgGain = (avgGain * (period - 1) + (change > 0 ? change : 0)) / period;
            avgLoss = (avgLoss * (period - 1) + (change < 0 ? -change : 0)) / period;
            rsi[i] = avgLoss == 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);
        }
        return rsi;
    }

    private double[] ComputeEMA(double[] data, int period)
    {
        var ema = new double[data.Length];
        if (data.Length == 0) return ema;
        double multiplier = 2.0 / (period + 1);
        ema[0] = data[0];
        for (int i = 1; i < data.Length; i++)
            ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1];
        return ema;
    }
}
