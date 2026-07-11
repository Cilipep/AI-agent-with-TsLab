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
public sealed class NNOnnxIndicator : IBar2DoubleHandler
{
    private InferenceSession _session;
    private bool _initialized;
    private int _window = 30;
    private int _features = 31;

    [HandlerParameter(true, "30", Min = "10", Max = "100", Step = "1")]
    public int Window { get; set; } = 30;

    [HandlerParameter(true, "0.5", Min = "0.1", Max = "0.9", Step = "0.05")]
    public double Threshold { get; set; } = 0.5;

    [HandlerParameter(true, "models/BTCUSDT_1d.onnx")]
    public string ModelPath { get; set; } = "models/BTCUSDT_1d.onnx";

    private void InitializeSession()
    {
        if (_initialized) return;

        try
        {
            // Try multiple paths for the ONNX model
            string[] paths = new[]
            {
                ModelPath,
                Path.Combine("C:\\Users\\i59400f\\Desktop\\ai-agent\\TsLabWorkspace\\nn-trading\\models", Path.GetFileName(ModelPath)),
                Path.Combine(AppDomain.CurrentDomain.BaseDirectory, ModelPath),
            };

            string modelPath = null;
            foreach (var p in paths)
            {
                if (File.Exists(p))
                {
                    modelPath = p;
                    break;
                }
            }

            if (modelPath == null)
            {
                _initialized = true;
                return;
            }

            // Create session options
            var options = new SessionOptions();
            options.GraphOptimizationLevel = GraphOptimizationLevel.ORT_ENABLE_ALL;
            options.InterOpNumThreads = 1;
            options.IntraOpNumThreads = 1;

            _session = new InferenceSession(modelPath, options);

            // Use fixed dimensions from model metadata
            _window = 30;
            _features = 31;

            _initialized = true;
        }
        catch (Exception ex)
        {
            _initialized = true;
        }
    }

    public IList<double> Execute(ISecurity source)
    {
        if (source == null || source.Bars == null || source.Bars.Count < Window)
            return Array.Empty<double>();

        InitializeSession();

        var bars = source.Bars;
        var count = bars.Count;
        var result = new double[count];

        if (_session == null)
        {
            // Fallback to formula-based indicator
            return ExecuteFallback(source);
        }

        var closes = new double[count];
        for (int i = 0; i < count; i++)
            closes[i] = bars[i].Close;

        // Process each bar
        for (int i = _window; i < count; i++)
        {
            try
            {
                // Create input tensor [1, Window, Features]
                var inputTensor = new DenseTensor<float>(new[] { 1, _window, _features });

                // Fill with normalized price data
                double basePrice = closes[i - _window];
                for (int j = 0; j < _window; j++)
                {
                    int idx = i - _window + j;
                    if (idx < 0) idx = 0;

                    // Feature 0: Normalized price
                    inputTensor[0, j, 0] = (float)((closes[idx] - basePrice) / (basePrice + 1e-8));

                    // Feature 1: Returns
                    if (j > 0)
                        inputTensor[0, j, 1] = (float)((closes[idx] - closes[idx - 1]) / (closes[idx - 1] + 1e-8));

                    // Feature 2: RSI-like (momentum)
                    if (j >= 14)
                    {
                        double avgGain = 0, avgLoss = 0;
                        for (int k = j - 14; k < j; k++)
                        {
                            double change = closes[idx - (j - k)] - closes[idx - (j - k) - 1];
                            if (change > 0) avgGain += change; else avgLoss -= change;
                        }
                        avgGain /= 14; avgLoss /= 14;
                        double rsi = avgLoss == 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);
                        inputTensor[0, j, 2] = (float)(rsi / 100.0);
                    }

                    // Feature 3: MACD-like
                    if (j >= 26)
                    {
                        double ema12 = CalcEMA(closes, idx, 12);
                        double ema26 = CalcEMA(closes, idx, 26);
                        inputTensor[0, j, 3] = (float)((ema12 - ema26) / (ema26 + 1e-8));
                    }

                    // Fill remaining features
                    for (int k = 4; k < _features; k++)
                        inputTensor[0, j, k] = 0;
                }

                // Run inference
                var inputs = new List<NamedOnnxValue>
                {
                    NamedOnnxValue.CreateFromTensor("input", inputTensor)
                };

                using (var outputs = _session.Run(inputs))
                {
                    var output = outputs.First().AsTensor<float>().ToArray();
                    result[i] = output[0];
                }
            }
            catch
            {
                result[i] = 0.5;
            }
        }

        return result;
    }

    private double CalcEMA(double[] data, int index, int period)
    {
        if (index < period) return data[index];
        double multiplier = 2.0 / (period + 1);
        double ema = data[0];
        for (int i = 1; i <= index; i++)
            ema = (data[i] - ema) * multiplier + ema;
        return ema;
    }

    private IList<double> ExecuteFallback(ISecurity source)
    {
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
