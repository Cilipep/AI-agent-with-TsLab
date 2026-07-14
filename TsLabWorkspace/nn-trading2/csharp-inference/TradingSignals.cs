namespace NNInference;

/// <summary>
/// Тип торгового сигнала.
/// </summary>
enum SignalType
{
    None,       // Нет сигнала
    Long,       // Покупка
    Short,      // Продажа
    CloseLong,  // Закрытие длинной позиции
    CloseShort  // Закрытие короткой позиции
}

/// <summary>
/// Сила сигнала (1-5).
/// </summary>
enum SignalStrength
{
    Weak = 1,       // Слабый (только для агрессивных стратегий)
    Moderate = 2,   // Умеренный
    Normal = 3,     // Обычный
    Strong = 4,     // Сильный
    VeryStrong = 5  // Очень сильный
}

/// <summary>
/// Торговый сигнал с метаданными.
/// </summary>
class TradeSignal
{
    public SignalType Type { get; set; }
    public SignalStrength Strength { get; set; }
    public float Prediction { get; set; }
    public float Confidence { get; set; }
    public float EntryPrice { get; set; }
    public float StopLoss { get; set; }
    public float TakeProfit { get; set; }
    public float PositionSizePct { get; set; }
    public string Reason { get; set; } = "";
    public DateTime Timestamp { get; set; }

    public override string ToString()
    {
        if (Type == SignalType.None)
            return $"[NO SIGNAL] {Reason}";

        var emoji = Type switch
        {
            SignalType.Long => "🟢",
            SignalType.Short => "🔴",
            SignalType.CloseLong => "🟡",
            SignalType.CloseShort => "🟡",
            _ => "⚪"
        };

        return $"{emoji} {Type} | Strength={Strength} | Conf={Confidence:P1} | " +
               $"Entry={EntryPrice:F2} | SL={StopLoss:F2} | TP={TakeProfit:F2} | " +
               $"Size={PositionSizePct:P0} | {Reason}";
    }
}

/// <summary>
/// Генератор торговых сигналов на основе предсказаний модели.
/// </summary>
class SignalGenerator
{
    private readonly SignalConfig _config;

    public SignalGenerator(SignalConfig config)
    {
        _config = config;
    }

    /// <summary>
    /// Генерация сигнала на основе предсказания и рыночных данных.
    /// </summary>
    public TradeSignal Generate(
        float prediction,
        List<Candle> candles,
        SignalType? currentPosition = null)
    {
        var signal = new TradeSignal
        {
            Prediction = prediction,
            Timestamp = candles[^1].OpenTime,
            EntryPrice = (float)candles[^1].Close
        };

        // Расчёт уверенности
        signal.Confidence = CalculateConfidence(prediction);

        // Проверка порога
        if (signal.Confidence < _config.MinConfidence)
        {
            signal.Type = SignalType.None;
            signal.Reason = $"Confidence {signal.Confidence:P1} < порога {_config.MinConfidence:P1}";
            return signal;
        }

        // Определение направления
        var direction = prediction > 0.5 ? SignalType.Long : SignalType.Short;

        // Проверка: если уже в позиции, не открывать повторно
        if (currentPosition == direction)
        {
            signal.Type = SignalType.None;
            signal.Reason = $"Уже в позиции {direction}";
            return signal;
        }

        // Если в противоположной позиции — закрыть
        if (currentPosition != null && currentPosition != SignalType.None)
        {
            signal.Type = direction == SignalType.Long ? SignalType.CloseShort : SignalType.CloseLong;
            signal.Strength = SignalStrength.Normal;
            signal.Reason = $"Разворот: {currentPosition} → {direction}";
            return signal;
        }

        // Новый вход
        signal.Type = direction;
        signal.Strength = CalculateStrength(signal.Confidence, candles);
        signal.Reason = $"Pred={prediction:F4}, Conf={signal.Confidence:P1}";

        // Расчёт Stop Loss и Take Profit
        CalculateSLTP(signal, candles);

        // Расчёт размера позиции
        signal.PositionSizePct = CalculatePositionSize(signal.Strength, signal.Confidence);

        return signal;
    }

    /// <summary>
    /// Расчёт уверенности: |pred - 0.5| * 2 → 0..1.
    /// </summary>
    private float CalculateConfidence(float prediction)
    {
        return Math.Abs(prediction - 0.5f) * 2;
    }

