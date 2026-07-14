namespace NNInference;

/// <summary>
/// Сканер нескольких символов: находит лучшие торговые возможности.
/// </summary>
class MultiSymbolScanner
{
    private readonly INNInferenceEngine _engine;
    private readonly ModelMetadata _metadata;
    private readonly SignalGenerator _signalGen;

    public MultiSymbolScanner(INNInferenceEngine engine, ModelMetadata metadata, SignalConfig signalConfig)
    {
        _engine = engine;
        _metadata = metadata;
        _signalGen = new SignalGenerator(signalConfig);
    }

    /// <summary>
    /// Сканирование списка символов.
    /// </summary>
    public async Task<List<ScanResult>> ScanAsync(string[] symbols, string interval = "1h")
    {
        var results = new List<ScanResult>();

        Console.WriteLine($"[Scanner] Сканирование {symbols.Length} символов...\n");

        foreach (var symbol in symbols)
        {
            try
            {
                var result = await ScanSymbolAsync(symbol, interval);
                results.Add(result);

                // Вывод промежуточного результата
                if (result.Signal.Type != SignalType.None)
                    Console.WriteLine($"  ✓ {symbol}: {result.Signal}");
                else
                    Console.WriteLine($"  · {symbol}: {result.Signal.Reason}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  ✗ {symbol}: {ex.Message}");
                results.Add(new ScanResult
                {
                    Symbol = symbol,
                    Error = ex.Message
                });
            }

            // Задержка между запросами (Rate limit)
            await Task.Delay(200);
        }

        return results;
    }

    /// <summary>
    /// Сканирование одного символа.
    /// </summary>
    private async Task<ScanResult> ScanSymbolAsync(string symbol, string interval)
    {
        // Получение свечей
        var candles = await BinanceDataFetcher.GetKlinesAsync(symbol, interval, _metadata.SequenceLength + 100);

        // Вычисление признаков
        var featureMatrix = FeatureComputer.Compute(candles, _metadata.Features, _metadata.SequenceLength);

        if (featureMatrix.Count < _metadata.SequenceLength)
        {
            return new ScanResult
            {
                Symbol = symbol,
                Error = $"Недостаточно данных: {featureMatrix.Count} окон"
            };
        }

        // Стандартизация
        var scaler = StandardScaler.FromMetadata(_metadata);
        var scaledMatrix = scaler.TransformAll(featureMatrix);

        // Инференс
        var sequenceWindows = scaledMatrix.Skip(scaledMatrix.Count - _metadata.SequenceLength).ToList();
        var inputTensor = TensorOps.Flatten(sequenceWindows);
        var prediction = _engine.Predict(inputTensor);

        // Генерация сигнала
        var signal = _signalGen.Generate(prediction, candles);

        return new ScanResult
        {
            Symbol = symbol,
            Prediction = prediction,
            Price = (float)candles[^1].Close,
            Signal = signal,
            Candles = candles
        };
    }

    /// <summary>
    /// Сортировка результатов по силе сигнала.
    /// </summary>
    public static List<ScanResult> RankByStrength(List<ScanResult> results)
    {
        return results
            .Where(r => r.Signal.Type != SignalType.None && r.Error == null)
            .OrderByDescending(r => (int)r.Signal.Strength)
            .ThenByDescending(r => r.Signal.Confidence)
            .ToList();
    }
}

/// <summary>
/// Результат сканирования одного символа.
/// </summary>
class ScanResult
{
    public string Symbol { get; set; } = "";
    public float Prediction { get; set; }
    public float Price { get; set; }
    public TradeSignal Signal { get; set; } = new() { Type = SignalType.None };
    public List<Candle>? Candles { get; set; }
    public string? Error { get; set; }
}

/// <summary>
/// Консольный вывод таблицы результатов сканирования.
/// </summary>
static class ScannerReport
{
    public static void Print(List<ScanResult> results)
    {
        Console.WriteLine("\n╔══════════════════════════════════════════════════════════════════════════╗");
        Console.WriteLine("║                        MULTI-SYMBOL SCANNER                            ║");
        Console.WriteLine("╠══════════════════════════════════════════════════════════════════════════╣");

        // Сигналы
        var signals = results.Where(r => r.Signal.Type != SignalType.None && r.Error == null).ToList();
        if (signals.Any())
        {
            Console.WriteLine("║  ТОРГОВЫЕ СИГНАЛЫ:                                                     ║");
            Console.WriteLine("║  ─────────────────────────────────────────────────────────────────────  ║");
            foreach (var r in signals.OrderByDescending(r => (int)r.Signal.Strength))
            {
                var s = r.Signal;
                var line = $"║  {r.Symbol,-8} │ {s.Type,-8} │ Str={s.Strength} │ Conf={s.Confidence:P0} │ " +
                          $"Entry={s.EntryPrice:F0} │ SL={s.StopLoss:F0} │ TP={s.TakeProfit:F0} │ {s.PositionSizePct:P0}";
                Console.WriteLine(line);
            }
        }
        else
        {
            Console.WriteLine("║  Нет активных сигналов                                                  ║");
        }

        Console.WriteLine("╠══════════════════════════════════════════════════════════════════════════╣");

        // Все предсказания
        Console.WriteLine("║  ВСЕ ПРЕДСКАЗАНИЯ:                                                      ║");
        Console.WriteLine("║  ─────────────────────────────────────────────────────────────────────  ║");
        Console.WriteLine("║  Символ   │ Prediction │ Цена      │ Conf    │ Signal                   ║");
        Console.WriteLine("║  ─────────┼────────────┼───────────┼─────────┼──────────────────────────║");

        foreach (var r in results.OrderByDescending(r => Math.Abs(r.Prediction - 0.5)))
        {
            if (r.Error != null)
            {
                Console.WriteLine($"║  {r.Symbol,-8} │ ERROR      │           │         │ {r.Error,-24}║");
                continue;
            }

            var conf = Math.Abs(r.Prediction - 0.5f) * 2;
            var sig = r.Signal.Type == SignalType.None ? "—" : r.Signal.Type.ToString();
            var line = $"║  {r.Symbol,-8} │ {r.Prediction,10:F4} │ {r.Price,9:F2} │ {conf,6:P1} │ {sig,-24}║";
            Console.WriteLine(line);
        }

        Console.WriteLine("╚══════════════════════════════════════════════════════════════════════════╝");
    }
}
