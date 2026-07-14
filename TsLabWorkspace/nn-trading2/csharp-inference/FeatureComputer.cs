namespace NNInference;

/// <summary>
/// Вычисление технических индикаторов на C#.
/// Должны совпадать с Python features.py: compute_all_features().
/// </summary>
static class FeatureComputer
{
    public static List<double[]> Compute(List<Candle> candles, string[] featureNames, int windowSize)
    {
        // Построение временных рядов
        var closes = candles.Select(c => c.Close).ToList();
        var highs = candles.Select(c => c.High).ToList();
        var lows = candles.Select(c => c.Low).ToList();
        var volumes = candles.Select(c => c.Volume).ToList();

        // Нормализация close и volume (z-score по истории)
        var closeNorm = ZScore(closes);
        var volumeNorm = ZScore(volumes);

        // MACD нормализованный
        var macd = ComputeMACD(closes);
        var macdNorm = ZScore(macd.ToList());

        var macdSignal = ComputeMACDSignal(closes);
        var macdSignalNorm = ZScore(macdSignal.ToList());

        // EMA дистанции
        var ema9 = ComputeEMA(closes, 9);
        var ema9Dist = DistanceFrom(closes, ema9);
        var ema21 = ComputeEMA(closes, 21);
        var ema21Dist = DistanceFrom(closes, ema21);

        // Индикаторы (10 признаков для модели)
        var indicators = new Dictionary<string, double[]>
        {
            ["close_norm"] = closeNorm,
            ["volume_norm"] = volumeNorm,
            ["rsi_14"] = ComputeRSI(closes, 14),
            ["macd_norm"] = macdNorm,
            ["macd_signal_norm"] = macdSignalNorm,
            ["bb_width"] = ComputeBBWidth(closes, 20, 2),
            ["ema_9_dist"] = ema9Dist,
            ["ema_21_dist"] = ema21Dist,
            ["volume_ratio"] = ComputeVolumeRatio(volumes, 20),
            ["volatility_20"] = ComputeVolatility(closes, 20),
        };

        // Сборка окон
        int n = candles.Count;
        var windows = new List<double[]>();
        for (int i = windowSize; i < n; i++)
        {
            var window = new double[featureNames.Length];
            for (int f = 0; f < featureNames.Length; f++)
            {
                if (indicators.TryGetValue(featureNames[f], out var series))
                    window[f] = series[i];
                else
                    window[f] = 0;
            }
            windows.Add(window);
        }
        return windows;
    }

    /// <summary>
    /// Z-score нормализация.
    /// </summary>
    static double[] ZScore(List<double> data)
    {
        var mean = data.Average();
        var std = Math.Sqrt(data.Average(v => (v - mean) * (v - mean)));
        if (std < 1e-10) std = 1;
        return data.Select(v => (v - mean) / std).ToArray();
    }

    // === Индикаторы ===

    static double[] ComputeReturns(List<double> closes)
    {
        var r = new double[closes.Count];
        for (int i = 1; i < closes.Count; i++)
            r[i] = (closes[i] - closes[i - 1]) / closes[i - 1];
        return r;
    }

    static double[] ComputeLogReturns(List<double> closes)
    {
        var r = new double[closes.Count];
        for (int i = 1; i < closes.Count; i++)
            r[i] = Math.Log(closes[i] / closes[i - 1]);
        return r;
    }

    static double[] ComputeSMA(List<double> data, int period)
    {
        var result = new double[data.Count];
        double sum = 0;
        for (int i = 0; i < data.Count; i++)
        {
            sum += data[i];
            if (i >= period) sum -= data[i - period];
            if (i >= period - 1) result[i] = sum / period;
        }
        return result;
    }

    static double[] ComputeEMA(List<double> data, int period)
    {
        var result = new double[data.Count];
        double k = 2.0 / (period + 1);
        result[0] = data[0];
        for (int i = 1; i < data.Count; i++)
            result[i] = data[i] * k + result[i - 1] * (1 - k);
        return result;
    }

