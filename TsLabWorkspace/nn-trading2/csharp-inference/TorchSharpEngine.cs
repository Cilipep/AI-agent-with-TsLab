using TorchSharp;
using static TorchSharp.torch;
using Newtonsoft.Json;

namespace NNInference;

/// <summary>
/// TorchSharp движок: загружает веса из NumPy .npy файлов.
/// Формат экспорта: scripts/export_torchsharp.py
/// </summary>
class TorchSharpEngine : INNInferenceEngine
{
    private readonly int _windowSize;
    private readonly int _inputSize;
    private readonly int _hiddenSize;
    private readonly int _numLayers;

    // Веса LSTM (каждый слой)
    private readonly Tensor[] _Wi, _Wh, _bi, _bh;
    // Веса head
    private readonly Tensor _W1, _b1, _W2, _b2;

    public TorchSharpEngine(string modelDir, ModelMetadata meta)
    {
        _windowSize = meta.SequenceLength;
        _inputSize = meta.InputSize;
        _hiddenSize = meta.HiddenSize;
        _numLayers = meta.NumLayers;

        torch.set_default_device("cpu");

        // Путь к папке с весами
        var weightsDir = Path.Combine(modelDir, "torchsharp");
        if (!Directory.Exists(weightsDir))
            throw new DirectoryNotFoundException($"Папка с весами не найдена: {weightsDir}");

        Console.WriteLine($"[TorchSharp] Загрузка весов из {weightsDir}/");

        // Загрузка весов LSTM
        _Wi = new Tensor[_numLayers];
        _Wh = new Tensor[_numLayers];
        _bi = new Tensor[_numLayers];
        _bh = new Tensor[_numLayers];

        for (int i = 0; i < _numLayers; i++)
        {
            _Wi[i] = LoadNpy(Path.Combine(weightsDir, $"lstm_weight_ih_l{i}.npy"));
            _Wh[i] = LoadNpy(Path.Combine(weightsDir, $"lstm_weight_hh_l{i}.npy"));
            _bi[i] = LoadNpy(Path.Combine(weightsDir, $"lstm_bias_ih_l{i}.npy"));
            _bh[i] = LoadNpy(Path.Combine(weightsDir, $"lstm_bias_hh_l{i}.npy"));
            Console.WriteLine($"  Layer {i}: Wi={Shape(_Wi[i])}, Wh={Shape(_Wh[i])}");
        }

        // Загрузка весов head (fc в PyTorch)
        _W1 = LoadNpy(Path.Combine(weightsDir, "fc_0_weight.npy"));
        _b1 = LoadNpy(Path.Combine(weightsDir, "fc_0_bias.npy"));
        _W2 = LoadNpy(Path.Combine(weightsDir, "fc_3_weight.npy"));
        _b2 = LoadNpy(Path.Combine(weightsDir, "fc_3_bias.npy"));
        Console.WriteLine($"  FC Head: W1={Shape(_W1)}, W2={Shape(_W2)}");

        Console.WriteLine($"[TorchSharp] Модель готова: LSTM({_inputSize}→{_hiddenSize}×{_numLayers}) → Linear({_hiddenSize}→32) → ReLU → Linear(32→1)");
    }

    /// <summary>
    /// Загрузка .npy файла.
    /// </summary>
    private static Tensor LoadNpy(string path)
    {
        if (!File.Exists(path))
            throw new FileNotFoundException($"Веса не найдены: {path}");

        return LoadNpyManual(path);
    }

