namespace NNInference;

/// <summary>
/// StandardScaler: Z-нормализация (mean=0, std=1).
/// Синхронизирован с Python sklearn StandardScaler.
/// Параметры берутся из metadata JSON (scaler_mean, scaler_scale).
/// </summary>
class StandardScaler
{
    private readonly double[] _mean;
    private readonly double[] _scale;

    public StandardScaler(double[] mean, double[] scale)
    {
        _mean = mean;
        _scale = scale;
    }

    public static StandardScaler FromMetadata(ModelMetadata meta)
    {
        if (meta.ScalerMean != null && meta.ScalerScale != null &&
            meta.ScalerMean.Length > 0 && meta.ScalerScale.Length > 0)
        {
            Console.WriteLine($"[Scaler] Загружен из metadata: {meta.ScalerMean.Length} признаков");
            return new StandardScaler(meta.ScalerMean, meta.ScalerScale);
        }

        Console.WriteLine("[Scaler] Параметры не найдены, используем default (mean=0, scale=1)");
        return new StandardScaler(Array.Empty<double>(), Array.Empty<double>());
    }

    public double[] Transform(double[] features)
    {
        var result = new double[features.Length];
        for (int i = 0; i < features.Length; i++)
        {
            var mean = i < _mean.Length ? _mean[i] : 0;
            var scale = i < _scale.Length ? _scale[i] : 1;
            result[i] = scale > 0 ? (features[i] - mean) / scale : 0;
        }
        return result;
    }

    public List<double[]> TransformAll(List<double[]> windows)
    {
        return windows.Select(Transform).ToList();
    }
}
