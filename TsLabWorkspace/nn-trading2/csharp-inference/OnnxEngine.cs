using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;

namespace NNInference;

/// <summary>
/// Fallback движок: ONNX Runtime для .onnx моделей.
/// Используется если TorchSharp недоступен.
/// </summary>
class OnnxEngine : INNInferenceEngine
{
    private readonly InferenceSession _session;
    private readonly int _windowSize;
    private readonly int _inputSize;
    private readonly string _inputName;

    public OnnxEngine(string onnxPath, ModelMetadata meta)
    {
        _windowSize = meta.SequenceLength;
        _inputSize = meta.InputSize;

        _session = new InferenceSession(onnxPath);
        _inputName = _session.InputMetadata.Keys.First();

        Console.WriteLine($"[ONNX] Модель загружена: {onnxPath}");
        Console.WriteLine($"[ONNX] Input: {_inputName}, dims: {string.Join("x", _session.InputMetadata[_inputName].Dimensions)}");
    }

    public float Predict(float[] flatInput)
    {
        var inputTensor = new DenseTensor<float>(flatInput, new[] { 1, _windowSize, _inputSize });
        var inputs = new List<NamedOnnxValue>
        {
            NamedOnnxValue.CreateFromTensor(_inputName, inputTensor)
        };

        using var results = _session.Run(inputs);
        var output = results.First().AsTensor<float>().ToArray();
        return Sigmoid(output[0]);
    }

    private static float Sigmoid(float x) => 1.0f / (1.0f + (float)Math.Exp(-x));

    public void Dispose()
    {
        _session?.Dispose();
    }
}