    static double[] ComputeRSI(List<double> closes, int period)
    {
        var rsi = new double[closes.Count];
        var gains = new double[closes.Count];
        var losses = new double[closes.Count];

        for (int i = 1; i < closes.Count; i++)
        {
            var delta = closes[i] - closes[i - 1];
            gains[i] = delta > 0 ? delta : 0;
            losses[i] = delta < 0 ? -delta : 0;
        }

        double avgGain = 0, avgLoss = 0;
        for (int i = 0; i < closes.Count; i++)
        {
            avgGain += gains[i];
            avgLoss += losses[i];
            if (i >= period)
            {
                avgGain -= gains[i - period];
                avgLoss -= losses[i - period];
            }
            if (i >= period - 1)
            {
                var rs = avgLoss > 0 ? avgGain / avgLoss : 100;
                rsi[i] = 100 - 100 / (1 + rs);
            }
        }
        return rsi;
    }

    static double[] ComputeMACD(List<double> closes)
    {
        var ema12 = ComputeEMA(closes, 12);
        var ema26 = ComputeEMA(closes, 26);
        var macd = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            macd[i] = ema12[i] - ema26[i];
        return macd;
    }

    static double[] ComputeMACDSignal(List<double> closes)
    {
        var macd = ComputeMACD(closes);
        return ComputeEMA(macd.ToList(), 9);
    }

    static double[] ComputeMACDHist(List<double> closes)
    {
        var macd = ComputeMACD(closes);
        var signal = ComputeMACDSignal(closes);
        var hist = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            hist[i] = macd[i] - signal[i];
        return hist;
    }

    static double[] ComputeBBUpper(List<double> closes, int period, double mult)
    {
        var sma = ComputeSMA(closes, period);
        var upper = new double[closes.Count];
        for (int i = period - 1; i < closes.Count; i++)
        {
            double sumSq = 0;
            for (int j = i - period + 1; j <= i; j++)
                sumSq += (closes[j] - sma[i]) * (closes[j] - sma[i]);
            upper[i] = sma[i] + mult * Math.Sqrt(sumSq / period);
        }
        return upper;
    }

    static double[] ComputeBBLower(List<double> closes, int period, double mult)
    {
        var sma = ComputeSMA(closes, period);
        var lower = new double[closes.Count];
        for (int i = period - 1; i < closes.Count; i++)
        {
            double sumSq = 0;
            for (int j = i - period + 1; j <= i; j++)
                sumSq += (closes[j] - sma[i]) * (closes[j] - sma[i]);
            lower[i] = sma[i] - mult * Math.Sqrt(sumSq / period);
        }
        return lower;
    }

    static double[] ComputeBBMiddle(List<double> closes, int period) => ComputeSMA(closes, period);

    static double[] ComputeBBWidth(List<double> closes, int period, double mult)
    {
        var upper = ComputeBBUpper(closes, period, mult);
        var lower = ComputeBBLower(closes, period, mult);
        var sma = ComputeSMA(closes, period);
        var width = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            width[i] = sma[i] > 0 ? (upper[i] - lower[i]) / sma[i] : 0;
        return width;
    }

    static double[] ComputeBBPctB(List<double> closes, int period, double mult)
    {
        var upper = ComputeBBUpper(closes, period, mult);
        var lower = ComputeBBLower(closes, period, mult);
        var pctb = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
        {
            var range = upper[i] - lower[i];
            pctb[i] = range > 0 ? (closes[i] - lower[i]) / range : 0.5;
        }
        return pctb;
    }

    static double[] ComputeATR(List<double> highs, List<double> lows, List<double> closes, int period)
    {
        var tr = new double[closes.Count];
        for (int i = 1; i < closes.Count; i++)
        {
            var hl = highs[i] - lows[i];
            var hc = Math.Abs(highs[i] - closes[i - 1]);
            var lc = Math.Abs(lows[i] - closes[i - 1]);
            tr[i] = Math.Max(hl, Math.Max(hc, lc));
        }

        var atr = new double[closes.Count];
        double sum = 0;
        for (int i = 0; i < closes.Count; i++)
        {
            sum += tr[i];
            if (i >= period) sum -= tr[i - period];
            if (i >= period - 1) atr[i] = sum / period;
        }
        return atr;
    }

