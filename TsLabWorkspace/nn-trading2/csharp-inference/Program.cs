using Newtonsoft.Json;
using System.Text;

namespace NNInference;

/// <summary>
/// Точка входа: загрузка модели, получение данных Binance, инференс, торговый сигнал.
/// Приоритет: TorchSharp (.npy веса) → ONNX Runtime (fallback).
/// Режимы: --single, --scan, --trade.
/// </summary>
class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("=== NN Trading Inference (TorchSharp + Binance.Net) ===\n");

        var config = LoadConfig();
        var metadata = LoadMetadata(config);
        PrintMetadata(metadata);

        // Загрузка модели
        var engine = LoadEngine(config, metadata);
        if (engine == null) return;

        // Режим
        var mode = args.Contains("--trade") ? "trade" :
                   args.Contains("--scan") ? "scan" : "single";
        var symbols = args.Contains("--symbols")
            ? args[Array.IndexOf(args, "--symbols") + 1].Split(',')
            : new[] { config.Symbol };
        var isLive = args.Contains("--live");

        switch (mode)
        {
            case "trade":
                await RunTrader(engine, metadata, config, symbols, isLive);
                break;
            case "scan":
                await RunScanner(engine, metadata, config, symbols);
                break;
            default:
                await RunSingle(engine, metadata, config);
                break;
        }

        Console.WriteLine("\n=== Inference Complete ===");
    }

    static async Task RunTrader(INNInferenceEngine engine, ModelMetadata metadata, InferenceConfig config, string[] symbols, bool isLive = false)
    {
        // Загрузка .env
        var envPath = Path.Combine(config.ModelDir, "..", ".env");
        var tradeConfig = LoadTradeConfig(envPath);
        tradeConfig.UseDemo = !isLive;

        Console.WriteLine($"[Trade] Режим: {(tradeConfig.UseDemo ? "DEMO" : "⚠️ LIVE ⚠️")}");
        Console.WriteLine($"[Trade] Символы: {string.Join(", ", symbols)}\n");

        // Подключение
        using var trader = new BinanceTrader(tradeConfig);
        if (!await trader.ConnectAsync())
        {
            Console.WriteLine("[Trade] Не удалось подключиться к Binance");
            return;
        }

        // Сигналы для каждого символа
        var signalConfig = new SignalConfig
        {
            MinConfidence = 0.02f,  // 2% порог для тестирования
            SL_ATR_Multiplier = 1.5f,
            TP_ATR_Multiplier = 2.5f,
            MaxStopLossPct = 0.03f,
        };
        var signalGen = new SignalGenerator(signalConfig);

        foreach (var symbol in symbols)
        {
            Console.WriteLine($"\n[Trade] === {symbol} ===");

            try
            {
                // Получение данных
                var candles = await BinanceDataFetcher.GetKlinesAsync(
                    symbol.Replace("/", ""), config.Interval, metadata.SequenceLength + 100);

                // Инференс
                var featureMatrix = FeatureComputer.Compute(candles, metadata.Features, metadata.SequenceLength);
                var scaler = StandardScaler.FromMetadata(metadata);
                var scaledMatrix = scaler.TransformAll(featureMatrix);

                if (scaledMatrix.Count < metadata.SequenceLength)
                {
                    Console.WriteLine($"  Недостаточно данных");
                    continue;
                }

                var sequenceWindows = scaledMatrix.Skip(scaledMatrix.Count - metadata.SequenceLength).ToList();
                var inputTensor = TensorOps.Flatten(sequenceWindows);
                var prediction = engine.Predict(inputTensor);

                // Генерация сигнала
                var signal = signalGen.Generate(prediction, candles);

                // Вывод
                Console.WriteLine($"  Prediction: {prediction:F4} | {signal}");

                // Исполнение
                if (signal.Type != SignalType.None)
                {
                    Console.Write("  Исполнить? (y/n): ");
                    var key = Console.ReadLine()?.Trim().ToLower();

                    if (key == "y" || key == "да")
                    {
                        var record = await trader.ExecuteSignalAsync(signal, symbol.Replace("/", ""));
                        if (record != null)
                        {
                            Console.WriteLine($"  ✓ Ордер исполнен: {record.OrderId}");
                        }
                    }
                    else
                    {
                        Console.WriteLine("  Пропущено");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  Ошибка: {ex.Message}");
            }
        }

        // История сделок
        var history = trader.GetTradeHistory();
        if (history.Any())
        {
            Console.WriteLine("\n=== История сделок ===");
            foreach (var t in history)
            {
                Console.WriteLine($"  {t.Timestamp:HH:mm:ss} {t.Side} {t.Symbol} {t.Quantity} @ {t.Price} = {t.Total:F2} USDT");
            }
        }
    }

    static async Task RunSingle(INNInferenceEngine engine, ModelMetadata metadata, InferenceConfig config)
    {
        Console.WriteLine($"[Binance] Получение истории {config.Symbol} ({config.Interval})...");

        var candles = await BinanceDataFetcher.GetKlinesAsync(config.Symbol, config.Interval, metadata.SequenceLength + 100);
        Console.WriteLine($"[Binance] Получено {candles.Count} свечей\n");

        var featureMatrix = FeatureComputer.Compute(candles, metadata.Features, metadata.SequenceLength);
        Console.WriteLine($"[Features] {metadata.Features.Length} признаков, {featureMatrix.Count} окон\n");

        var scaler = StandardScaler.FromMetadata(metadata);
        var scaledMatrix = scaler.TransformAll(featureMatrix);

        int seqLen = metadata.SequenceLength;
        if (scaledMatrix.Count < seqLen)
        {
            Console.WriteLine($"Недостаточно данных: {scaledMatrix.Count} окон, нужно {seqLen}");
            return;
        }

        var sequenceWindows = scaledMatrix.Skip(scaledMatrix.Count - seqLen).ToList();
        var inputTensor = TensorOps.Flatten(sequenceWindows);
        Console.WriteLine($"[Input] {seqLen} окон × {metadata.InputSize} признаков = {inputTensor.Length} элементов\n");

        var prediction = engine.Predict(inputTensor);

        var signalConfig = new SignalConfig
        {
            MinConfidence = (float)config.MinConfidence,
            SL_ATR_Multiplier = 1.5f,
            TP_ATR_Multiplier = 2.5f,
            MaxStopLossPct = 0.03f,
        };
        var signalGen = new SignalGenerator(signalConfig);
        var tradeSignal = signalGen.Generate(prediction, candles);

        Console.WriteLine("=== Результат ===");
        Console.WriteLine($"  Модель:     {engine.GetType().Name}");
        Console.WriteLine($"  Символ:     {config.Symbol}");
        Console.WriteLine($"  Таймфрейм:  {config.Interval}");
        Console.WriteLine($"  Prediction: {prediction:F6}");
        Console.WriteLine($"  Цена:       {candles[^1].Close:F2}");
        Console.WriteLine();

        if (tradeSignal.Type == SignalType.None)
        {
            Console.WriteLine($"  {tradeSignal}");
        }
        else
        {
            Console.WriteLine($"  ═══════════════════════════════════════");
            Console.WriteLine($"  {tradeSignal}");
            Console.WriteLine($"  ═══════════════════════════════════════");
            Console.WriteLine();
            Console.WriteLine($"  Вход:       {tradeSignal.EntryPrice:F2}");
            Console.WriteLine($"  Stop Loss:  {tradeSignal.StopLoss:F2} ({Math.Abs(tradeSignal.StopLoss - tradeSignal.EntryPrice) / tradeSignal.EntryPrice:P1})");
            Console.WriteLine($"  Take Profit:{tradeSignal.TakeProfit:F2} ({Math.Abs(tradeSignal.TakeProfit - tradeSignal.EntryPrice) / tradeSignal.EntryPrice:P1})");
            Console.WriteLine($"  Размер:     {tradeSignal.PositionSizePct:P0} депозита");
            Console.WriteLine($"  R:R =       {Math.Abs(tradeSignal.TakeProfit - tradeSignal.EntryPrice) / Math.Abs(tradeSignal.StopLoss - tradeSignal.EntryPrice):F2}");
        }
    }

    static async Task RunScanner(INNInferenceEngine engine, ModelMetadata metadata, InferenceConfig config, string[] symbols)
    {
        var signalConfig = new SignalConfig
        {
            MinConfidence = (float)config.MinConfidence,
            SL_ATR_Multiplier = 1.5f,
            TP_ATR_Multiplier = 2.5f,
            MaxStopLossPct = 0.03f,
        };

        var scanner = new MultiSymbolScanner(engine, metadata, signalConfig);
        var results = await scanner.ScanAsync(symbols, config.Interval);

        ScannerReport.Print(results);

        // Топ сигналы
        var topSignals = MultiSymbolScanner.RankByStrength(results);
        if (topSignals.Any())
        {
            Console.WriteLine("\n🏆 ТОП СИГНАЛЫ ДЛЯ ТОРГОВЛИ:");
            foreach (var r in topSignals.Take(3))
            {
                Console.WriteLine($"  {r.Signal}");
            }
        }
    }

    static INNInferenceEngine? LoadEngine(InferenceConfig config, ModelMetadata metadata)
    {
        var torchsharpDir = Path.Combine(config.ModelDir, "torchsharp");
        var onnxPath = Path.Combine(config.ModelDir, "lstm_model.onnx");

        if (Directory.Exists(torchsharpDir) && File.Exists(Path.Combine(torchsharpDir, "metadata.json")))
        {
            Console.WriteLine($"[TorchSharp] Загрузка из {torchsharpDir}/...");
            try
            {
                return new TorchSharpEngine(config.ModelDir, metadata);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[TorchSharp] Ошибка: {ex.Message}");
                Console.WriteLine("[TorchSharp] Fallback → ONNX");
            }
        }

        if (File.Exists(onnxPath))
        {
            Console.WriteLine($"[ONNX] Загрузка {onnxPath}...");
            return new OnnxEngine(onnxPath, metadata);
        }

        Console.WriteLine("Модель не найдена. Проверьте models/ папку.");
        return null;
    }

    static InferenceConfig LoadConfig()
    {
        var configPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "models", "lstm_model_metadata.json");
        if (File.Exists(configPath))
        {
            var json = File.ReadAllText(configPath);
            var meta = JsonConvert.DeserializeObject<ModelMetadata>(json);
            if (meta != null)
            {
                return new InferenceConfig
                {
                    Symbol = meta.Symbol ?? "BTCUSDT",
                    Interval = meta.Interval ?? "1h",
                    ModelDir = Path.GetDirectoryName(configPath)!,
                    MinConfidence = meta.MinConfidence
                };
            }
        }
        return new InferenceConfig();
    }

    static ModelMetadata LoadMetadata(InferenceConfig config)
    {
        var path = Path.Combine(config.ModelDir, "lstm_model_metadata.json");
        if (!File.Exists(path))
            return ModelMetadata.Default();

        var json = File.ReadAllText(path);
        return JsonConvert.DeserializeObject<ModelMetadata>(json) ?? ModelMetadata.Default();
    }

    static void PrintMetadata(ModelMetadata m)
    {
        Console.WriteLine($"  Модель:      LSTM ({m.HiddenSize}h x {m.NumLayers}l)");
        Console.WriteLine($"  Вход:        {m.InputSize} признаков, окно {m.SequenceLength}");
        Console.WriteLine($"  Признаки:    {string.Join(", ", m.Features.Take(5))}... ({m.Features.Length} всего)");
        Console.WriteLine();
    }

    static TradeConfig LoadTradeConfig(string envPath)
    {
        var config = new TradeConfig();

        if (!File.Exists(envPath))
        {
            Console.WriteLine($"[Trade] .env не найден: {envPath}");
            return config;
        }

        var lines = File.ReadAllLines(envPath);
        foreach (var line in lines)
        {
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith('#'))
                continue;

            var parts = line.Split('=', 2);
            if (parts.Length != 2) continue;

            var key = parts[0].Trim();
            var value = parts[1].Trim();

            switch (key)
            {
                case "BINANCE_API_KEY": config.ApiKey = value; break;
                case "BINANCE_API_SECRET": config.ApiSecret = value; break;
                case "USE_DEMO": config.UseDemo = value.ToLower() == "true"; break;
                case "MAX_POSITION_PCT": config.MaxPositionPct = decimal.Parse(value, System.Globalization.CultureInfo.InvariantCulture); break;
                case "MAX_DAILY_TRADES": config.MaxDailyTrades = int.Parse(value, System.Globalization.CultureInfo.InvariantCulture); break;
            }
        }

        Console.WriteLine($"[Trade] API Key: {config.ApiKey[..8]}...");
        Console.WriteLine($"[Trade] Demo: {config.UseDemo}");
        return config;
    }
}

