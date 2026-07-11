---
name: tslab-csharp-handler-lifecycle
description: "End-to-end C# handler lifecycle for TSLab 3.0: compile with dotnet build, upload DLL via /api/indicator-dlls, verify handler registration, create test script, and run lifecycle. Handles TSLab 3.0 API quirks (IStreamHandler vs IExternalScript, HandlerParameter attribute syntax, ConverterItem block type)."
---

# C# Handler Compile→Upload→Test Lifecycle (TSLab 3.0)

Use this skill when the user asks to **compile a C# handler, upload it to TSLab, and test it** — the full cycle from source code to running backtest.

For pure indicator authoring (choosing interfaces, writing handler code), prefer `$tslab-indicator-authoring`.
For agent management after the handler is working, prefer `$tslab-api-agents`.

## TSLab 3.0 API Quirks (critical)

These differ from TSLab 2.x and cause compilation/runtime errors if not followed:

1. **`IExternalScript` is NOT a handler interface** in 3.0. Use `IStreamHandler` + `IContextUses` for trading scripts.
2. **`ISecurity` has `ClosePrices`/`HighPrices`/`LowPrices`** (IList\<double\>), NOT `Close`/`High`/`Low`.
3. **`ISecurity.Positions`** (IPositionsList), NOT `Position`.
4. **`IContext` has `Runtime.Securities`**, NOT `ctx.Securities`.
5. **`IPosition.EntryPrice`** (property), NOT `GetOpenPrice(barNum)`.
6. **`IPosition.CloseAtMarket(barNum, signalName)`** — requires 2+ args.
7. **`IPositionsList.BuyAtMarket(barNum, shares, signalName)`** — requires 3 args.
8. **`Series.TrueRange(IDataBar[])`** — takes bars, NOT separate H/L/C arrays.
9. **`HandlerParameter` constructor**: `HandlerParameter(bool isShown, string def)` — Min/Max/Step are properties, not constructor args.
10. **Handler registered as `ConverterItem`** in block system, NOT `ExternalScriptItem`.

## Workflow

### Step 1: Compile

```powershell
# Prerequisites: .NET SDK 10.x, TSLab 3.0 DLLs at C:\Program Files\TSLab\TSLab 3.0\
dotnet build -c Release
```

csproj must reference:
- `TSLab.Script.dll`
- `TSLab.Script.Handlers.dll`
- `TSLab.DataSource.dll`
- `TSLab.Utility.dll`

All with `<Private>false</Private>`.

### Step 2: Upload DLL

```powershell
# Using curl (PowerShell Invoke-RestMethod often times out on multipart)
curl.exe -s -X POST "http://localhost:5000/api/indicator-dlls/<HandlerName>" `
  -F "file=@path\to\bin\Release\net10.0\Handler.dll" --max-time 180
```

Or replace existing:
```powershell
curl.exe -s -X POST "http://localhost:5000/api/indicator-dlls/<HandlerName>" `
  -F "file=@path\to\bin\Release\net10.0\Handler.dll" --max-time 180
```

Verify: `GET /api/handlers/<HandlerName>`

### Step 3: Create Test Script

```powershell
# 1. Create blank script
POST /api/script-manager/scripts  { "name": "Test_<Handler>" }

# 2. Set instrument source
POST /api/scripts/{name}/instrument-source  { "dataSourceName": "...", "securityId": "...", "interval": "60" }

# 3. Add ConverterItem block + connect + set params
POST /api/scripts/{name}/ops  {
  "ops": [
    { "op": "AddBlock", "blockId": "Ext", "blockType": "ConverterItem",
      "typeName": "<HandlerName>", "handlerTypeName": "<FullTypeName>" },
    { "op": "Connect", "fromBlockId": "Src", "fromPort": "Out",
      "toBlockId": "Ext", "toInputName": "Input0" },
    { "op": "SetParam", "blockId": "Ext", "paramName": "PARAM", "value": "VALUE" }
  ]
}
```

### Step 4: Lifecycle

```powershell
POST /api/scripts/{name}/validate
POST /api/scripts/{name}/build       # may timeout on heavy instruments
POST /api/scripts/{name}/load
POST /api/scripts/{name}/run
GET  /api/scripts/{name}/metrics-summary
```

If build times out: restart TSLab, re-upload DLL, retry.

### Step 5: Batch (optional)

For multiple instruments, create scripts in a loop:
```powershell
foreach ($ticker in $tickers) {
    # create → source → ops → validate → build → load → run → metrics
}
```

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `CS1061: IContext не содержит Securities` | TSLab 2.x API | Use `ctx.Runtime.Securities` |
| `CS7036: Missing arg for sec` | IExternalScript used | Switch to IStreamHandler |
| `HandlerParameter not found` | Wrong attribute syntax | Use `HandlerParameter(true, "default")` |
| Build timeout | Heavy instrument data | Restart TSLab, retry |
| `isEditing=true` blocks ops | Script stuck in editor | Restart TSLab |
| Memory spike to 8GB | Many sequential builds | Restart TSLab at 128MB |

## Example: Complete Handler Template

```csharp
using TSLab.Script;
using TSLab.Script.Handlers;
using TSLab.Script.Helpers;
using TSLab.Utils;

[HandlerCategory(HandlerCategories.Indicators)]
[Description("My Handler")]
[InputsCount(1)]
[Input(0, TemplateTypes.SECURITY, false, "Security")]
[OutputType(TemplateTypes.DOUBLE)]
public class MyHandler : IStreamHandler, IContextUses
{
    public IContext Context { get; set; }

    [HandlerParameter(true, "14", Min = "5", Max = "50", Step = "1")]
    public int Period { get; set; } = 14;

    public IList<double> Execute(ISecurity sec)
    {
        var close = sec.ClosePrices;
        var result = Context.GetArray<double>(close.Count);
        // ... strategy logic ...
        return result;
    }
}
```