    static double[] ComputeADX(List<double> highs, List<double> lows, List<double> closes, int period)
    {
        var plusDI = ComputePlusDI(highs, lows, closes, period);
        var minusDI = ComputeMinusDI(highs, lows, closes, period);
        var dx = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
        {
            var sum = plusDI[i] + minusDI[i];
            dx[i] = sum > 0 ? 100 * Math.Abs(plusDI[i] - minusDI[i]) / sum : 0;
        }
        return ComputeSMA(dx.ToList(), period);
    }

    static double[] ComputePlusDI(List<double> highs, List<double> lows, List<double> closes, int period)
    {
        var plusDM = new double[highs.Count];
        for (int i = 1; i < highs.Count; i++)
        {
            var up = highs[i] - highs[i - 1];
            var down = lows[i - 1] - lows[i];
            plusDM[i] = (up > down && up > 0) ? up : 0;
        }
        var atr = ComputeATR(highs, lows, closes, period);
        var di = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            di[i] = atr[i] > 0 ? 100 * ComputeSMA(plusDM.ToList(), period)[i] / atr[i] : 0;
        return di;
    }

    static double[] ComputeMinusDI(List<double> highs, List<double> lows, List<double> closes, int period)
    {
        var minusDM = new double[highs.Count];
        for (int i = 1; i < highs.Count; i++)
        {
            var up = highs[i] - highs[i - 1];
            var down = lows[i - 1] - lows[i];
            minusDM[i] = (down > up && down > 0) ? down : 0;
        }
        var atr = ComputeATR(highs, lows, closes, period);
        var di = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            di[i] = atr[i] > 0 ? 100 * ComputeSMA(minusDM.ToList(), period)[i] / atr[i] : 0;
        return di;
    }

    static double[] ComputeStochK(List<double> highs, List<double> lows, List<double> closes, int period)
    {
        var k = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
        {
            double low = double.MaxValue, high = double.MinValue;
            for (int j = Math.Max(0, i - period + 1); j <= i; j++)
            {
                low = Math.Min(low, lows[j]);
                high = Math.Max(high, highs[j]);
            }
            k[i] = high > low ? 100 * (closes[i] - low) / (high - low) : 50;
        }
        return k;
    }

    static double[] ComputeStochD(List<double> highs, List<double> lows, List<double> closes, int period)
    {
        var k = ComputeStochK(highs, lows, closes, period);
        return ComputeSMA(k.ToList(), 3);
    }

    static double[] ComputeWilliamsR(List<double> highs, List<double> lows, List<double> closes, int period)
    {
        var wr = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
        {
            double high = double.MinValue;
            for (int j = Math.Max(0, i - period + 1); j <= i; j++)
                high = Math.Max(high, highs[j]);
            double low = double.MaxValue;
            for (int j = Math.Max(0, i - period + 1); j <= i; j++)
                low = Math.Min(low, lows[j]);
            wr[i] = high > low ? -100 * (high - closes[i]) / (high - low) : -50;
        }
        return wr;
    }

    static double[] ComputeCCI(List<double> highs, List<double> lows, List<double> closes, int period)
    {
        var tp = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            tp[i] = (highs[i] + lows[i] + closes[i]) / 3;

        var sma = ComputeSMA(tp.ToList(), period);
        var cci = new double[closes.Count];
        for (int i = period - 1; i < closes.Count; i++)
        {
            double mad = 0;
            for (int j = i - period + 1; j <= i; j++)
                mad += Math.Abs(tp[j] - sma[i]);
            mad /= period;
            cci[i] = mad > 0 ? (tp[i] - sma[i]) / (0.015 * mad) : 0;
        }
        return cci;
    }

    static double[] ComputeMFI(List<double> highs, List<double> lows, List<double> closes, List<double> volumes, int period)
    {
        var tp = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            tp[i] = (highs[i] + lows[i] + closes[i]) / 3;

        var mf = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            mf[i] = tp[i] * volumes[i];

        var posMF = new double[closes.Count];
        var negMF = new double[closes.Count];
        for (int i = 1; i < closes.Count; i++)
        {
            posMF[i] = tp[i] > tp[i - 1] ? mf[i] : 0;
            negMF[i] = tp[i] < tp[i - 1] ? mf[i] : 0;
        }

        var mfi = new double[closes.Count];
        for (int i = period; i < closes.Count; i++)
        {
            double pSum = 0, nSum = 0;
            for (int j = i - period + 1; j <= i; j++)
            {
                pSum += posMF[j];
                nSum += negMF[j];
            }
            var ratio = nSum > 0 ? pSum / nSum : 100;
            mfi[i] = 100 - 100 / (1 + ratio);
        }
        return mfi;
    }