/// <summary>
/// Конфигурация инференса.
/// </summary>
class InferenceConfig
{
    public string Symbol { get; set; } = "BTCUSDT";
    public string Interval { get; set; } = "1h";
    public string ModelDir { get; set; } = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "models");
    public double MinConfidence { get; set; } = 0.6;
}

/// <summary>
/// Метаданные модели (из Python-экспорта).
/// </summary>
class ModelMetadata
{
    [JsonProperty("input_size")] public int InputSize { get; set; } = 20;
    [JsonProperty("hidden_size")] public int HiddenSize { get; set; } = 32;
    [JsonProperty("num_layers")] public int NumLayers { get; set; } = 2;
    [JsonProperty("sequence_length")] public int SequenceLength { get; set; } = 20;
    [JsonProperty("features")] public string[] Features { get; set; } = Array.Empty<string>();
    [JsonProperty("symbol")] public string? Symbol { get; set; }
    [JsonProperty("interval")] public string? Interval { get; set; }
    [JsonProperty("min_confidence")] public double MinConfidence { get; set; } = 0.6;
    [JsonProperty("scaler_mean")] public double[]? ScalerMean { get; set; }
    [JsonProperty("scaler_scale")] public double[]? ScalerScale { get; set; }

    public static ModelMetadata Default() => new()
    {
        Features = new[] { "returns", "rsi_14", "macd", "bb_width", "atr_14", "adx", "volume_ratio", "volatility_20", "momentum_5", "ema_20" }
    };
}

/// <summary>
/// Интерфейс движка инференса.
/// </summary>
interface INNInferenceEngine
{
    float Predict(float[] flatInput);
}
