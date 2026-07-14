namespace NNInference;

/// <summary>
/// Утилиты для работы с тензорами.
/// </summary>
static class TensorOps
{
    /// <summary>
    /// Выравнивание 2D массива (window × features) в плоский float[] для инференса.
    /// </summary>
    public static float[] Flatten(double[] window)
    {
        var result = new float[window.Length];
        for (int i = 0; i < window.Length; i++)
            result[i] = (float)window[i];
        return result;
    }

    /// <summary>
    /// Выравнивание списка окон в плоский float[].
    /// </summary>
    public static float[] Flatten(List<double[]> windows)
    {
        int totalLen = windows.Sum(w => w.Length);
        var result = new float[totalLen];
        int offset = 0;
        foreach (var window in windows)
        {
            for (int i = 0; i < window.Length; i++)
                result[offset + i] = (float)window[i];
            offset += window.Length;
        }
        return result;
    }
}
