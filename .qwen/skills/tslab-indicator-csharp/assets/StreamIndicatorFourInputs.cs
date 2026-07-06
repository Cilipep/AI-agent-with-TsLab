using System;
using System.Collections.Generic;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(4)]
[Input(0, TemplateTypes.DOUBLE, false, "High")]
[Input(1, TemplateTypes.DOUBLE, false, "Low")]
[Input(2, TemplateTypes.DOUBLE, false, "Close")]
[Input(3, TemplateTypes.DOUBLE, false, "Volume")]
[OutputType(TemplateTypes.DOUBLE)]
// Default mental model: one stream handler produces one plotted series.
// Use only runtime-confirmed attributes from /api/sdk/contracts/indicator:
// HandlerCategory, InputsCount, Input, OutputType, OutputsCount, HandlerParameter.
// Put display text/docs into Properties/Resources.resx; use .en/.ru
// resource keys for bilingual docs. Do not add non-contract
// Description/DisplayName/ResourceKey attributes.
public sealed class __CLASS_NAME__ : IHandler, IStreamHandler
{
    [HandlerParameter(true, "100", Min = "2", Step = "1")]
    public int Period { get; set; } = 100;

    [HandlerParameter(true, "2", Min = "0.1", Step = "0.1")]
    public double Multiplier { get; set; } = 2.0;

    public IList<double> Execute(IList<double> high, IList<double> low, IList<double> close, IList<double> volume)
    {
        if (high == null || low == null || close == null || volume == null)
            return Array.Empty<double>();

        var count = Math.Min(Math.Min(high.Count, low.Count), Math.Min(close.Count, volume.Count));
        if (count <= 0)
            return Array.Empty<double>();

        var result = new double[count];
        for (var i = 0; i < count; i++)
        {
            // Replace this with the requested OHLCV indicator formula.
            result[i] = close[i];
        }

        return result;
    }
}
