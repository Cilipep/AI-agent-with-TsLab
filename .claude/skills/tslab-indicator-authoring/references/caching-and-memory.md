# Caching, Pooling, and Optimization Safety

This reference is written to be usable in a delivery build (no repo required).

## `IContext.GetData(...)` (per-run deterministic cache)

Important: `IContext.GetData(...)` takes **`string[] parameters`**, not `object[]`.

Typical overloads:
- `IList<double> GetData(string handlerName, string[] parameters, CacheObjectMaker<IList<double>> maker)`
- `IList<bool> GetData(...)`
- `IList<int> GetData(...)`
- `IList<Double2> GetData(...)`
- `ISecurity GetData(...)`

### Rules

- `handlerName` must be a stable identifier for what you're caching.
  - Common pattern: use a short string like `"RSI"`, `"Highest"`, `"ATR"`, or your handler type name.
- `parameters` must include **everything** that influences the output:
  - numeric periods/thresholds
  - flags/modes
  - security identity (`security.CacheName`)
  - anything else that changes the result
- Convert numbers to strings using `CultureInfo.InvariantCulture` to avoid locale-dependent keys.
- Treat cached results as **immutable**. Never mutate arrays/lists returned from cache.
- If the cached result is a pooled array (created via `Context.GetArray` or via a helper overload that used pooling),
  do **not** call `ReleaseArray` on it.

### Minimal `GetData` example (EMA cache)

```csharp
using System.Collections.Generic;
using System.Globalization;
using TSLab.Script.Helpers;
using TSLab.Script.Handlers;
using TSLab.Utils;

public sealed class EmaCached : IStreamHandler, IContextUses
{
    public IContext Context { get; set; } = null!;

    public int Period { get; set; } = 14;

    public IList<double> Execute(IList<double> source)
    {
        var p = Period < 1 ? 1 : Period;
        return Context.GetData(
            handlerName: nameof(EmaCached),
            parameters: new[]
            {
                p.ToString(CultureInfo.InvariantCulture),
                source.Count.ToString(CultureInfo.InvariantCulture),
            },
            maker: () => Series.EMA((IReadOnlyList<double>)source.AsReadOnly(), p));
    }
}
```

### Realistic `GetData` example (cache expensive intermediates for a security)

```csharp
using System.Collections.Generic;
using System.Globalization;
using TSLab.Script;
using TSLab.Script.Helpers;
using TSLab.Script.Handlers;
using TSLab.Utils;

public sealed class StochKLike : IStreamHandler, IContextUses
{
    public IContext Context { get; set; } = null!;

    public int Period { get; set; } = 14;

    public IList<double> Execute(ISecurity source)
    {
        var p = Period < 1 ? 1 : Period;
        var pStr = p.ToString(CultureInfo.InvariantCulture);

        // CacheName is explicitly documented to be suitable for IContext.GetData keys.
        var secKey = source.CacheName;

        var highestHigh = Context.GetData(
            handlerName: "HighestHigh",
            parameters: new[] { pStr, secKey },
            maker: () => Series.Highest((IReadOnlyList<double>)source.HighPrices.AsReadOnly(), p));

        var lowestLow = Context.GetData(
            handlerName: "LowestLow",
            parameters: new[] { pStr, secKey },
            maker: () => Series.Lowest((IReadOnlyList<double>)source.LowPrices.AsReadOnly(), p));

        var bars = source.Bars;
        var res = Context.GetArray<double>(bars.Count);
        for (var i = 0; i < bars.Count; i++)
        {
            var range = highestHigh[i] - lowestLow[i];
            res[i] = range == 0 ? 0 : 100 * (bars[i].Close - lowestLow[i]) / range;
        }
        return res;
    }
}
```

## Array pooling (`GetArray<T>` / `ReleaseArray(Array)`)

`IContext` implements `IMemoryManagement` (via `IMemoryContext`), so it can pool arrays.

### Rules

- Release only temporary buffers that you do **not** return and do **not** cache.
- If you return an array as the handler output, do not release it.
- If you store an array/list in `Context.GetData(...)`, do not release it.

Pattern:

```csharp
var tmp = Context.GetArray<double>(count);
try
{
    // fill/use tmp
}
finally
{
    Context.ReleaseArray(tmp);
}
```

## Optimization behavior

- During optimization loops `Context.IsOptimization` is usually `true`.
- Use it to skip work that is not required for numeric results (UI-only, I/O, logging-heavy paths).
- Caching and pooling have the biggest payoff during optimization because the same graph is executed many times.

## Global cache (advanced)

`IContext` also exposes a global cache:
- `StoreGlobalObject(...)`
- `LoadGlobalObject(...)`

This cache can be shared across scripts/agents and can be cleared under memory pressure.
Use it only when you understand lifetime/eviction behavior and your keys are collision-safe.

