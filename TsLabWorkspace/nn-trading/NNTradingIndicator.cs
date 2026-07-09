using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;
using TSLab.Script;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(1)]
[Input(0, TemplateTypes.SECURITY)]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class NNTradingIndicator : IBar2DoubleHandler, IDisposable
{
    private InferenceSession? _session;
    private bool _disposed;

    [HandlerParameter(true, "30", Min = "10", Max = "100", Step = "1")]
    public int Window { get; set; } = 30;

    [HandlerParameter(true, "0.5", Min = "0.1", Max = "0.9", Step = "0.05")]
    public double Threshold { get; set; } = 0.5;

    private InferenceSession GetSession()
    {
        if (_session != null)
            return _session;

        var modelPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "nn_trading.onnx");
        if (!File.Exists(modelPath))
            throw new FileNotFoundException($"ONNX model not found: {modelPath}");

        _session = new InferenceSession(modelPath);
        return _session;
    }

    public IList<double> Execute(ISecurity source)
    {
        if (source == null || source.Bars == null || source.Bars.Count < Window)
            return Array.Empty<double>();

        var session = GetSession();
        var bars = source.Bars;
        var count = bars.Count;
        var result = new double[count];

        // Precompute indicators for all bars
        var closes = new double[count];
        var highs = new double[count];
        var lows = new double[count];
        var volumes = new double[count];

        for (int i = 0; i < count; i++)
        {
            closes[i] = bars[i].Close;
            highs[i] = bars[i].High;
            lows[i] = bars[i].Low;
            volumes[i] = bars[i].Volume;
        }

        // Compute RSI
        var rsi = ComputeRSI(closes, 14);

        // Compute EMAs
        var ema12 = ComputeEMA(closes, 12);
        var ema26 = ComputeEMA(closes, 26);

        // Compute MACD
        var macd = new double[count];
        var macdSignal = new double[count];
        var macdHist = new double[count];
        for (int i = 0; i < count; i++)
        {
            macd[i] = ema12[i] - ema26[i];
        }
        macdSignal = ComputeEMA(macd, 9);
        for (int i = 0; i < count; i++)
        {
            macdHist[i] = macd[i] - macdSignal[i];
        }

        // Compute Bollinger Bands
        var bbUpper = new double[count];
        var bbLower = new double[count];
        var bbWidth = new double[count];
        for (int i = 19; i < count; i++)
        {
            double sum = 0;
            for (int j = i - 19; j <= i; j++)
                sum += closes[j];
            double sma = sum / 20;
            double variance = 0;
            for (int j = i - 19; j <= i; j++)
                variance += (closes[j] - sma) * (closes[j] - sma);
            double std = Math.Sqrt(variance / 20);
            bbUpper[i] = sma + 2 * std;
            bbLower[i] = sma - 2 * std;
            bbWidth[i] = (bbUpper[i] - bbLower[i]) / sma;
        }

        // Compute ATR
        var atr = new double[count];
        for (int i = 1; i < count; i++)
        {
            double tr = Math.Max(
                highs[i] - lows[i],
                Math.Max(
                    Math.Abs(highs[i] - closes[i - 1]),
                    Math.Abs(lows[i] - closes[i - 1])
                )
            );
            atr[i] = (atr[i - 1] * 13 + tr) / 14;
        }

        // Run inference for each bar
        for (int i = Window; i < count; i++)
        {
            var features = new float[Window, 104];

            for (int t = 0; t < Window; t++)
            {
                int idx = i - Window + t;
                features[t, 0] = (float)(closes[idx] / closes[idx - 1] - 1); // returns
                features[t, 1] = (float)rsi[idx];
                features[t, 2] = (float)(highs[idx] / lows[idx] - 1); // high/low ratio
                features[t, 3] = (float)(closes[idx] / closes[Math.Max(0, idx - 1)] - 1); // close/open
                features[t, 4] = (float)macd[idx];
                features[t, 5] = (float)macdSignal[idx];
                features[t, 6] = (float)macdHist[idx];
                features[t, 7] = (float)ema12[idx];
                features[t, 8] = (float)ema26[idx];
                features[t, 9] = (float)(bbUpper[idx] - closes[idx]);
                features[t, 10] = (float)(closes[idx] - bbLower[idx]);
                features[t, 11] = (float)bbWidth[idx];
                features[t, 12] = (float)atr[idx];
                features[t, 13] = (float)(atr[idx] / closes[idx]);

                // Fill remaining features with zeros (model was trained with 104 features)
                for (int f = 14; f < 104; f++)
                    features[t, f] = 0;
            }

            // Create input tensor
            var flattened = new float[1 * Window * 104];
            Buffer.BlockCopy(features, 0, flattened, 0, flattened.Length * sizeof(float));
            var inputTensor = new DenseTensor<float>(flattened, new[] { 1, Window, 104 });
            var inputs = new List<NamedOnnxValue>
            {
                NamedOnnxValue.CreateFromTensor("input", inputTensor)
            };

            // Run inference
            using var results = session.Run(inputs);
            var output = results.First().AsTensor<float>().ToArray();
            result[i] = output[0];
        }

        return result;
    }

    private double[] ComputeRSI(double[] closes, int period)
    {
        var rsi = new double[closes.Length];
        if (closes.Length < period + 1)
            return rsi;

        double avgGain = 0, avgLoss = 0;

        for (int i = 1; i <= period; i++)
        {
            double change = closes[i] - closes[i - 1];
            if (change > 0) avgGain += change;
            else avgLoss -= change;
        }
        avgGain /= period;
        avgLoss /= period;

        rsi[period] = avgLoss == 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);

        for (int i = period + 1; i < closes.Length; i++)
        {
            double change = closes[i] - closes[i - 1];
            double gain = change > 0 ? change : 0;
            double loss = change < 0 ? -change : 0;

            avgGain = (avgGain * (period - 1) + gain) / period;
            avgLoss = (avgLoss * (period - 1) + loss) / period;

            rsi[i] = avgLoss == 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);
        }

        return rsi;
    }

    private double[] ComputeEMA(double[] data, int period)
    {
        var ema = new double[data.Length];
        if (data.Length == 0)
            return ema;

        double multiplier = 2.0 / (period + 1);
        ema[0] = data[0];

        for (int i = 1; i < data.Length; i++)
        {
            ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1];
        }

        return ema;
    }

    public void Dispose()
    {
        if (!_disposed)
        {
            _session?.Dispose();
            _disposed = true;
        }
    }
}