    /// <summary>
    /// Расчёт силы сигнала на основе уверенности и волатильности.
    /// </summary>
    private SignalStrength CalculateStrength(float confidence, List<Candle> candles)
    {
        // Базовая сила по уверенности
        int baseStrength = confidence switch
        {
            >= 0.8f => 5,
            >= 0.6f => 4,
            >= 0.4f => 3,
            >= 0.2f => 2,
            _ => 1
        };

        // Волатильность: если высокая — снижаем силу
        var volatility = CalculateVolatility(candles, 20);
        if (volatility > _config.HighVolatilityThreshold)
            baseStrength = Math.Max(1, baseStrength - 1);

        // Тренд: если сильный тренд — повышаем силу
        var trend = CalculateTrendStrength(candles, 20);
        if (trend > 0.7)
            baseStrength = Math.Min(5, baseStrength + 1);

        return (SignalStrength)Math.Clamp(baseStrength, 1, 5);
    }

    /// <summary>
    /// Расчёт Stop Loss и Take Profit.
    /// </summary>
    private void CalculateSLTP(TradeSignal signal, List<Candle> candles)
    {
        var atr = CalculateATR(candles, 14);
        var price = signal.EntryPrice;

        if (signal.Type == SignalType.Long)
        {
            // Long: SL ниже, TP выше
            signal.StopLoss = price - (atr * _config.SL_ATR_Multiplier);
            signal.TakeProfit = price + (atr * _config.TP_ATR_Multiplier);
        }
        else if (signal.Type == SignalType.Short)
        {
            // Short: SL выше, TP ниже
            signal.StopLoss = price + (atr * _config.SL_ATR_Multiplier);
            signal.TakeProfit = price - (atr * _config.TP_ATR_Multiplier);
        }

        // Ограничение по проценту
        var maxSLPct = _config.MaxStopLossPct;
        var slPct = Math.Abs(signal.StopLoss - price) / price;
        if (slPct > maxSLPct)
        {
            if (signal.Type == SignalType.Long)
                signal.StopLoss = price * (1 - maxSLPct);
            else
                signal.StopLoss = price * (1 + maxSLPct);
        }
    }

    /// <summary>
    /// Расчёт размера позиции (процит от депозита).
    /// Kelly criterion упрощённый.
    /// </summary>
    private float CalculatePositionSize(SignalStrength strength, float confidence)
    {
        // Базовый размер по силе
        float baseSize = strength switch
        {
            SignalStrength.VeryStrong => 0.20f,
            SignalStrength.Strong => 0.15f,
            SignalStrength.Normal => 0.10f,
            SignalStrength.Moderate => 0.05f,
            SignalStrength.Weak => 0.02f,
            _ => 0.05f
        };

        // Корректировка по уверенности
        baseSize *= confidence;

        // Ограничение
        return Math.Clamp(baseSize, _config.MinPositionPct, _config.MaxPositionPct);
    }

    /// <summary>
    /// ATR (Average True Range).
    /// </summary>
    private float CalculateATR(List<Candle> candles, int period)
    {
        if (candles.Count < period + 1)
            return (float)(candles[^1].High - candles[^1].Low);

        var tr = new List<double>();
        for (int i = candles.Count - period; i < candles.Count; i++)
        {
            var hl = candles[i].High - candles[i].Low;
            var hc = Math.Abs(candles[i].High - candles[i - 1].Close);
            var lc = Math.Abs(candles[i].Low - candles[i - 1].Close);
            tr.Add(Math.Max(hl, Math.Max(hc, lc)));
        }

        return (float)tr.Average();
    }

    /// <summary>
    /// Волатильность (отношение диапазона к цене).
    /// </summary>
    private float CalculateVolatility(List<Candle> candles, int period)
    {
        if (candles.Count < period)
            return 0;

        var ranges = candles.Skip(candles.Count - period)
            .Select(c => (c.High - c.Low) / c.Close)
            .ToList();

        return (float)ranges.Average();
    }

    /// <summary>
    /// Сила тренда (0-1): насколько цена следует направлению.
    /// </summary>
    private float CalculateTrendStrength(List<Candle> candles, int period)
    {
        if (candles.Count < period)
            return 0;

        var closes = candles.Skip(candles.Count - period).Select(c => c.Close).ToList();
        var up = 0;
        for (int i = 1; i < closes.Count; i++)
        {
            if (closes[i] > closes[i - 1]) up++;
        }

        return Math.Abs(up - period / 2.0f) / (period / 2.0f);
    }
}

/// <summary>
/// Конфигурация генератора сигналов.
/// </summary>
class SignalConfig
{
    public float MinConfidence { get; set; } = 0.02f;  // 2% для тестирования
    public float SL_ATR_Multiplier { get; set; } = 1.5f;
    public float TP_ATR_Multiplier { get; set; } = 2.5f;
    public float MaxStopLossPct { get; set; } = 0.03f;
    public float HighVolatilityThreshold { get; set; } = 0.02f;
    public float MinPositionPct { get; set; } = 0.02f;
    public float MaxPositionPct { get; set; } = 0.20f;
}
