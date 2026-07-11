"""Export trained model to ONNX format for TSLab integration."""
import os
import torch
from model import AttentionTransformer

# Create model with correct input size (40 features from auto-select)
model = AttentionTransformer(input_size=40, hidden_size=64, num_layers=2, dropout=0.35)
model.eval()

# Dummy input: batch=1, window=30, features=40
dummy = torch.randn(1, 30, 40)

# Export to ONNX
output_path = "models/nn_trading_v2.onnx"
torch.onnx.export(
    model, dummy, output_path,
    export_params=True,
    opset_version=11,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"}
    }
)

size = os.path.getsize(output_path)
print(f"ONNX model exported: {output_path}")
print(f"Size: {size:,} bytes ({size/1024:.1f} KB)")
print(f"Input: [batch, 30, 40] (window=30, features=40)")
print(f"Output: [batch, 1] (prediction score 0-1)")
