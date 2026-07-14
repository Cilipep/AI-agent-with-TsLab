"""
Конвертация PyTorch .pth → TorchSharp формат.

TorchSharp не может напрямую загрузить state_dict PyTorch из-за различий
в формате сериализации. Этот скрипт экспортирует веса в формате NumPy .npy,
который TorchSharp читает natивно.

Формат экспорта:
  - weights/{layer_name}.npy — веса каждого слоя
  - weights/metadata.json — архитектура модели

Использование:
  python export_torchsharp.py --input models/lstm_model.pth --output models/torchsharp/
"""
import os
import json
import argparse
import numpy as np
import torch
import torch.nn as nn


class LSTMModel(nn.Module):
    """Архитектура, совпадающая с model.py."""

    def __init__(self, input_size, hidden_size, num_layers, dropout=0.35):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
        )
        # Используем fc (как в оригинальной модели) вместо head
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def load_model(pth_path, input_size, hidden_size, num_layers):
    """Загрузка state_dict из .pth файла."""
    checkpoint = torch.load(pth_path, map_location="cpu", weights_only=True)

    # Поддержка разных форматов сохранения
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
        # Обновляем параметры из checkpoint если есть
        input_size = checkpoint.get("input_size", input_size)
        hidden_size = checkpoint.get("hidden_size", hidden_size)
        num_layers = checkpoint.get("num_layers", num_layers)
    elif isinstance(checkpoint, dict) and any("lstm" in k for k in checkpoint.keys()):
        state_dict = checkpoint
    else:
        raise ValueError(f"Неизвестный формат checkpoint: {list(checkpoint.keys()) if isinstance(checkpoint, dict) else type(checkpoint)}")

    model = LSTMModel(input_size, hidden_size, num_layers)
    model.load_state_dict(state_dict)
    model.eval()
    return model, input_size, hidden_size, num_layers


def export_weights(model, output_dir):
    """Экспорт весов в NumPy .npy формат."""
    os.makedirs(output_dir, exist_ok=True)

    state_dict = model.state_dict()
    exported = {}

    for name, tensor in state_dict.items():
        # Конвертация в NumPy и сохранение
        npy_name = name.replace(".", "_") + ".npy"
        npy_path = os.path.join(output_dir, npy_name)
        np.save(npy_path, tensor.detach().numpy())
        exported[name] = {
            "file": npy_name,
            "shape": list(tensor.shape),
            "dtype": str(tensor.dtype),
        }
        print(f"  {name:30s} → {npy_name:30s} [{', '.join(str(s) for s in tensor.shape)}]")

    return exported


def main():
    parser = argparse.ArgumentParser(description="Конвертация .pth → TorchSharp")
    parser.add_argument("--input", default="models/lstm_model.pth", help="Путь к .pth модели")
    parser.add_argument("--output", default="models/torchsharp", help="Директория для экспорта")
    parser.add_argument("--input-size", type=int, default=10, help="Размер входа")
    parser.add_argument("--hidden-size", type=int, default=64, help="Размер скрытого слоя")
    parser.add_argument("--num-layers", type=int, default=2, help="Количество слоёв LSTM")
    args = parser.parse_args()

    print(f"=== Конвертация PyTorch → TorchSharp ===\n")
    print(f"  Вход:    {args.input}")
    print(f"  Выход:   {args.output}/")
    print(f"  Архитектура: LSTM({args.input_size}→{args.hidden_size}×{args.num_layers}→1)\n")

    # Загрузка модели
    print("Загрузка .pth модели...")
    model, input_size, hidden_size, num_layers = load_model(args.input, args.input_size, args.hidden_size, args.num_layers)
    print(f"  Модель загружена: {sum(p.numel() for p in model.parameters())} параметров")
    print(f"  Архитектура: LSTM({input_size}→{hidden_size}×{num_layers}→1)\n")

    # Экспорт весов
    print("Экспорт весов в NumPy .npy:")
    weight_map = export_weights(model, args.output)

    # Сохранение метаданных
    metadata = {
        "architecture": "LSTMWithHead",
        "input_size": input_size,
        "hidden_size": hidden_size,
        "num_layers": num_layers,
        "dropout": 0.35,
        "source_file": os.path.basename(args.input),
        "weights": weight_map,
    }

    meta_path = os.path.join(args.output, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n  Метаданные: {meta_path}")
    print(f"\n=== Конвертация завершена ===")
    print(f"\nФайлы:")
    print(f"  {args.output}/")
    for name in weight_map:
        print(f"    {weight_map[name]['file']}")
    print(f"    metadata.json")


if __name__ == "__main__":
    main()
