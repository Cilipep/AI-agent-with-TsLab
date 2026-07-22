# Handlers Reference: Indicators

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## ADX

- Display name: ADX (Old)
- typeName: `ADX`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
ADX (legacy 2-input variant). Computes DX = 100 * abs(Input0 - Input1) / (Input0 + Input1) (0 if both are 0), then applies EMA(DX, Period). This is a generic "difference vs sum" smoother, not the full DI-based ADX pipeline.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ADX1", "typeName": "ADX", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## ADXFull

- Display name: ADX
- typeName: `ADXFull`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Average Directional Movement Index (ADX). Computes +DI and -DI from bar High/Low using EMA-smoothed directional movement normalized by EMA(TrueRange, Period); then DX = 100 * abs(+DI - -DI) / (+DI + -DI) and ADX = EMA(DX, Period). Used to estimate trend strength.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ADXFull1", "typeName": "ADXFull", "blockType": "ConverterItem"
    }
  ]
}
```

## AMA

- Display name: AMA
- typeName: `AMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Adaptive Moving Average (AMA, KAMA-style). Uses an efficiency ratio ER = abs(x[i]-x[i-Period]) / (epsilon + sum(abs(x[t]-x[t-1])) over Period). Then SSC = ER*0.60215 + 0.06452, and AMA = prev + SSC^2 * (x - prev). Not gap-tolerant.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AMA1", "typeName": "AMA", "blockType": "ConverterItem"
    }
  ]
}
```

## AroonDown

- Display name: Aroon-
- typeName: `AroonDown`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Aroon Down. Measures how recently a new low occurred within Period: AroonDown = 100 * (Period - barsSinceLowest) / Period, where barsSinceLowest is the distance from the current bar to the most recent lowest value in the lookback window.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AroonDown1", "typeName": "AroonDown", "blockType": "ConverterItem"
    }
  ]
}
```

## AroonUp

- Display name: Aroon+
- typeName: `AroonUp`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Aroon Up. Measures how recently a new high occurred within Period: AroonUp = 100 * (Period - barsSinceHighest) / Period, where barsSinceHighest is the distance from the current bar to the most recent highest value in the lookback window.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AroonUp1", "typeName": "AroonUp", "blockType": "ConverterItem"
    }
  ]
}
```

## AverageTrueRange

- Display name: ATR (Old)
- typeName: `AverageTrueRange`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Average True Range (ATR, Wilder-style smoothing). Uses TR per bar and Wilder smoothing: ATR[i] = (ATR[i-1]*(Period-1) + TR[i]) / Period; on early bars it uses the average of available TR samples.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AverageTrueRange1", "typeName": "AverageTrueRange", "blockType": "ConverterItem"
    }
  ]
}
```

## AverageTrueRangeNew

- Display name: ATR
- typeName: `AverageTrueRangeNew`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Average True Range (ATR, simple). Computes TR per bar and then applies an SMA over Period: ATR[i] = SMA(TR, Period)[i]. This differs from the Wilder-style smoothing used by AverageTrueRange (Old).

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AverageTrueRangeNew1", "typeName": "AverageTrueRangeNew", "blockType": "ConverterItem"
    }
  ]
}
```

## BarsCountForValuesSumHandler

- Display name: Number of bars for the sum of values
- typeName: `BarsCountForValuesSumHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Bars count for values sum. For each bar i, walks backward summing values[i] + values[i-1] + ... and returns the smallest bar count needed to reach ValuesSum (returns 0 if the threshold is never reached).

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `ValuesSum` (`Double`), title="Values sum", default=`1`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`, help="Indicator values sum"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BarsCountForValuesSumHandler1", "typeName": "BarsCountForValuesSumHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## BollingerBands1

- Display name: Bollinger Bands (+)
- typeName: `BollingerBands1`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Upper Bollinger Band. Computed as SMA(x, Period) + Coef * StDev(x, Period), where StDev is the rolling standard deviation around the same SMA base.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Coef` (`Double`), title="Width", default=`2`, range=`0.5`..`3` step `0.5`, shown=`True`, optimizable=`True`, help="Width of a Bollinger band"
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BollingerBands11", "typeName": "BollingerBands1", "blockType": "ConverterItem"
    }
  ]
}
```

## BollingerBands2

- Display name: Bollinger Bands (-)
- typeName: `BollingerBands2`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Lower Bollinger Band. Computed as SMA(x, Period) - Coef * StDev(x, Period), where StDev is the rolling standard deviation around the same SMA base.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Coef` (`Double`), title="Width", default=`2`, range=`0.5`..`3` step `0.5`, shown=`True`, optimizable=`True`, help="Width of a Bollinger band"
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BollingerBands21", "typeName": "BollingerBands2", "blockType": "ConverterItem"
    }
  ]
}
```

## CCI

- Display name: CCI (Old)
- typeName: `CCI`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Commodity Channel Index (CCI). Uses Typical Price TP=(H+L+C)/3 and SMA(TP,Period). CCI = (TP - SMA(TP)) / (0.015 * MAD), where MAD is the mean absolute deviation of TP around SMA over the lookback window.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CCI1", "typeName": "CCI", "blockType": "ConverterItem"
    }
  ]
}
```

