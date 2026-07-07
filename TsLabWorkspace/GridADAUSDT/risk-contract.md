# Risk Contract — Grid ADAUSDT

## Entry Price Source
- **Long**: Limit order at `GridBuyLevel[i] = Close - (i * GridSpacing)`
- **Short**: Limit order at `GridSellLevel[i] = Close + (i * GridSpacing)`

## Protective Stop
- **Long stop**: `EntryPrice - (ATR(14) * StopMultiplier)`
- **Short stop**: `EntryPrice + (ATR(14) * StopMultiplier)`
- **Source**: ATR(14) indicator
- **Update**: Entry-anchored (fixed at entry time)

## Risk Per Unit
- **Distance**: ATR(14) * StopMultiplier
- **Example**: If ATR=0.005, StopMultiplier=2.0 → risk per unit = 0.01

## Account Risk Per Trade
- **Risk percent**: 1% of capital
- **Capital base**: Initial deposit (25 USDT)
- **Risk money**: 25 * 0.01 = 0.25 USDT per trade

## Position Size Calculation
```
RiskMoney = Capital * RiskPct = 25 * 0.01 = 0.25 USDT
RiskPerUnit = ATR * StopMultiplier = 0.005 * 2.0 = 0.01
Shares = RiskMoney / RiskPerUnit = 0.25 / 0.01 = 25 ADA
```

## Shares Connection
- **Method**: Formula-based calculation
- **Formula**: `Shares = floor(RiskMoney / RiskPerUnit)`
- **Connection**: Direct formula output to entry block `Shares` input

## Stop Behavior When Invalid
- **If stop missing**: Skip trade (do not enter)
- **If stop on wrong side**: Skip trade
- **If ATR zero**: Skip trade (avoid division by zero)

## Engineering Stop
- **Status**: Optional, switchable
- **Parameter**: `StopEnabled` (true/false)
- **Default**: true (enabled for baseline safety)
- **Gate**: Logical constant controls enable/disable

## Commission
- **Model**: RelativeCommission
- **Rate**: 0.05% (Binance futures taker fee)
- **Margin,%**: 0 (crypto perpetual, no stock-borrow model)
- **Slippage**: 0.02% assumed

## Position Sizing Rules
- **Method**: Fixed fractional
- **Per-trade risk**: 1% of capital
- **Maximum position**: 20% of capital per grid level
- **Maximum total exposure**: 100% of capital (all grid levels combined)

## Risk Parameters
| Parameter | Value | Optimization-ready |
|-----------|-------|-------------------|
| RiskPct | 1% | Yes (0.5%, 1%, 1.5%, 2%) |
| StopMultiplier | 2.0 | Yes (1.5, 2.0, 2.5, 3.0) |
| MaxPositionPct | 20% | Yes (10%, 15%, 20%, 25%) |
| StopEnabled | true | Yes (true/false) |

## Worst-Case Per-Trade Loss
- **Maximum loss**: 1% of capital = 0.25 USDT
- **Scenario**: Price gaps through stop level
- **Protection**: ATR-based stop adapts to volatility

## Capital Base
- **Source**: Initial deposit (25 USDT)
- **Type**: Fixed constant
- **Not recalculated**: Risk is based on initial capital, not equity

## Risk Model Status
- **Entry-anchored stop**: Yes
- **Dynamic protective**: Yes (ATR-based)
- **Trailing stop**: No (grid strategy uses fixed grid levels)
- **Account-level stop**: Maximum drawdown 20%
