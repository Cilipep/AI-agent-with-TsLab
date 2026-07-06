# Handlers Reference: ClusterAnalysis

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## AlignedSecurityHandler

- Display name: Aligned instrument
- typeName: `AlignedSecurityHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `TimeFrame` (`int`), default=`1`, range=`1`..`365` step `1`, shown=`True`, optimizable=`True`, help="Timeframe (integer value in units of parameter 'Timeframe units')"
- `TimeFrameUnit` (`TimeFrameUnit`), title="Timeframe units", default=`Hour`, shown=`True`, optimizable=`True`, help="Timeframe units (second, minute, hour, day)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AlignedSecurityHandler1", "typeName": "AlignedSecurityHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## AllTimeTradeStatisticsHandler

- Display name: All Time Trade Statistics
- typeName: `AllTimeTradeStatisticsHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `TRADE_STATISTICS` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `CombinePricesCount` (`int`), title="Combine price steps", default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`, help="How many price steps should be grouped together."
- `Kind` (`TradeStatisticsKind`), default=`TradesCount`, shown=`True`, optimizable=`True`, help="Kind of a trade statistics (trades count, trade volume, buy count, sell count, buy and sell difference, relative buy and sell difference)."
- `WidthPercent` (`Double`), title="Width, %", default=`10`, range=`1`..`100` step `1`, shown=`True`, optimizable=`True`, help="A width of a hystogram relative to a width of a chart pane."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AllTimeTradeStatisticsHandler1", "typeName": "AllTimeTradeStatisticsHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## BidAskMarketPosition

- Display name: Buy/Sell cluster(view only)
- typeName: `BidAskMarketPosition`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `FOOTPRINT` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `ColorPower` (`Double`), default=`3`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`
- `CombineSteps` (`Double`), default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BidAskMarketPosition1", "typeName": "BidAskMarketPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## DeltaMarketPosition

- Display name: Delta cluster(view only)
- typeName: `DeltaMarketPosition`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `FOOTPRINT` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `ColorPower` (`Double`), default=`3`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`
- `CombineSteps` (`Double`), default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DeltaMarketPosition1", "typeName": "DeltaMarketPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## InteractiveSeriesHandler

- Display name: InteractiveSeriesHandler
- typeName: `InteractiveSeriesHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "InteractiveSeriesHandler1", "typeName": "InteractiveSeriesHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## LastContractsTradeStatisticsHandler

- Display name: Last Contracts Trade Statistics
- typeName: `LastContractsTradeStatisticsHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `LAST_CONTRACTS_TRADE_STATISTICS` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `CombinePricesCount` (`int`), title="Combine price steps", default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`, help="How many price steps should be grouped together."
- `ContractsCount` (`int`), title="Contracts count", default=`10000`, range=`10000`..`1000000` step `10000`, shown=`True`, optimizable=`True`, help="A parameter to set contracts count to be used for trade statistics."
- `Kind` (`TradeStatisticsKind`), default=`TradesCount`, shown=`True`, optimizable=`True`, help="Kind of a trade statistics (trades count, trade volume, buy count, sell count, buy and sell difference, relative buy and sell difference)."
- `WidthPercent` (`Double`), title="Width, %", default=`100`, range=`1`..`100` step `1`, shown=`True`, optimizable=`True`, help="A width of a hystogram relative to a width of a chart pane."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastContractsTradeStatisticsHandler1", "typeName": "LastContractsTradeStatisticsHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## LastTradeStatisticsHandler

- Display name: Last Trade Statistics
- typeName: `LastTradeStatisticsHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `TRADE_STATISTICS` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `CombinePricesCount` (`int`), title="Combine price steps", default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`, help="How many price steps should be grouped together."
- `Kind` (`TradeStatisticsKind`), default=`TradesCount`, shown=`True`, optimizable=`True`, help="Kind of a trade statistics (trades count, trade volume, buy count, sell count, buy and sell difference, relative buy and sell difference)."
- `TimeFrame` (`int`), default=`1`, range=`1`..`365` step `1`, shown=`True`, optimizable=`True`, help="Timeframe (integer value in units of parameter 'Timeframe units')"
- `TimeFrameKind` (`TimeFrameKind`), default=`FromMidnightToNow`, shown=`True`, optimizable=`True`
- `TimeFrameShift` (`int`), default=`0`, range=`0`..`365` step `1`, shown=`True`, optimizable=`True`
- `TimeFrameShiftUnit` (`TimeFrameUnit`), default=`Hour`, shown=`True`, optimizable=`True`
- `TimeFrameUnit` (`TimeFrameUnit`), title="Timeframe units", default=`Hour`, shown=`True`, optimizable=`True`, help="Timeframe units (second, minute, hour, day)"
- `WidthPercent` (`Double`), title="Width, %", default=`100`, range=`1`..`100` step `1`, shown=`True`, optimizable=`True`, help="A width of a hystogram relative to a width of a chart pane."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastTradeStatisticsHandler1", "typeName": "LastTradeStatisticsHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## SpecifiedQuantityPriceAtTradeHandler