    /// <summary>
    /// Ручной парсинг NumPy .npy формата (v1.0, little-endian).
    /// </summary>
    private static Tensor LoadNpyManual(string path)
    {
        using var stream = File.OpenRead(path);
        using var reader = new BinaryReader(stream);

        // Магический заголовок: \x93NUMPY
        var magic = reader.ReadBytes(6);
        if (magic[0] != 0x93 || magic[1] != 'N' || magic[2] != 'U' ||
            magic[3] != 'M' || magic[4] != 'P' || magic[5] != 'Y')
            throw new InvalidDataException($"Не NumPy .npy файл: {path}");

        // Версия
        var major = reader.ReadByte(); // 1
        var minor = reader.ReadByte(); // 0

        // Длина заголовка
        int headerLen;
        if (major == 1)
            headerLen = reader.ReadUInt16();
        else
            headerLen = reader.ReadInt32();

        // Заголовок (ASCII)
        var headerBytes = reader.ReadBytes(headerLen);
        var header = System.Text.Encoding.ASCII.GetString(headerBytes);

        // Парсинг описания данных
        // Формат: {'descr': '<f4', 'fortran_order': False, 'shape': (64, 640), }
        var descrMatch = System.Text.RegularExpressions.Regex.Match(header, @"'descr':\s*'([^']+)'");
        var shapeMatch = System.Text.RegularExpressions.Regex.Match(header, @"'shape':\s*\(([^)]+)\)");

        if (!descrMatch.Success || !shapeMatch.Success)
            throw new InvalidDataException($"Не удалось распарсить заголовок .npy: {header}");

        var dtype = descrMatch.Groups[1].Value;
        var shapeStr = shapeMatch.Groups[1].Value.Trim();
        var shape = shapeStr.Split(',')
            .Where(s => !string.IsNullOrWhiteSpace(s))
            .Select(s => int.Parse(s.Trim()))
            .ToArray();

        // Чтение данных
        int elementSize = dtype switch
        {
            "<f4" => 4,
            "<f8" => 8,
            "<i4" => 4,
            "<i8" => 8,
            _ => throw new NotSupportedException($"dtype не поддерживается: {dtype}")
        };

        int totalElements = 1;
        foreach (var dim in shape) totalElements *= dim;

        var data = new float[totalElements];
        for (int i = 0; i < totalElements; i++)
        {
            data[i] = dtype switch
            {
                "<f4" => reader.ReadSingle(),
                "<f8" => (float)reader.ReadDouble(),
                "<i4" => reader.ReadInt32(),
                "<i8" => reader.ReadInt64(),
                _ => 0
            };
        }

        return torch.tensor(data, dtype: ScalarType.Float32).reshape(shape.Select(s => (long)s).ToArray());
    }

    private static string Shape(Tensor t) => string.Join("×", t.shape);

    public float Predict(float[] flatInput)
    {
        using var scope = NewDisposeScope();

        // Reshape input: (1, window, features)
        var input = torch.tensor(flatInput, dtype: ScalarType.Float32)
            .reshape(new long[] { 1, _windowSize, _inputSize });

        // LSTM forward по слоям
        var h = torch.zeros(new long[] { _numLayers, 1, _hiddenSize }, dtype: ScalarType.Float32);
        var c = torch.zeros(new long[] { _numLayers, 1, _hiddenSize }, dtype: ScalarType.Float32);

        for (int t = 0; t < _windowSize; t++)
        {
            var xT = input[0, t, ..];

            for (int layer = 0; layer < _numLayers; layer++)
            {
                var xL = layer == 0 ? xT : h[layer - 1, 0, ..];

                // Gates: i, f, g, o
                var gates = torch.mm(xL.reshape(1, -1), _Wi[layer].T) + _bi[layer]
                          + torch.mm(h[layer], _Wh[layer].T) + _bh[layer];

                var iGate = torch.sigmoid(gates[0, new Range(0, _hiddenSize)]);
                var fGate = torch.sigmoid(gates[0, new Range(_hiddenSize, _hiddenSize * 2)]);
                var gGate = torch.tanh(gates[0, new Range(_hiddenSize * 2, _hiddenSize * 3)]);
                var oGate = torch.sigmoid(gates[0, new Range(_hiddenSize * 3, _hiddenSize * 4)]);

                c[layer] = fGate * c[layer] + iGate * gGate;
                h[layer] = oGate * torch.tanh(c[layer]);
            }
        }

        // Head: Linear(32) → ReLU → Dropout → Linear(1)
        var lastHidden = h[_numLayers - 1];
        var x1 = torch.mm(lastHidden, _W1.T) + _b1;
        var x1Relu = torch.clamp(x1, min: 0); // ReLU
        var logits = torch.mm(x1Relu, _W2.T) + _b2;

        var value = logits.item<float>();
        return Sigmoid(value);
    }

    private static float Sigmoid(float x) => 1.0f / (1.0f + (float)Math.Exp(-x));
}
