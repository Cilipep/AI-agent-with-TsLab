using Binance.Net.Clients;
using Binance.Net.Objects.Models.Spot;

namespace NNInference;

/// <summary>
/// Получение свечей с Binance через Binance.Net.
/// Публичный API — ключи не нужны.
/// </summary>
static class BinanceDataFetcher
{
    private static readonly BinanceRestClient Client = new();

    public static async Task<List<Candle>> GetKlinesAsync(string symbol, string interval, int limit)
    {
        var binanceInterval = MapInterval(interval);

        var result = await Client.SpotApi.ExchangeData.GetKlinesAsync(
            symbol, binanceInterval, limit: limit);

        if (!result.Success)
            throw new Exception($"Binance API ошибка: {result.Error?.Message}");

        var candles = result.Data.Select(k => new Candle
        {
            OpenTime = k.OpenTime,
            Open = (double)k.OpenPrice,
            High = (double)k.HighPrice,
            Low = (double)k.LowPrice,
            Close = (double)k.ClosePrice,
            Volume = (double)k.Volume,
        }).ToList();

        return candles;
    }

    private static Binance.Net.Enums.KlineInterval MapInterval(string interval) => interval switch
    {
        "1m" => Binance.Net.Enums.KlineInterval.OneMinute,
        "5m" => Binance.Net.Enums.KlineInterval.FiveMinutes,
        "15m" => Binance.Net.Enums.KlineInterval.FifteenMinutes,
        "30m" => Binance.Net.Enums.KlineInterval.ThirtyMinutes,
        "1h" => Binance.Net.Enums.KlineInterval.OneHour,
        "4h" => Binance.Net.Enums.KlineInterval.FourHour,
        "1d" => Binance.Net.Enums.KlineInterval.OneDay,
        "1w" => Binance.Net.Enums.KlineInterval.OneWeek,
        _ => Binance.Net.Enums.KlineInterval.OneHour
    };
}

/// <summary>
/// Свеча OHLCV.
/// </summary>
class Candle
{
    public DateTime OpenTime { get; set; }
    public double Open { get; set; }
    public double High { get; set; }
    public double Low { get; set; }
    public double Close { get; set; }
    public double Volume { get; set; }
}