## CCINew

- Display name: CCI
- typeName: `CCINew`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Commodity Channel Index (CCI, new). Same TP/SMA/MAD formula as CCI, but uses a per-bar MAD window that shrinks on early bars (effective window = min(Period, index)). This avoids unstable behavior on the first Period bars.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CCINew1", "typeName": "CCINew", "blockType": "ConverterItem"
    }
  ]
}
```

## CuttlerRSI

- Display name: Cutler's RSI
- typeName: `CuttlerRSI`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Cutler's RSI. Uses the same RSI formula as RSI, but smooths AvgUp/AvgDown with an SMA (not EMA): RSI = 100 - 100/(1 + AvgUp/AvgDown). Useful when you want a less reactive, SMA-based RSI variant.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CuttlerRSI1", "typeName": "CuttlerRSI", "blockType": "ConverterItem"
    }
  ]
}
```

## DEMA

- Display name: DEMA
- typeName: `DEMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Double Exponential Moving Average (DEMA). Computed as DEMA = 2*EMA1 - EMA2, where EMA1=EMA(x) and EMA2=EMA(EMA1). Designed to reduce lag compared to a single EMA.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DEMA1", "typeName": "DEMA", "blockType": "ConverterItem"
    }
  ]
}
```

## DIM

- Display name: -DI
- typeName: `DIM`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
-DI (Negative Directional Indicator). Computes -DM from bar High/Low and smooths it with EMA over Period; normalizes by EMA(TrueRange, Period): -DI = EMA(-DM,Period) / EMA(TR,Period). Values are ratios (not multiplied by 100 in this implementation).

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DIM1", "typeName": "DIM", "blockType": "ConverterItem"
    }
  ]
}
```

## DIP

- Display name: +DI
- typeName: `DIP`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
+DI (Positive Directional Indicator). Computes +DM from bar High/Low and smooths it with EMA over Period; normalizes by EMA(TrueRange, Period): +DI = EMA(+DM,Period) / EMA(TR,Period). Values are ratios (not multiplied by 100 in this implementation).

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DIP1", "typeName": "DIP", "blockType": "ConverterItem"
    }
  ]
}
```

## EMA

- Display name: EMA
- typeName: `EMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Exponential Moving Average (EMA). EMA[0]=x[0]; EMA[i]=EMA[i-1] + k*(x[i]-EMA[i-1]), where k = 2/(Period+1). This is a classic EMA with the first value initialized from the first sample.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EMA1", "typeName": "EMA", "blockType": "ConverterItem"
    }
  ]
}
```

## FAMA

- Display name: FAMA
- typeName: `FAMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Following Adaptive Moving Average (FAMA). Companion line for MAMA: applies additional smoothing to the MAMA output using ~0.5*alpha, producing a slower "follower" curve (same FastLimit/SlowLimit bounds).

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `FastLimit` (`Double`), title="Fast limit", default=`0.5`, range=`0.1`..`1.0` step `0.1`, shown=`True`, optimizable=`True`, help="Fast limit parameter"
- `SlowLimit` (`Double`), title="Slow limit", default=`0.05`, range=`0.01`..`0.1` step `0.01`, shown=`True`, optimizable=`True`, help="Slow limit parameter"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "FAMA1", "typeName": "FAMA", "blockType": "ConverterItem"
    }
  ]
}
```

