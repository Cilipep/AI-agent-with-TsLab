using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace NNInference;

/// <summary>
/// Торговый исполнитель: размещение ордеров через Binance REST API.
/// Использует HttpClient напрямую (без Binance.Net зависимостей).
/// </summary>
class BinanceTrader : IDisposable
{
    private readonly HttpClient _http;
    private readonly TradeConfig _config;
    private readonly List<TradeRecord> _tradeHistory = new();
    private readonly string _baseUrl;

    public BinanceTrader(TradeConfig config)
    {
        _config = config;
        _baseUrl = config.UseDemo
            ? "https://testnet.binance.vision"
            : "https://api.binance.com";

        var handler = new HttpClientHandler
        {
            SslProtocols = System.Security.Authentication.SslProtocols.Tls12 | System.Security.Authentication.SslProtocols.Tls13,
            AutomaticDecompression = System.Net.DecompressionMethods.All
        };
        _http = new HttpClient(handler)
        {
            BaseAddress = new Uri(_baseUrl),
            Timeout = TimeSpan.FromSeconds(30)
        };
    }

    /// <summary>
    /// Проверка подключения и баланса.
    /// </summary>
    public async Task<bool> ConnectAsync()
    {
        Console.WriteLine($"[Trader] Подключение к {(_config.UseDemo ? "DEMO" : "MAINNET")}...");

        try
        {
            var timeResp = await GetAsync("/api/v3/time");
            if (timeResp.ValueKind == JsonValueKind.Undefined)
            {
                Console.WriteLine("[Trader] Ping failed");
                return false;
            }
            Console.WriteLine($"[Trader] Серверное время: {DateTimeOffset.FromUnixTimeMilliseconds(timeResp.GetProperty("serverTime").GetInt64())}");

            var account = await SignedRequestAsync("/api/v3/account", new Dictionary<string, string>());
            if (account.ValueKind != JsonValueKind.Undefined)
            {
                var balances = account.GetProperty("balances").EnumerateArray();
                foreach (var b in balances)
                {
                    var asset = b.GetProperty("asset").GetString()!;
                    var free = decimal.Parse(b.GetProperty("free").GetString()!, System.Globalization.CultureInfo.InvariantCulture);
                    if (free > 0 && (asset == "USDT" || asset == "BTC" || asset == "ETH"))
                        Console.WriteLine($"[Trader] {asset}: {free}");
                }
            }

            Console.WriteLine("[Trader] Подключение успешно\n");
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Trader] Ошибка подключения: {ex.Message}");
            return false;
        }
    }

    /// <summary>
    /// Получение текущей цены.
    /// </summary>
    public async Task<decimal> GetPriceAsync(string symbol)
    {
        var resp = await GetAsync($"/api/v3/ticker/price?symbol={symbol}");
        if (resp.ValueKind == JsonValueKind.Undefined)
            throw new Exception("Ошибка получения цены");
        return decimal.Parse(resp.GetProperty("price").GetString()!, System.Globalization.CultureInfo.InvariantCulture);
    }

    /// <summary>
    /// Получение баланса.
    /// </summary>
    public async Task<(decimal Free, decimal Locked)> GetBalanceAsync(string asset)
    {
        var account = await SignedRequestAsync("/api/v3/account", new Dictionary<string, string>());
        if (account.ValueKind == JsonValueKind.Undefined)
            return (0, 0);

        var balances = account.GetProperty("balances").EnumerateArray();
        foreach (var b in balances)
        {
            if (b.GetProperty("asset").GetString() == asset)
            {
                return (
                    decimal.Parse(b.GetProperty("free").GetString()!, System.Globalization.CultureInfo.InvariantCulture),
                    decimal.Parse(b.GetProperty("locked").GetString()!, System.Globalization.CultureInfo.InvariantCulture)
                );
            }
        }
        return (0, 0);
    }

    /// <summary>
    /// Рыночный ордер на покупку.
    /// </summary>
    public async Task<TradeRecord?> BuyMarketAsync(string symbol, decimal quantity)
    {
        Console.WriteLine($"[Trader] BUY {symbol}: qty={quantity}");

        var parameters = new Dictionary<string, string>
        {
            ["symbol"] = symbol,
            ["side"] = "BUY",
            ["type"] = "MARKET",
            ["quantity"] = quantity.ToString("F6", System.Globalization.CultureInfo.InvariantCulture)
        };

        var resp = await SignedRequestAsync("/api/v3/order", parameters, method: "POST");
        if (resp.ValueKind == JsonValueKind.Undefined)
            return null;

        var price = await GetPriceAsync(symbol);
        var record = new TradeRecord
        {
            OrderId = resp.GetProperty("orderId").GetInt64().ToString(),
            Symbol = symbol,
            Side = "BUY",
            Price = price,
            Quantity = quantity,
            Total = price * quantity,
            Timestamp = DateTime.UtcNow,
            Status = resp.GetProperty("status").GetString()!
        };

        _tradeHistory.Add(record);
        Console.WriteLine($"[Trader] ✓ BUY: {record.Total:F2} USDT @ {record.Price:F2}");
        return record;
    }

    /// <summary>
    /// Рыночный ордер на продажу.
    /// </summary>
    public async Task<TradeRecord?> SellMarketAsync(string symbol, decimal quantity)
    {
        Console.WriteLine($"[Trader] SELL {symbol}: qty={quantity}");

        var parameters = new Dictionary<string, string>
        {
            ["symbol"] = symbol,
            ["side"] = "SELL",
            ["type"] = "MARKET",
            ["quantity"] = quantity.ToString("F6", System.Globalization.CultureInfo.InvariantCulture)
        };

        var resp = await SignedRequestAsync("/api/v3/order", parameters, method: "POST");
        if (resp.ValueKind == JsonValueKind.Undefined)
            return null;

        var price = await GetPriceAsync(symbol);
        var record = new TradeRecord
        {
            OrderId = resp.GetProperty("orderId").GetInt64().ToString(),
            Symbol = symbol,
            Side = "SELL",
            Price = price,
            Quantity = quantity,
            Total = price * quantity,
            Timestamp = DateTime.UtcNow,
            Status = resp.GetProperty("status").GetString()!
        };

        _tradeHistory.Add(record);
        Console.WriteLine($"[Trader] ✓ SELL: {record.Total:F2} USDT @ {record.Price:F2}");
        return record;
    }

    /// <summary>
    /// Исполнение торгового сигнала.
    /// </summary>
    public async Task<TradeRecord?> ExecuteSignalAsync(TradeSignal signal, string symbol)
    {
        if (signal.Type == SignalType.None)
            return null;

        var price = await GetPriceAsync(symbol);
        var (free, _) = await GetBalanceAsync("USDT");

        decimal quantity;
        if (signal.Type == SignalType.Long || signal.Type == SignalType.Short)
        {
            var positionValue = free * (decimal)signal.PositionSizePct;
            quantity = positionValue / price;
            quantity = RoundStepSize(quantity, GetStepSize(symbol));
        }
        else
        {
            var asset = symbol.Replace("USDT", "");
            var (assetFree, _) = await GetBalanceAsync(asset);
            quantity = assetFree;
            if (quantity <= 0)
            {
                Console.WriteLine($"[Trader] Нет позиции для закрытия");
                return null;
            }
        }

        if (quantity <= 0)
        {
            Console.WriteLine($"[Trader] Недостаточно средств");
            return null;
        }

        var todayTrades = _tradeHistory.Count(t => t.Timestamp.Date == DateTime.UtcNow.Date);
        if (todayTrades >= _config.MaxDailyTrades)
        {
            Console.WriteLine($"[Trader] Дневной лимит: {_config.MaxDailyTrades}");
            return null;
        }

        return signal.Type switch
        {
            SignalType.Long => await BuyMarketAsync(symbol, quantity),
            SignalType.CloseLong => await SellMarketAsync(symbol, quantity),
            _ => null
        };
    }

    public List<TradeRecord> GetTradeHistory() => _tradeHistory.ToList();

    // === HTTP helpers ===

    private async Task<JsonElement> GetAsync(string path)
    {
        var resp = await _http.GetAsync(path);
        var json = await resp.Content.ReadAsStringAsync();
        if (!resp.IsSuccessStatusCode)
        {
            Console.WriteLine($"[Trader] GET {path} failed: {resp.StatusCode} {json}");
            return default;
        }
        return JsonSerializer.Deserialize<JsonElement>(json);
    }

    private async Task<JsonElement> SignedRequestAsync(string path,
        Dictionary<string, string> parameters, string method = "GET")
    {
        parameters["timestamp"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds().ToString();
        parameters["recvWindow"] = "5000";

        // Подпись HMAC-SHA256
        var queryString = string.Join("&", parameters.Select(kv => $"{kv.Key}={kv.Value}"));
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(_config.ApiSecret));
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(queryString));
        var signature = BitConverter.ToString(hash).Replace("-", "").ToLower();
        parameters["signature"] = signature;

        var signedQuery = string.Join("&", parameters.Select(kv => $"{kv.Key}={kv.Value}"));

        // Заголовок API ключа
        var request = new HttpRequestMessage();
        request.Headers.Add("X-MBX-APIKEY", _config.ApiKey);

        HttpResponseMessage resp;
        if (method == "POST")
        {
            request.Method = HttpMethod.Post;
            request.RequestUri = new Uri(path, UriKind.Relative);
            request.Content = new StringContent(signedQuery, Encoding.UTF8, "application/x-www-form-urlencoded");
            resp = await _http.SendAsync(request);
        }
        else
        {
            request.Method = HttpMethod.Get;
            request.RequestUri = new Uri($"{path}?{signedQuery}", UriKind.Relative);
            resp = await _http.SendAsync(request);
        }

        var json = await resp.Content.ReadAsStringAsync();
        if (!resp.IsSuccessStatusCode)
        {
            Console.WriteLine($"[Trader] {method} {path} failed: {resp.StatusCode} {json}");
            return default;
        }
        return JsonSerializer.Deserialize<JsonElement>(json);
    }

    private static decimal RoundStepSize(decimal quantity, decimal stepSize)
    {
        if (stepSize <= 0) return quantity;
        return Math.Floor(quantity / stepSize) * stepSize;
    }

    private decimal GetStepSize(string symbol)
    {
        if (symbol.Contains("BTC")) return 0.00001m;
        if (symbol.Contains("ETH")) return 0.001m;
        if (symbol.Contains("SOL")) return 0.01m;
        return 0.001m;
    }

    public void Dispose()
    {
        _http?.Dispose();
    }
}

/// <summary>
/// Конфигурация торговли.
/// </summary>
class TradeConfig
{
    public string ApiKey { get; set; } = "";
    public string ApiSecret { get; set; } = "";
    public bool UseDemo { get; set; } = true;
    public int MaxDailyTrades { get; set; } = 10;
    public decimal MaxPositionPct { get; set; } = 0.02m;
}

/// <summary>
/// Запись о сделке.
/// </summary>
class TradeRecord
{
    public string OrderId { get; set; } = "";
    public string Symbol { get; set; } = "";
    public string Side { get; set; } = "";
    public decimal Price { get; set; }
    public decimal Quantity { get; set; }
    public decimal Total { get; set; }
    public DateTime Timestamp { get; set; }
    public string Status { get; set; } = "";
}
