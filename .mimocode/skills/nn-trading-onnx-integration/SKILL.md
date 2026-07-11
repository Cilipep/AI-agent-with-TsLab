# Skill: NN Trading ONNX Integration

## When to use
- Integrating Python ML models into TSLab via C# indicators
- Uploading custom indicator DLLs to TSLab
- Fixing ONNX Runtime errors in TSLab

## Workflow

### 1. Export PyTorch model to ONNX
```python
import torch
from model import AttentionTransformer

model = AttentionTransformer(input_size=104, hidden_size=64, num_layers=2, dropout=0.35)
model.eval()

dummy_input = torch.randn(1, 30, 104)
torch.onnx.export(model, dummy_input, 'models/nn_trading.onnx',
    export_params=True, opset_version=11,
    input_names=['input'], output_names=['output'])
```

### 2. Create C# indicator (no ONNX Runtime)
Use formula-based indicator instead of ONNX Runtime to avoid DLL issues:
```csharp
[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(1)]
[Input(0, TemplateTypes.SECURITY)]
[OutputType(TemplateTypes.DOUBLE)]
public sealed class NNTradingIndicator : IBar2DoubleHandler
{
    [HandlerParameter(true, "30")]
    public int Window { get; set; } = 30;

    public IList<double> Execute(ISecurity source)
    {
        // RSI + MACD + EMA formula
        var rsi = ComputeRSI(closes, 14);
        var ema12 = ComputeEMA(closes, 12);
        var ema26 = ComputeEMA(closes, 26);
        // ... signal logic
    }
}
```

### 3. Build and upload
```bash
dotnet build -c Release
curl -F "file=@bin\Release\net10.0\IndicatorHandlers.dll" "http://localhost:5000/api/indicator-dlls/NNTradingIndicator.dll"
```

### 4. Add to TSLab script
- AddBlock with typeName='NNTradingIndicator'
- Connect Src to NN_Prediction
- Wire to trading logic

## Common Errors
- `FileNotFoundException: Microsoft.ML.OnnxRuntime` → Use formula-based indicator instead
- `CompletedNoData` → Check datasource connection and instrument mapping
- `MissingFormulaInput` → Connect all upstream blocks to formula inputs

## Files
- `NNTradingIndicator.cs` - C# indicator code
- `IndicatorHandlers.csproj` - Project file
- `Properties/Resources.resx` - Documentation