## Highest

- Display name: Highest for
- typeName: `Highest`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Highest for Period. Rolling maximum of the input series over the last Period bars (including the current bar).

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Highest1", "typeName": "Highest", "blockType": "ConverterItem"
    }
  ]
}
```

## Lowest

- Display name: Lowest for
- typeName: `Lowest`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Lowest for Period. Rolling minimum of the input series over the last Period bars (including the current bar).

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Lowest1", "typeName": "Lowest", "blockType": "ConverterItem"
    }
  ]
}
```

## LWMA

- Display name: LWMA
- typeName: `LWMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Linear Weighted Moving Average (LWMA). Weighted mean of the last Period values with weights 1..Period (most recent has the largest weight). Produces 0 until there are enough bars to fill the window.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LWMA1", "typeName": "LWMA", "blockType": "ConverterItem"
    }
  ]
}
```

## MACD

- Display name: MACD
- typeName: `MACD`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Moving Average Convergence/Divergence (MACD). Implemented as MACD = EMA(x,12) - EMA(x,26) (fixed 12/26 periods). Positive values indicate the fast EMA is above the slow EMA.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MACD1", "typeName": "MACD", "blockType": "ConverterItem"
    }
  ]
}
```

## MACDEx

- Display name: MACD Ext
- typeName: `MACDEx`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
MACD with configurable EMA periods (optimizable): EMA(x, Period1) - EMA(x, Period2). Use this when you need to tune the MACD fast/slow windows.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `Period1` (`int`), title="First period", default=`12`, range=`5`..`40` step `1`, shown=`True`, optimizable=`True`, help="First EMA period"
- `Period2` (`int`), title="Second period", default=`26`, range=`10`..`40` step `1`, shown=`True`, optimizable=`True`, help="Second EMA period"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MACDEx1", "typeName": "MACDEx", "blockType": "ConverterItem"
    }
  ]
}
```

## MACDSig

- Display name: MACD Signal
- typeName: `MACDSig`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
MACD Signal line. Implemented as EMA(MACD, Period) where the input series is typically the output of MACD or MACDEx.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`9`, range=`3`..`20` step `1`, shown=`True`, optimizable=`True`, help="Signal EMA period"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MACDSig1", "typeName": "MACDSig", "blockType": "ConverterItem"
    }
  ]
}
```

## MAMA

- Display name: MAMA
- typeName: `MAMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
MESA Adaptive Moving Average (MAMA). Adaptive filter based on Ehlers' MESA algorithm (phase/period estimation via quadrature components). Uses FastLimit/SlowLimit to bound alpha; output is an adaptive EMA of the input.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `FastLimit` (`Double`), title="Fast limit", default=`0.5`, range=`0.1`..`1.0` step `0.1`, shown=`True`, optimizable=`True`, help="Fast limit parameter"
- `SlowLimit` (`Double`), title="Slow limit", default=`0.05`, range=`0.01`..`0.1` step `0.01`, shown=`True`, optimizable=`True`, help="Slow limit parameter"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MAMA1", "typeName": "MAMA", "blockType": "ConverterItem"
    }
  ]
}
```

## MedianPrice

- Display name: Median Price
- typeName: `MedianPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Median Price. For each bar: (High + Low) / 2. Often used as a price proxy that ignores Close.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MedianPrice1", "typeName": "MedianPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## Momentum

- Display name: Momentum
- typeName: `Momentum`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Momentum (difference). MOM[i] = x[i] - x[i-Period]; for i<Period it uses x[i] - x[0]. This is a simple momentum/velocity measure in price units.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Momentum1", "typeName": "Momentum", "blockType": "ConverterItem"
    }
  ]
}
```

## MomentumOsc

- Display name: Chande Momentum Oscillator
- typeName: `MomentumOsc`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Chande Momentum Oscillator (CMO). Over Period sums positive and negative bar-to-bar changes and computes: CMO = 100 * (sumUp - sumDown) / (sumUp + sumDown). Returns 0 when the denominator is 0.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MomentumOsc1", "typeName": "MomentumOsc", "blockType": "ConverterItem"
    }
  ]
}
```

