"""
Экспорт LSTM модели в ONNX формат
"""
import torch
import numpy as np
import os
import json


def export_to_onnx(model_path, onnx_path):
    """Экспорт модели в ONNX"""
    checkpoint = torch.load(model_path, map_location='cpu', weights_only=True)

    # Восстановление модели
    from train_lstm import LSTMModel
    model = LSTMModel(
        input_size=checkpoint['input_size'],
        hidden_size=checkpoint['hidden_size'],
        num_layers=checkpoint['num_layers'],
        output_size=1
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    # Тестовый вход
    sequence_length = checkpoint['sequence_length']
    dummy_input = torch.randn(1, sequence_length, checkpoint['input_size'])

    # Экспорт
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output']
    )

    print(f"Модель экспортирована в ONNX: {onnx_path}")

    # Сохранение метаданных
    metadata = {
        'input_size': checkpoint['input_size'],
        'hidden_size': checkpoint['hidden_size'],
        'num_layers': checkpoint['num_layers'],
        'sequence_length': sequence_length,
        'features': ['close', 'volume', 'rsi', 'macd', 'macd_signal',
                     'bb_width', 'ema_9', 'ema_21', 'volume_ratio', 'volatility']
    }

    metadata_path = onnx_path.replace('.onnx', '_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Метаданные сохранены: {metadata_path}")

    return onnx_path, metadata_path


def main():
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    model_path = os.path.join(models_dir, 'lstm_model.pth')
    onnx_path = os.path.join(models_dir, 'lstm_model.onnx')

    if not os.path.exists(model_path):
        print(f"Модель не найдена: {model_path}")
        return

    export_to_onnx(model_path, onnx_path)
    print("\nЭкспорт завершен!")


if __name__ == '__main__':
    main()
