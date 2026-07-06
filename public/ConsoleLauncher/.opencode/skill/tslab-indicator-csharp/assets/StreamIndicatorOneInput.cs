using System;
using System.Collections.Generic;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(1)]
[Input(0, TemplateTypes.DOUBLE, false, "Source")]
[OutputType(TemplateTypes.DOUBLE)]
// Default mental model: one stream handler produces one plotted series.
// Put display text/docs into Properties/Resources.resx: <TypeName>.Name,
// <TypeName>.Description, <TypeName>.Formula, and <TypeName>.<ParamName>.Effect.
// For bilingual docs, fill the same keys with .en and .ru suffixes.
// Do not add non-contract Description/DisplayName/ResourceKey attributes.
public sealed class __CLASS_NAME__ : IHandler, IStreamHandler
{
    [HandlerParameter(true, "14", Min = "1", Step = "1")]
    public int Period { get; set; } = 14;

    public IList<double> Execute(IList<double> source)
    {
        if (source == null || source.Count <= 0)
            return Array.Empty<double>();

        var count = source.Count;
        var result = new double[count];
        for (var i = 0; i < count; i++)
        {
            // Replace this with the requested indicator formula.
            result[i] = source[i];
        }

        return result;
    }
}