## MomentumPct

- Display name: Momentum %
- typeName: `MomentumPct`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Momentum % / Rate Of Change (ROC). ROC[i] = 100 * x[i] / x[i-Period]; for i<Period it uses 100 * x[i]/x[0]. Returns 0 when the denominator is 0.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MomentumPct1", "typeName": "MomentumPct", "blockType": "ConverterItem"
    }
  ]
}
```

## ParabolicSAR

- Display name: Parabolic SAR
- typeName: `ParabolicSAR`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Parabolic SAR (Stop And Reverse). Trails price using an acceleration factor that increases from AccelerationStart by AccelerationStep up to AccelerationMax as new extremes are made, and flips direction ("reverse") when price crosses the SAR level.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `AccelerationMax` (`Double`), title="Acceleration max", default=`0.2`, range=`0.1`..`0.4` step `0.1`, shown=`True`, optimizable=`True`, help="Acceleration limit"
- `AccelerationStart` (`Double`), title="Acceleration start", default=`0.02`, range=`0.01`..`0.1` step `0.01`, shown=`True`, optimizable=`True`, help="Initial acceleration"
- `AccelerationStep` (`Double`), title="Acceleration step", default=`0.02`, range=`0.01`..`0.1` step `0.01`, shown=`True`, optimizable=`True`, help="Step to increase acceleration"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ParabolicSAR1", "typeName": "ParabolicSAR", "blockType": "ConverterItem"
    }
  ]
}
```

## Relative

- Display name: Relative
- typeName: `Relative`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Relative change from the first sample. Uses the first value as baseline and outputs percent change: 100 * (x[i] - x[0]) / x[0]. If the baseline is 0, a large sentinel is used to avoid division by zero.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Relative1", "typeName": "Relative", "blockType": "ConverterItem"
    }
  ]
}
```

## RelativeForPeriod

- Display name: Relative for period
- typeName: `RelativeForPeriod`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Relative change per timeframe bucket. Splits bars into TimeFrame intervals; within each interval the first bar becomes baseline (output 0 at that bar) and the rest are 100 * (x - baseline) / baseline.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `TimeFrame` (`TimeSpan`), default=`1.0:0:0`, range=`0:0:1`..`365.0:0:0` step `0:0:1`, shown=`True`, optimizable=`True`, help="Timeframe (format D.HH:MM:SS)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "RelativeForPeriod1", "typeName": "RelativeForPeriod", "blockType": "ConverterItem"
    }
  ]
}
```

## RSI

- Display name: RSI
- typeName: `RSI`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Relative Strength Index (RSI). Computed from smoothed averages of up-moves and down-moves over Period: RSI = 100 - 100/(1 + AvgUp/AvgDown). This implementation uses EMA smoothing (see CuttlerRSI for the SMA-based variant); if AvgDown=0 it returns 100, and if AvgUp==AvgDown exactly it returns 0 (legacy behavior).

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "RSI1", "typeName": "RSI", "blockType": "ConverterItem"
    }
  ]
}
```

## SMA

- Display name: SMA
- typeName: `SMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Simple Moving Average (SMA). Arithmetic mean of the last Period values; on early bars it averages the available samples (the effective window grows until it reaches Period).

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SMA1", "typeName": "SMA", "blockType": "ConverterItem"
    }
  ]
}
```

## SMMA

- Display name: SMMA
- typeName: `SMMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shifted SMA used by Alligator-style indicators. Internally computes SMA(Period) and then shifts the resulting series by Shift bars (delays output by returning older SMA values).

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"
- `Shift` (`int`), default=`5`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`, help="Shift"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SMMA1", "typeName": "SMMA", "blockType": "ConverterItem"
    }
  ]
}
```

## StDev

