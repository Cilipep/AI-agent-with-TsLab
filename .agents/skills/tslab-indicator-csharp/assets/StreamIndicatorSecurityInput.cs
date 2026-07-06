using System;
using System.Collections.Generic;
using TSLab.Script;
using TSLab.Script.Handlers;

[HandlerCategory(HandlerCategories.Indicators)]
[InputsCount(1)]
[Input(0, TemplateTypes.SECURITY)]
[OutputType(TemplateTypes.DOUBLE)]
// Use this scaffold when the formula needs candles, OHLCV, volume, or bar metadata
// for one instrument. ISecurity exposes Bars, ClosePrices, HighPrices, LowPrices,
// OpenPrices, and Volumes, so the script graph only needs one SECURITY input.
// Put display text/docs into Properties/Resources.resx; use .en/.ru
// resource keys for bilingual docs. Do not add non-contract
// Description/DisplayName/ResourceKey attributes.
public sealed class __CLASS_NAME__ : IBar2DoubleHandler
{
    [HandlerParameter(true, "100", Min = "2", Step = "1")]
    public int Period { get; set; } = 100;

    public IList<double> Execute(ISecurity source)
    {
        if (source == null || source.Bars == null || source.Bars.Count == 0)
            return Array.Empty<double>();

        var result = new double[source.Bars.Count];
        for (var i = 0; i < result.Length; i++)
        {
            // Replace this with the requested candle/volume formula.
            result[i] = source.ClosePrices[i];
        }

        return result;
    }
}