- Display name: Specified quantity price at trade
- typeName: `SpecifiedQuantityPriceAtTradeHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Direction` (`SpecifiedTradeDirection`), default=`Any`, shown=`True`, optimizable=`True`, help="Direction"
- `Quantity` (`Double`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`, help="Quantity"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SpecifiedQuantityPriceAtTradeHandler1", "typeName": "SpecifiedQuantityPriceAtTradeHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsBarsCountHandler

- Display name: Trade Statistics Strings Count
- typeName: `TradeStatisticsBarsCountHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `MaxBarPct` (`Double`), default=`100`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `MinBarPct` (`Double`), default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `TrimComparisonMode` (`ComparisonMode`), title="Comparison operator", default=`GreaterOrEqual`, shown=`True`, optimizable=`True`, help="Comparison operator for trimming (greater, greater or equal, less, less or equal, equal, not equal)."
- `TrimValue` (`Double`), title="Trim value", default=`0`, range=`-999999999999999`..`999999999999999` step `1`, shown=`True`, optimizable=`True`, help="Trim value."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsBarsCountHandler1", "typeName": "TradeStatisticsBarsCountHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsBarsSumHandler

- Display name: Trade Statistics Strings Sum
- typeName: `TradeStatisticsBarsSumHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `MaxBarPct` (`Double`), default=`100`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `MinBarPct` (`Double`), default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `TrimComparisonMode` (`ComparisonMode`), title="Comparison operator", default=`GreaterOrEqual`, shown=`True`, optimizable=`True`, help="Comparison operator for trimming (greater, greater or equal, less, less or equal, equal, not equal)."
- `TrimValue` (`Double`), title="Trim value", default=`0`, range=`-999999999999999`..`999999999999999` step `1`, shown=`True`, optimizable=`True`, help="Trim value."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsBarsSumHandler1", "typeName": "TradeStatisticsBarsSumHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsCombineHandler

- Display name: Stacked Trading Statistics
- typeName: `TradeStatisticsCombineHandler`
- Namespace: `TSLab.Script.Handlers.ClusterAnalysis`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `TRADE_STATISTICS` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsCombineHandler1", "typeName": "TradeStatisticsCombineHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsExtendedBarsCountHandler

- Display name: Trade Statistics Extended Strings Count 1
- typeName: `TradeStatisticsExtendedBarsCountHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `TrimAskQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimBidQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimComparisonMode` (`ComparisonMode`), title="Comparison operator", default=`GreaterOrEqual`, shown=`True`, optimizable=`True`, help="Comparison operator for trimming (greater, greater or equal, less, less or equal, equal, not equal)."
- `TrimDeltaAskBidQuantity` (`Double`), default=`0`, range=`-999999999999999`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercent` (`Double`), default=`0`, range=`-100`..`100` step `1`, shown=`True`, optimizable=`True`
- `TrimTradesCount` (`int`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`
- `UseTrimAskQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimDeltaAskBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimRelativeDeltaAskBidQuantityPercent` (`bool`), default=`false`, shown=`True`, optimizable=`False`
- `UseTrimTradesCount` (`bool`), shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsExtendedBarsCountHandler1", "typeName": "TradeStatisticsExtendedBarsCountHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsExtendedBarsCountHandler2

- Display name: Trade Statistics Extended Strings Count 2
- typeName: `TradeStatisticsExtendedBarsCountHandler2`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `TrimAskQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimAskQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimBidQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimBidQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimDeltaAskBidQuantity` (`Double`), default=`0`, range=`-999999999999999`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimDeltaAskBidQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercent` (`Double`), default=`0`, range=`-100`..`100` step `1`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercentComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimTradesCount` (`int`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`
- `TrimTradesCountComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `UseTrimAskQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimDeltaAskBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimRelativeDeltaAskBidQuantityPercent` (`bool`), default=`false`, shown=`True`, optimizable=`False`
- `UseTrimTradesCount` (`bool`), shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsExtendedBarsCountHandler21", "typeName": "TradeStatisticsExtendedBarsCountHandler2", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsExtendedBarsSumHandler

- Display name: Trade Statistics Extended Strings Sum 1
- typeName: `TradeStatisticsExtendedBarsSumHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `Kind` (`TradeStatisticsKind`), default=`TradesCount`, shown=`True`, optimizable=`True`, help="Kind of a trade statistics (trades count, trade volume, buy count, sell count, buy and sell difference, relative buy and sell difference)."
- `TrimAskQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimBidQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimComparisonMode` (`ComparisonMode`), title="Comparison operator", default=`GreaterOrEqual`, shown=`True`, optimizable=`True`, help="Comparison operator for trimming (greater, greater or equal, less, less or equal, equal, not equal)."
- `TrimDeltaAskBidQuantity` (`Double`), default=`0`, range=`-999999999999999`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercent` (`Double`), default=`0`, range=`-100`..`100` step `1`, shown=`True`, optimizable=`True`
- `TrimTradesCount` (`int`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`
- `UseTrimAskQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimDeltaAskBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimRelativeDeltaAskBidQuantityPercent` (`bool`), default=`false`, shown=`True`, optimizable=`False`
- `UseTrimTradesCount` (`bool`), shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsExtendedBarsSumHandler1", "typeName": "TradeStatisticsExtendedBarsSumHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsExtendedBarsSumHandler2

- Display name: Trade Statistics Extended Strings Sum 2
- typeName: `TradeStatisticsExtendedBarsSumHandler2`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `Kind` (`TradeStatisticsKind`), default=`TradesCount`, shown=`True`, optimizable=`True`, help="Kind of a trade statistics (trades count, trade volume, buy count, sell count, buy and sell difference, relative buy and sell difference)."
- `TrimAskQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimAskQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimBidQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimBidQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimDeltaAskBidQuantity` (`Double`), default=`0`, range=`-999999999999999`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimDeltaAskBidQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercent` (`Double`), default=`0`, range=`-100`..`100` step `1`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercentComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimTradesCount` (`int`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`
- `TrimTradesCountComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `UseTrimAskQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimDeltaAskBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimRelativeDeltaAskBidQuantityPercent` (`bool`), default=`false`, shown=`True`, optimizable=`False`
- `UseTrimTradesCount` (`bool`), shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsExtendedBarsSumHandler21", "typeName": "TradeStatisticsExtendedBarsSumHandler2", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsExtendedExtremumPriceHandler

- Display name: Trade Statistics Extended Extremum Price 1
- typeName: `TradeStatisticsExtendedExtremumPriceHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `MaxBarPct` (`Double`), default=`100`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `MinBarPct` (`Double`), default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `PriceMode` (`ExtremumPriceMode`), title="Extremum kind", default=`Minimum`, shown=`True`, optimizable=`True`, help="Extremum kind (minimum, maximum)."
- `TrimAskQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimBidQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimDeltaAskBidQuantity` (`Double`), default=`0`, range=`-999999999999999`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercent` (`Double`), default=`0`, range=`-100`..`100` step `1`, shown=`True`, optimizable=`True`
- `TrimTradesCount` (`int`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`
- `UseTrimAskQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimDeltaAskBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimRelativeDeltaAskBidQuantityPercent` (`bool`), default=`false`, shown=`True`, optimizable=`False`
- `UseTrimTradesCount` (`bool`), shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsExtendedExtremumPriceHandler1", "typeName": "TradeStatisticsExtendedExtremumPriceHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsExtendedExtremumPriceHandler2

- Display name: Trade Statistics Extended Extremum Price 2
- typeName: `TradeStatisticsExtendedExtremumPriceHandler2`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `MaxBarPct` (`Double`), default=`100`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `MinBarPct` (`Double`), default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `PriceMode` (`ExtremumPriceMode`), title="Extremum kind", default=`Minimum`, shown=`True`, optimizable=`True`, help="Extremum kind (minimum, maximum)."
- `TrimAskQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimAskQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimBidQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimBidQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimDeltaAskBidQuantity` (`Double`), default=`0`, range=`-999999999999999`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimDeltaAskBidQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimQuantity` (`Double`), default=`0`, range=`0`..`999999999999999` step `1`, shown=`True`, optimizable=`True`
- `TrimQuantityComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercent` (`Double`), default=`0`, range=`-100`..`100` step `1`, shown=`True`, optimizable=`True`
- `TrimRelativeDeltaAskBidQuantityPercentComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `TrimTradesCount` (`int`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`
- `TrimTradesCountComparisonMode` (`ComparisonMode`), default=`GreaterOrEqual`, shown=`True`, optimizable=`True`
- `UseTrimAskQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimDeltaAskBidQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimQuantity` (`bool`), shown=`True`, optimizable=`False`
- `UseTrimRelativeDeltaAskBidQuantityPercent` (`bool`), default=`false`, shown=`True`, optimizable=`False`
- `UseTrimTradesCount` (`bool`), shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsExtendedExtremumPriceHandler21", "typeName": "TradeStatisticsExtendedExtremumPriceHandler2", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsExtremumPriceHandler

- Display name: Trade Statistics Extremum Price (POC)
- typeName: `TradeStatisticsExtremumPriceHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `MaxBarPct` (`Double`), default=`100`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `MinBarPct` (`Double`), default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `PriceMode` (`ExtremumPriceMode`), title="Extremum kind", default=`Minimum`, shown=`True`, optimizable=`True`, help="Extremum kind (minimum, maximum)."
- `TrimValue` (`Double`), title="Trim value", default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`, help="Trim value."
- `TrimValueMode` (`TrimValueMode`), title="Trim value mode", default=`None`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsExtremumPriceHandler1", "typeName": "TradeStatisticsExtremumPriceHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsExtremumValueHandler

- Display name: Trade Statistics Extremum Value
- typeName: `TradeStatisticsExtremumValueHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `MaxBarPct` (`Double`), default=`100`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`
- `MinBarPct` (`Double`), default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsExtremumValueHandler1", "typeName": "TradeStatisticsExtremumValueHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsHandler

- Display name: Trade Statistics
- typeName: `TradeStatisticsHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `TRADE_STATISTICS` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `CombinePricesCount` (`int`), title="Combine price steps", default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`, help="How many price steps should be grouped together."
- `Kind` (`TradeStatisticsKind`), default=`TradesCount`, shown=`True`, optimizable=`True`, help="Kind of a trade statistics (trades count, trade volume, buy count, sell count, buy and sell difference, relative buy and sell difference)."
- `StartTime` (`DateTime`), title="Start time", default=`0001-01-01`, shown=`True`, optimizable=`True`, help="Start building a profile."
- `TimeFrame` (`int`), default=`1`, range=`1`..`365` step `1`, shown=`True`, optimizable=`True`, help="Timeframe (integer value in units of parameter 'Timeframe units')"
- `TimeFrameKind` (`TimeFrameKind`), title="Time frame kind", default=`FromMidnightToNow`, shown=`True`, optimizable=`True`, help="Time frame kind (from now to past, from midnight to now)."
- `TimeFrameUnit` (`TimeFrameUnit`), title="Timeframe units", default=`Hour`, shown=`True`, optimizable=`True`, help="Timeframe units (second, minute, hour, day)"
- `TopTimeFrame` (`int`), default=`20`, range=`1`..`2000000` step `1`, shown=`True`, optimizable=`True`
- `TopTimeFrameUnit` (`TimeFrameUnit`), default=`Day`, shown=`True`, optimizable=`True`
- `UseTopTimeFrame` (`bool`), default=`false`, shown=`True`, optimizable=`False`
- `WidthPercent` (`Double`), title="Width, %", default=`100`, range=`1`..`100` step `1`, shown=`True`, optimizable=`True`, help="A width of a hystogram relative to a width of a chart pane."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsHandler1", "typeName": "TradeStatisticsHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsLowerEdgeHandler

- Display name: Trade Statistics Lower Level (VAL)
- typeName: `TradeStatisticsLowerEdgeHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `TrimLevelPercent` (`Double`), title="Trim level, %", default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`, help="Trim level (as percents)."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsLowerEdgeHandler1", "typeName": "TradeStatisticsLowerEdgeHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## TradeStatisticsPriceValueHandler

- Display name: Trade Statistics Price Value
- typeName: `TradeStatisticsPriceValueHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsPriceValueHandler1", "typeName": "TradeStatisticsPriceValueHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## TradeStatisticsUpperEdgeHandler

- Display name: Trade Statistics Upper Level (VAH)
- typeName: `TradeStatisticsUpperEdgeHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `Input0` accepts `TRADE_STATISTICS, LAST_CONTRACTS_TRADE_STATISTICS` (required: `True`, stream-only: `True`)

### Parameters
- `TrimLevelPercent` (`Double`), title="Trim level, %", default=`0`, range=`0`..`100` step `1`, shown=`True`, optimizable=`True`, help="Trim level (as percents)."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TradeStatisticsUpperEdgeHandler1", "typeName": "TradeStatisticsUpperEdgeHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## VolumeMarketPosition

- Display name: Volume cluster(view only)
- typeName: `VolumeMarketPosition`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ClusterAnalysis`
- Output: `FOOTPRINT` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No description. This block is visible only in the developer build.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `ColorPower` (`Double`), default=`3`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`
- `CombineSteps` (`Double`), default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "VolumeMarketPosition1", "typeName": "VolumeMarketPosition", "blockType": "ConverterItem"
    }
  ]
}
```

