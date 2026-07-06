# Contracts: Stream vs Values vs PreCalc (How TSLab Actually Calls `Execute`)

This reference is written to be usable in a delivery build (no repo required).

## Core fact: `IStreamHandler` / `IValuesHandler*` are marker interfaces

They do **not** declare `Execute(...)`. TSLab discovers the callable method by reflection and validates it against:
- declared inputs (`[InputsCount]` + `[Input]` attributes and/or arity marker interfaces)
- output type (`[OutputType]`, `[OutputsCount]`)
- method signature shapes that the engine supports in this build

Because signatures vary between builds, do not guess.

## The runtime source of truth (use this first)

1. `GET /api/sdk/contracts`
   - read `observedExecuteSignatures` to see the real `Execute(...)`/`PreCalc(...)` patterns present in this build
   - copy a `templates[]` snippet as a starting point
2. `GET /api/handlers/{typeName}`
   - verify how the API describes your handler inputs/outputs/params after loading

## Mode selection (what you implement)

- **Stream handler** (`IStreamHandler`):
  - Use when the output is a full series (`IList<T>`) computed from one or more series/security inputs.
  - Typical for technical indicators over price/volume.
- **Values handler** (`IValuesHandler` / `IValuesHandlerWithNumber`):
  - Use when the output is a scalar per bar (often over positions/trading analytics).
  - `IValuesHandlerWithNumber` when bar index is part of the signature.
- **Values + PreCalc** (`IValuesHandlerWithPrecalc`):
  - Use when you need a single pre-pass over a stream input (or expensive setup), then cheap per-bar `Execute`.
  - Requires a `PreCalc(...)` method (shape must match supported contracts in this build).

## Arity markers vs `[InputsCount]`

TSLab supports both patterns:

- Attribute:
  - `[InputsCount(n)]` or `[InputsCount(min, max)]`
- Marker interfaces:
  - `IZeroSourceHandler`, `IOneSourceHandler`, `ITwoSourcesHandler`, `IThreeSourcesHandler`, ...

Recommendation for custom DLL indicators:
- Always specify `[InputsCount(...)]` explicitly.
- Optionally implement the marker interface for readability; it should match your actual `Execute(...)` parameters count.

## Examples (safe patterns)

### Stream: 1 series input -> 1 series output

```csharp
using System.Collections.Generic;
using TSLab.Script.Handlers;

[InputsCount(1)]
[Input(0, TemplateTypes.DOUBLE, false, "Source")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class MyStream1 : IStreamHandler
{
    public IList<double> Execute(IList<double> source) => source;
}
```

### Stream: 3 series inputs (H/L/C) -> 1 series output

```csharp
using System.Collections.Generic;
using TSLab.Script.Handlers;

[InputsCount(3)]
[Input(0, TemplateTypes.DOUBLE, false, "High")]
[Input(1, TemplateTypes.DOUBLE, false, "Low")]
[Input(2, TemplateTypes.DOUBLE, false, "Close")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class MyStream3 : IStreamHandler
{
    public IList<double> Execute(IList<double> high, IList<double> low, IList<double> close)
    {
        // compute and return a series
        return close;
    }
}
```

### Values: scalar per bar + bar index

```csharp
using TSLab.Script.Handlers;

[InputsCount(1)]
[Input(0, TemplateTypes.DOUBLE, true, "Value")]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class MyValues : IValuesHandlerWithNumber
{
    public double Execute(double value, int barNum) => value;
}
```

## Critical rule: `InputAttribute.IsValue` matters for values/precalc

For values-style handlers, inputs can be:
- stream inputs (a full series)
- value inputs (a scalar for the current bar)

The engine uses the `Input(..., isValue: ...)` flag to decide what wiring is allowed.

Practical guidance:
- For stream inputs to a stream handler: `isValue:false`
- For value inputs to a values handler: `isValue:true`
- For `IValuesHandlerWithPrecalc`, if you want to allow value wiring on some inputs, you must mark those `[Input(..., isValue:true, ...)]`

If you are unsure, copy an existing supported signature from:
- `GET /api/sdk/contracts` templates
- or a similar built-in handler via `GET /api/handlers/{typeName}`