- Display name: StDev
- typeName: `StDev`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Standard Deviation (rolling). Measures dispersion around SMA over Period: StDev = sqrt(mean((x - SMA(x,Period))^2)). Often used for Bollinger Bands and volatility estimation.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "StDev1", "typeName": "StDev", "blockType": "ConverterItem"
    }
  ]
}
```

## StochK

- Display name: StochK
- typeName: `StochK`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Stochastic %K. Uses bar High/Low and Close: %K = 100 * (Close - LowestLow(Period)) / (HighestHigh(Period) - LowestLow(Period)). Returns 0 when the High/Low range is 0. Range is typically 0..100.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "StochK1", "typeName": "StochK", "blockType": "ConverterItem"
    }
  ]
}
```

## StochRSI

- Display name: Stoch RSI
- typeName: `StochRSI`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Stochastic RSI. Computes RSI(close, Period) and then normalizes it within its rolling min/max: 100 * (RSI - LowestRSI(Period)) / (HighestRSI(Period) - LowestRSI(Period)). Returns 0 when the range is 0.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "StochRSI1", "typeName": "StochRSI", "blockType": "ConverterItem"
    }
  ]
}
```

## SumForTimeFrameHandler

- Display name: Sum for time frame
- typeName: `SumForTimeFrameHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Sum for timeframe. Running cumulative sum that resets at TimeFrame boundaries based on bar timestamps of the first security in the script. Useful for "sum within the current hour/day/week" style logic.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `TimeFrame` (`TimeSpan`), default=`1:0:0`, range=`0:0:0`..`365.0:0:0` step `0:1:0`, shown=`True`, optimizable=`True`, help="Timeframe (format D.HH:MM:SS)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SumForTimeFrameHandler1", "typeName": "SumForTimeFrameHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## SummFor

- Display name: Sum in
- typeName: `SummFor`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
SumFor (rolling sum). Computes the sum of the last Period values (including current); on early bars it sums the available samples until the window reaches Period.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SummFor1", "typeName": "SummFor", "blockType": "ConverterItem"
    }
  ]
}
```

## TEMA

- Display name: TEMA
- typeName: `TEMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Triple Exponential Moving Average (TEMA). Computed as TEMA = 3*EMA1 - 3*EMA2 + EMA3, where EMA1=EMA(x), EMA2=EMA(EMA1), EMA3=EMA(EMA2). Designed to reduce lag compared to a single EMA.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TEMA1", "typeName": "TEMA", "blockType": "ConverterItem"
    }
  ]
}
```

## TRIX

- Display name: TRIX
- typeName: `TRIX`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
TRIX. Computes a triple EMA of the input and then returns its rate of change: TRIX[i] = (EMA3[i] - EMA3[i-1]) / EMA3[i-1] (0 if the previous EMA3 is 0). Often used as a trend/momentum oscillator.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TRIX1", "typeName": "TRIX", "blockType": "ConverterItem"
    }
  ]
}
```

## TrueRange

- Display name: TR
- typeName: `TrueRange`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
True Range (TR). For each bar: TR = max(High-Low, abs(High-prevClose), abs(Low-prevClose)). Used as the base series for ATR and other volatility measures.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TrueRange1", "typeName": "TrueRange", "blockType": "ConverterItem"
    }
  ]
}
```

## TypicalPrice

- Display name: Typical Price
- typeName: `TypicalPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Typical Price. For each bar: (High + Low + Close) / 3. Used by indicators like CCI and as a smoother price proxy.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TypicalPrice1", "typeName": "TypicalPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## Volatility

- Display name: Variation
- typeName: `Volatility`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Variation / "Volatility" (variance-like). Computes the mean of squared deviations from SMA over Period: mean((x - SMA(x,Period))^2). This is similar to variance and does NOT take the square root (unlike StDev).

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Volatility1", "typeName": "Volatility", "blockType": "ConverterItem"
    }
  ]
}
```

## ZeroLagTEMA

- Display name: TEMA (Zero Lag)
- typeName: `ZeroLagTEMA`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Indicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Zero-Lag TEMA variant. Implemented as 2*TEMA(x) - TEMA(TEMA(x)) (a "double TEMA" correction) to further reduce lag compared to TEMA.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ZeroLagTEMA1", "typeName": "ZeroLagTEMA", "blockType": "ConverterItem"
    }
  ]
}
```