    static double[] ComputeVolumeRatio(List<double> volumes, int period)
    {
        var sma = ComputeSMA(volumes, period);
        var ratio = new double[volumes.Count];
        for (int i = 0; i < volumes.Count; i++)
            ratio[i] = sma[i] > 0 ? volumes[i] / sma[i] : 1;
        return ratio;
    }

    static double[] ComputeOBV(List<double> closes, List<double> volumes)
    {
        var obv = new double[closes.Count];
        obv[0] = volumes[0];
        for (int i = 1; i < closes.Count; i++)
            obv[i] = obv[i - 1] + (closes[i] > closes[i - 1] ? volumes[i] : -volumes[i]);
        return obv;
    }

    static double[] ComputeVWAP(List<double> highs, List<double> lows, List<double> closes, List<double> volumes)
    {
        var vwap = new double[closes.Count];
        double cumTPV = 0, cumV = 0;
        for (int i = 0; i < closes.Count; i++)
        {
            var tp = (highs[i] + lows[i] + closes[i]) / 3;
            cumTPV += tp * volumes[i];
            cumV += volumes[i];
            vwap[i] = cumV > 0 ? cumTPV / cumV : closes[i];
        }
        return vwap;
    }

    static double[] ComputeVolatility(List<double> closes, int period)
    {
        var sma = ComputeSMA(closes, period);
        var vol = new double[closes.Count];
        for (int i = period - 1; i < closes.Count; i++)
        {
            double sumSq = 0;
            for (int j = i - period + 1; j <= i; j++)
                sumSq += (closes[j] - sma[i]) * (closes[j] - sma[i]);
            vol[i] = sma[i] > 0 ? Math.Sqrt(sumSq / period) / sma[i] : 0;
        }
        return vol;
    }

    static double[] ComputeMomentum(List<double> closes, int period)
    {
        var mom = new double[closes.Count];
        for (int i = period; i < closes.Count; i++)
            mom[i] = closes[i - period] > 0 ? closes[i] / closes[i - period] - 1 : 0;
        return mom;
    }

    static double[] ComputeROC(List<double> closes, int period)
    {
        var roc = new double[closes.Count];
        for (int i = period; i < closes.Count; i++)
            roc[i] = closes[i - period] > 0 ? (closes[i] - closes[i - period]) / closes[i - period] : 0;
        return roc;
    }

    static double[] DistanceFrom(List<double> closes, double[] sma)
    {
        var dist = new double[closes.Count];
        for (int i = 0; i < closes.Count; i++)
            dist[i] = sma[i] > 0 ? (closes[i] - sma[i]) / sma[i] : 0;
        return dist;
    }

    static double[] ComputeDoji(List<Candle> candles)
    {
        var r = new double[candles.Count];
        for (int i = 0; i < candles.Count; i++)
        {
            var range = candles[i].High - candles[i].Low;
            r[i] = range > 0 && Math.Abs(candles[i].Close - candles[i].Open) / range < 0.1 ? 1 : 0;
        }
        return r;
    }

    static double[] ComputeHammer(List<Candle> candles)
    {
        var r = new double[candles.Count];
        for (int i = 0; i < candles.Count; i++)
        {
            var range = candles[i].High - candles[i].Low;
            r[i] = range > 0 && (candles[i].Close - candles[i].Low) / range > 0.7 ? 1 : 0;
        }
        return r;
    }

    static double[] ComputeShootingStar(List<Candle> candles)
    {
        var r = new double[candles.Count];
        for (int i = 0; i < candles.Count; i++)
        {
            var range = candles[i].High - candles[i].Low;
            r[i] = range > 0 && (candles[i].High - candles[i].Close) / range > 0.7 ? 1 : 0;
        }
        return r;
    }
}
