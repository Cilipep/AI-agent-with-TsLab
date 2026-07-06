using System;
using System.Collections.Generic;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(3)]
[Input(0, TemplateTypes.DOUBLE, false, "Input1")]
[Input(1, TemplateTypes.DOUBLE, false, "Input2")]
[Input(2, TemplateTypes.DOUBLE, false, "Input3")]
[OutputType(TemplateTypes.DOUBLE)]
// Default mental model: one stream handler produces one plotted series.
// Put display text/docs into Properties/Resources.resx: <TypeName>.Name,
// <TypeName>.Description, <TypeName>.Formula, and <TypeName>.<ParamName>.Effect.
// For bilingual docs, fill the same keys with .en and .ru suffixes.
// Do not add non-contract Description/DisplayName/ResourceKey attributes.
public sealed class __CLASS_NAME__ : IHandler, IStreamHandler
{
    [HandlerParameter(true, "10", Min = "1", Step = "1")]
    public int Period { get; set; } = 10;

    [HandlerParameter(true, "3", Min = "0.1", Step = "0.1")]
    public double Multiplier { get; set; } = 3.0;

    public IList<double> Execute(IList<double> input1, IList<double> input2, IList<double> input3)
    {
        if (input1 == null || input2 == null || input3 == null)
            return Array.Empty<double>();

        var count = Math.Min(input1.Count, Math.Min(input2.Count, input3.Count));
        if (count <= 0)
            return Array.Empty<double>();

        var result = new double[count];
        for (var i = 0; i < count; i++)
        {
            // Replace this with the requested indicator formula.
            result[i] = input3[i];
        }

        return result;
    }
}
