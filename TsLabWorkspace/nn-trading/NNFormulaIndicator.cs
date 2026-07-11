using System;
using System.Collections.Generic;
using TSLab.Script;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(1)]
[Input(0, TemplateTypes.SECURITY)]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class NNFormulaIndicator : IBar2DoubleHandler
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

        // Compute indicators
        var rsi = ComputeRSI(closes, 14);
        var ema12 = ComputeEMA(closes, 12);
        var ema26 = ComputeEMA(closes, 26);
        var macd = new double[count];
        for (int i = 0; i < count; i++)
            macd[i] = ema12[i] - ema26[i];
        var macdSignal = ComputeEMA(macd, 9);
        var bb = ComputeBollinger(closes, 20);
        var atr = ComputeATR(bars, 14);

        // Neural network-like signal combining multiple indicators
        for (int i = Window; i < count; i++)
        {
            // RSI signal (0-1)
            double rsiSignal = rsi[i] < 30 ? 1.0 : (rsi[i] > 70 ? 0.0 : 0.5);

            // MACD signal (0-1)
            double macdSignal_val = macd[i] > macdSignal[i] ? 0.7 : 0.3;

            // Trend signal (0-1)
            double trendSignal = ema12[i] > ema26[i] ? 0.6 : 0.4;

            // Bollinger signal (0-1)
            double bbSignal = 0.5;
            if (bb[i].upper > 0 && bb[i].lower > 0)
            {
                double bbPos = (closes[i] - bb[i].lower) / (bb[i].upper - bb[i].lower);
                bbSignal = bbPos < 0.2 ? 0.8 : (bbPos > 0.8 ? 0.2 : 0.5);
            }

            // Volume trend (simplified)
            double volSignal = 0.5;

            // Combined signal (weighted average like neural network)
            result[i] = rsiSignal * 0.25 +
                        macdSignal_val * 0.20 +
                        trendSignal * 0.20 +
                        bbSignal * 0.20 +
                        volSignal * 0.15;
        }

        return result;
    }

    private struct Bollinger
    {
        public double upper, middle, lower;
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

    private Bollinger[] ComputeBollinger(double[] closes, int period)
    {
        var result = new Bollinger[closes.Length];
        for (int i = period; i < closes.Length; i++)
        {
            double sum = 0, sumSq = 0;
            for (int j = i - period; j < i; j++)
            {
                sum += closes[j];
                sumSq += closes[j] * closes[j];
            }
            double mean = sum / period;
            double std = Math.Sqrt(sumSq / period - mean * mean);
            result[i].middle = mean;
            result[i].upper = mean + 2 * std;
            result[i].lower = mean - 2 * std;
        }
        return result;
    }

    private double ComputeATR(object barsObj, int period)
    {
        dynamic bars = barsObj;
        if (bars == null || bars.Count < period + 1) return 0;
        double sum = 0;
        int start = Math.Max(1, bars.Count - period);
        for (int i = start; i < bars.Count; i++)
        {
            double tr = Math.Max(
                bars[i].High - bars[i].Low,
                Math.Max(Math.Abs(bars[i].High - bars[i - 1].Close),
                         Math.Abs(bars[i].Low - bars[i - 1].Close)));
            sum += tr;
        }
        return sum / period;
    }
}
