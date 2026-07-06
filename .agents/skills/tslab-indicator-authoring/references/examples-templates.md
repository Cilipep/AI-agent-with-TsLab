# Examples and Templates (Shipped With This Skill)

This file is **self-contained** and designed to be used in a delivery build (no repo required).

Notes:
- `IStreamHandler` / `IValuesHandler*` are marker interfaces; supported `Execute(...)` signatures are build-dependent.
- Always use `GET /api/sdk/contracts` and `GET /api/handlers/{typeName}` to validate the exact contract.
- Prefer canonical helpers:
  - `TSLab.Script.Helpers.Series`
  - `TSLab.Script.Helpers.Indicators`
- Many `Series.*` methods accept `IReadOnlyList<T>`; when your input is `IList<T>`, use `source.AsReadOnly()` (from `TSLab.Utils`) and cast.
- `IContext.GetData(...)` uses `string[] parameters` (cache keys), not `object[]`.

## Template 1: Stream DOUBLE indicator (EMA) with Period

Use when:
- output is a numeric series (`IList<double>`)
- can compute in bulk via `Series.*`

```csharp
using System.Collections.Generic;
using System.ComponentModel;
using TSLab.Script.Handlers;
using TSLab.Script.Helpers;
using TSLab.Utils;

[HandlerCategory(HandlerCategories.Indicators)]
[Description("Computes EMA(Source, Period).")]
[InputsCount(1)]
[Input(0, TemplateTypes.DOUBLE, false, "Source")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class EmaTemplateHandler : IStreamHandler, IContextUses
{
    public IContext Context { get; set; } = null!;

    [HandlerParameter(true, "14", Min = "1", Step = "1")]
    public int Period { get; set; } = 14;

    public IList<double> Execute(IList<double> source)
    {
        var p = Period < 1 ? 1 : Period;
        return Series.EMA((IReadOnlyList<double>)source.AsReadOnly(), p, Context);
    }
}
```

## Template 2: Stream indicator with caching via `Context.GetData(...)`

Use when:
- the same expensive series is reused across the graph
- you want deterministic caching within a run

```csharp
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using TSLab.Script.Handlers;
using TSLab.Script.Helpers;
using TSLab.Utils;

[HandlerCategory(HandlerCategories.Indicators)]
[Description("Caches EMA(Source, Period) via Context.GetData().")]
[InputsCount(1)]
[Input(0, TemplateTypes.DOUBLE, false, "Source")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class EmaCachedTemplateHandler : IStreamHandler, IContextUses
{
    public IContext Context { get; set; } = null!;

    [HandlerParameter(true, "14", Min = "1", Step = "1")]
    public int Period { get; set; } = 14;

    public IList<double> Execute(IList<double> source)
    {
        var p = Period < 1 ? 1 : Period;

        // Parameters must include everything that influences output.
        return Context.GetData(
            handlerName: nameof(EmaCachedTemplateHandler),
            parameters: new[]
            {
                p.ToString(CultureInfo.InvariantCulture),
                source.Count.ToString(CultureInfo.InvariantCulture),
            },
            // Prefer non-pooled allocation for cached series unless you fully control the lifetime.
            maker: () => Series.EMA((IReadOnlyList<double>)source.AsReadOnly(), p));
    }
}
```

## Template 3: Multi-input stream handler (OHLC -> Typical Price)

Use when:
- you need 3+ series inputs (high/low/close etc.)

```csharp
using System;
using System.Collections.Generic;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(3)]
[Input(0, TemplateTypes.DOUBLE, false, "High")]
[Input(1, TemplateTypes.DOUBLE, false, "Low")]
[Input(2, TemplateTypes.DOUBLE, false, "Close")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class TypicalPriceStreamHandler : IStreamHandler, IContextUses
{
    public IContext Context { get; set; } = null!;

    public IList<double> Execute(IList<double> high, IList<double> low, IList<double> close)
    {
        var count = Math.Min(high.Count, Math.Min(low.Count, close.Count));
        if (count <= 0)
            return Array.Empty<double>();

        var res = Context.GetArray<double>(count);
        for (var i = 0; i < count; i++)
            res[i] = (high[i] + low[i] + close[i]) / 3.0;
        return res;
    }
}
```

## Template 4: `ISecurity` input + cached intermediates (StochK-like)

Use when:
- input is `ISecurity` (bars/ohlc)
- you want to cache helper series keyed by `security.CacheName`

