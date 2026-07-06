# Series and Indicators Helpers (Mandatory)

This reference is written to be usable in a delivery build (no repo required).

TSLab provides two canonical helper APIs for indicators:

- `TSLab.Script.Helpers.Series`: bulk (whole-series) computations like EMA/SMA/RSI/Highest/Lowest/StDev/ATR, etc.
- `TSLab.Script.Helpers.Indicators`: per-bar helper functions (e.g. `TrueRange(...)`), usually used internally by `Series`.

## Critical type rule: `Series.*` often wants `IReadOnlyList<T>`

Many `Series.*` methods accept `IReadOnlyList<double>` while handler `Execute(...)` inputs are frequently `IList<double>`.

Use the TSLab utility adapter:
- `source.AsReadOnly()` (extension method in `TSLab.Utils`)
- then cast to `IReadOnlyList<T>` when needed.

Example:

```csharp
using System.Collections.Generic;
using TSLab.Script.Helpers;
using TSLab.Utils;

public static IList<double> CalcEma(IList<double> source, int period, TSLab.Script.Handlers.IContext ctx)
{
    return Series.EMA((IReadOnlyList<double>)source.AsReadOnly(), period, ctx);
}
```

## Pass `Context` into helpers when an overload supports it

If a `Series.*` overload accepts `IMemoryContext` (or `IContext`), pass the handler `Context`:
- helper internals can use pooled arrays (`GetArray` / `ReleaseArray`)
- reduces GC pressure in optimizations

If the result is cached in `Context.GetData(...)` or stored long-term, prefer a non-pooled overload (no `Context`) unless you fully understand lifetime implications.

## Common recipes (copy/paste)

### EMA (bulk series)

```csharp
using System.Collections.Generic;
using TSLab.Script.Helpers;
using TSLab.Utils;

public IList<double> Execute(IList<double> source)
{
    return Series.EMA((IReadOnlyList<double>)source.AsReadOnly(), Period, Context);
}
```

### ATR / Average True Range from OHLC bars

`ISecurity.Bars` is already `IReadOnlyList<IDataBar>`, so no adapter is needed.

```csharp
using System.Collections.Generic;
using TSLab.Script;
using TSLab.Script.Helpers;
using TSLab.Script.Handlers;

public sealed class AtrFromSecurity : IStreamHandler, IContextUses
{
    public IContext Context { get; set; } = null!;

    [HandlerParameter(true, "14", Min = "1", Step = "1")]
    public int Period { get; set; } = 14;

    public IList<double> Execute(ISecurity security)
    {
        return Series.AverageTrueRange(security.Bars, Period, Context);
    }
}
```

### True Range per bar (low-level helper)

```csharp
using TSLab.Script;
using TSLab.Script.Helpers;

public double GetTr(ISecurity sec, int barNum)
{
    return Indicators.TrueRange(sec.Bars, barNum);
}
```

## Avoid common mistakes

- Do not allocate arrays in a per-bar loop if you can compute the series once via `Series.*`.
- If you allocate temporary buffers via pooling:
  - acquire via `Context.GetArray<T>(count)`
  - release via `Context.ReleaseArray((Array)buffer)` (only if you do **not** return/cache the buffer)
- Do not mutate arrays/lists returned from `Context.GetData(...)` (treat cached data as immutable).

