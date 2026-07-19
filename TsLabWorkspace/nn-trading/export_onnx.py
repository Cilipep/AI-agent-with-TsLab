"""Export PyTorch model to ONNX for TSLab integration."""
import torch
import numpy as np
from pathlib import Path


def export_to_onnx(model, config, input_size=None, output_path=None):
    """
    Export PyTorch model to ONNX format.
    
    Args:
        model: Trained PyTorch model
        config: Config object with model parameters
        input_size: Number of input features (auto-detected if None)
        output_path: Output ONNX file path (auto-generated if None)
    """
    if input_size is None:
        input_size = config.max_features
    
    if output_path is None:
        output_path = Path("models") / f"{config.model_type}_{config.hidden_size}.onnx"
    
    # Ensure output directory exists
    output_path.parent.mkdir(exist_ok=True)
    
    # Set model to eval mode
    model.eval()
    
    # Create dummy input
    batch_size = 1
    seq_len = config.window
    dummy_input = torch.randn(batch_size, seq_len, input_size)
    
    # Export to ONNX
    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size", 1: "sequence"},
            "output": {0: "batch_size", 1: "sequence"}
        },
        opset_version=14,
        do_constant_folding=True,
    )
    
    print(f"✓ Model exported to: {output_path}")
    
    return output_path


def test_onnx_export(model, config, input_size=None):
    """Test ONNX export by comparing PyTorch and ONNX outputs."""
    import onnx
    import onnxruntime
    
    if input_size is None:
        input_size = config.max_features
    
    model.eval()
    
    # Create test input
    batch_size = 1
    seq_len = config.window
    test_input = torch.randn(batch_size, seq_len, input_size)
    
    # Get PyTorch prediction
    with torch.no_grad():
        pytorch_output = model(test_input).numpy()
    
    # Export to ONNX
    output_path = Path("models") / "test_export.onnx"
    output_path.parent.mkdir(exist_ok=True)
    
    torch.onnx.export(
        model,
        test_input,
        str(output_path),
        input_names=["input"],
        output_names=["output"],
        opset_version=14,
        do_constant_folding=True,
    )
    
    # Load ONNX model
    onnx_model = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_model)
    
    # Run ONNX inference
    ort_session = onnxruntime.InferenceSession(str(output_path))
    ort_input_name = ort_session.get_inputs()[0].name
    ort_output_name = ort_session.get_outputs()[0].name
    
    ort_output = ort_session.run(
        [ort_output_name],
        {ort_input_name: test_input.numpy()}
    )[0]
    
    # Compare outputs
    diff = np.abs(pytorch_output - ort_output).max()
    print(f"  Max difference: {diff:.6f}")
    
    # Clean up
    output_path.unlink()
    
    return diff


def create_csharp_onnx_wrapper(model_path, output_path=None):
    """
    Create C# wrapper for ONNX model using Microsoft.ML.OnnxRuntime.
    
    Args:
        model_path: Path to ONNX model
        output_path: Output C# file path
    """
    if output_path is None:
        output_path = Path("tslab_scripts") / "NNTradingIndicator.cs"
    
    csharp_code = f'''// Auto-generated C# wrapper for ONNX model
// Generated: {str(Path(model_path).name)}

using System;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;

public class NNTradingIndicator
{{
    private InferenceSession _session;
    private bool _isInitialized = false;

    public void Initialize(string modelPath)
    {{
        _session = new InferenceSession(modelPath);
        _isInitialized = true;
    }}

    public double[] Predict(float[,] input)
    {{
        if (!_isInitialized)
            throw new InvalidOperationException("Model not initialized. Call Initialize() first.");

        // Convert input to tensor
        var inputTensor = new DenseTensor<float>(input, new[] {{ input.GetLength(0), input.GetLength(1) }});
        
        // Create inputs
        var inputs = new List<NamedOnnxValue>
        {{
            NamedOnnxValue.CreateFromTensor("input", inputTensor)
        }};

        // Run inference
        using var results = _session.Run(inputs);
        
        // Get output
        var output = results.First().AsTensor<double>();
        
        return output.ToArray();
    }}

    public void Dispose()
    {{
        _session?.Dispose();
        _isInitialized = false;
    }}
}}
'''
    
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(csharp_code)
    
    print(f"✓ C# wrapper created: {output_path}")
    
    return output_path


def main():
    """Main export workflow."""
    from config import Config
    from model import build_model
    
    print("=" * 60)
    print("PyTorch → ONNX Export for TSLab")
    print("=" * 60)
    
    # Config for export
    config = Config()
    config.model_type = "attention"
    config.hidden_size = 32
    config.num_layers = 1
    config.dropout = 0.2
    config.window = 30
    
    input_size = 30  # Number of features
    
    # Load or create model
    print("\n1. Loading model...")
    model = build_model(config, input_size)
    
    # Test export
    print("\n2. Testing ONNX export...")
    max_diff = test_onnx_export(model, config, input_size)
    
    if max_diff < 0.01:
        print("  ✓ ONNX export verified (max diff < 0.01)")
    else:
        print(f"  ⚠ Warning: Large difference detected: {max_diff:.6f}")
    
    # Export model
    print("\n3. Exporting model to ONNX...")
    output_path = Path("models") / "btc_attention_32.onnx"
    torch.onnx.export(
        model,
        torch.randn(1, config.window, input_size),
        str(output_path),
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size", 1: "sequence"},
            "output": {0: "batch_size"}
        },
        opset_version=14,
        do_constant_folding=True,
    )
    print(f"  ✓ Model saved: {output_path}")
    
    # Create C# wrapper
    print("\n4. Creating C# wrapper...")
    cs_path = Path("tslab_scripts") / "NNTradingIndicator.cs"
    create_csharp_onnx_wrapper(output_path, cs_path)
    
    print("\n" + "=" * 60)
    print("Export completed!")
    print("=" * 60)
    print(f"\nFiles created:")
    print(f"  • ONNX model: {output_path}")
    print(f"  • C# wrapper: {cs_path}")
    print(f"\nTo use in TSLab:")
    print(f"  1. Copy {output_path.name} to TSLab's data folder")
    print(f"  2. Use ExternalScriptItem with ONNX runtime")
    print(f"  3. Reference NNTradingIndicator.cs in TSLab script")


if __name__ == "__main__":
    main()