```csharp
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using TSLab.Script;
using TSLab.Script.Handlers;
using TSLab.Script.Helpers;
using TSLab.Utils;

[HandlerCategory(HandlerCategories.Indicators)]
[Description("Stochastic-like example: uses cached Highest/Lowest over Security bars.")]
[InputsCount(1)]
[Input(0, TemplateTypes.SECURITY, false, "Security")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class StochKLikeTemplate : IStreamHandler, IContextUses
{
    public IContext Context { get; set; } = null!;

    [HandlerParameter(true, "14", Min = "1", Step = "1")]
    public int Period { get; set; } = 14;

    public IList<double> Execute(ISecurity source)
    {
        var p = Period < 1 ? 1 : Period;
        var pStr = p.ToString(CultureInfo.InvariantCulture);
        var secKey = source.CacheName;

        var high = Context.GetData(
            handlerName: "HighestHigh",
            parameters: new[] { pStr, secKey },
            maker: () => Series.Highest((IReadOnlyList<double>)source.HighPrices.AsReadOnly(), p));

        var low = Context.GetData(
            handlerName: "LowestLow",
            parameters: new[] { pStr, secKey },
            maker: () => Series.Lowest((IReadOnlyList<double>)source.LowPrices.AsReadOnly(), p));

        var bars = source.Bars;
        var res = Context.GetArray<double>(bars.Count);
        for (var i = 0; i < bars.Count; i++)
        {
            var range = high[i] - low[i];
            res[i] = range == 0 ? 0 : 100 * (bars[i].Close - low[i]) / range;
        }
        return res;
    }
}
```

## Template 5: Values handler with bar number

Use when:
- logic is per-bar and you need the bar index

```csharp
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(1)]
[Input(0, TemplateTypes.DOUBLE, true, "Value")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class ValuesWithNumberTemplateHandler : IValuesHandlerWithNumber
{
    public double Execute(double value, int barNum) => value;
}
```

## Template 6: Values handler with `PreCalc(...)` (skeleton)

Warning:
- The exact `PreCalc(...)` + `Execute(...)` signatures used for precalc handlers are build-dependent.
- Always check `GET /api/sdk/contracts` and copy the closest template/signature.

```csharp
using System.Collections.Generic;
using System.ComponentModel;
using TSLab.Script.Handlers;
using TSLab.Script.Helpers;
using TSLab.Utils;

[HandlerCategory(HandlerCategories.Indicators)]
[Description("Skeleton: precalc stream input once, then return a scalar per bar.")]
[InputsCount(1)]
[Input(0, TemplateTypes.DOUBLE, false, "Source")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class PrecalcValuesSkeleton : IValuesHandlerWithPrecalc, IContextUses
{
    public IContext Context { get; set; } = null!;

    private IList<double>? ema;

    [HandlerParameter(true, "14", Min = "1", Step = "1")]
    public int Period { get; set; } = 14;

    public void PreCalc(IList<double> source)
    {
        ema = Series.EMA((IReadOnlyList<double>)source.AsReadOnly(), Period);
    }

    // Many builds use: Execute(<value inputs>, int barNum).
    // If your build expects a different signature, adjust based on /api/sdk/contracts.
    public double Execute(double value, int barNum)
    {
        var e = ema;
        if (e == null || e.Count == 0)
            return value;
        if ((uint)barNum >= (uint)e.Count)
            barNum = e.Count - 1;
        return e[barNum];
    }
}
```

## Template 7: Values indicator over positions (trading analytics)

```csharp
using TSLab.Script;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Position)]
[InputsCount(1)]
[Input(0, TemplateTypes.POSITIONS, true, "Positions")]
[OutputType(TemplateTypes.INT)]
public sealed class ActivePositionsCountTemplateHandler : IValuesHandlerWithNumber
{
    public int Execute(IPositionsList positions, int barNum)
    {
        var active = positions.GetActiveForBar(barNum);
        return active?.Count ?? 0;
    }
}
```

## Resource strings for handler display name/description (DLL, localized)

To provide better docs for handler blocks, embed resources in your DLL.

Expected keys (short type name):
- Display name: `<TypeName>.Name`
- Description: `<TypeName>.Description`
- Parameter display name: `<TypeName>.<ParamName>.Name`
- Parameter description: `<TypeName>.<ParamName>.Description`

Minimal `Properties/Resources.resx` example (add more cultures as `Resources.ru-RU.resx`, `Resources.en-US.resx`, etc.):

```xml
<?xml version="1.0" encoding="utf-8"?>
<root>
  <data name="EmaTemplateHandler.Name" xml:space="preserve">
    <value>EMA</value>
  </data>
  <data name="EmaTemplateHandler.Description" xml:space="preserve">
    <value>Exponential moving average of Source with Period.</value>
  </data>
</root>
```

Upload workflow:
- Disk: drop `.dll` to HandlersFolder (plus `.pdb` for debugging)
- DB: `POST /api/indicator-dlls/{name}` with multipart `file` and optional `description`

