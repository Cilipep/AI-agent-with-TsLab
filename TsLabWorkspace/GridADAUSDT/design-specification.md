# Design Specification

## Strategy Name
Grid ADAUSDT — Adaptive Grid Trading

## Market and Data
- **Provider**: Binance (BinanceCoin-MFutures)
- **Instrument**: ADAUSDT Perpetual
- **Timeframe**: 30m
- **Direction**: Long + Short (bidirectional grid)

## Trading Hypothesis
Capture profit from price oscillations within a defined grid range by placing symmetric buy/sell limit orders at regular intervals. Each price swing between grid levels generates a small profit, accumulating gains from repeated oscillations in range-bound markets.

## Indicators and Input Series

### Primary Indicators
1. **Grid Calculation** (formula-based):
   - `GridSpacing = ATR(14) * GridMultiplier`
   - `GridLevel[i] = Close[0] ± (i * GridSpacing)`
   - Grid levels recalculated every N bars or on significant price move

2. **ATR(14)** — for adaptive grid spacing
   - Built-in TSLab block: `Indicators.ATR(Series, period)`
   - Optimization-ready: period (10-20), multiplier (0.5-2.0)

3. **EMA(200)** — trend filter (optional)
   - Built-in TSLab block: `Indicators.EMA(Series, period)`
   - Used to avoid grid in strong trends
   - Optimization-ready: period (150-250)

### Grid Parameters (optimization-ready)
- `GridSpacing` — distance between grid levels (ATR-based)
- `GridMultiplier` — ATR multiplier for spacing (default: 1.0)
- `GridLevels` — number of levels per side (default: 5)
- `RecalcBars` — bars between grid recalculations (default: 12 = 6 hours)
- `MaxGridDeviation` — max % price can move before grid reset (default: 5%)

## Long Entry Rules

**Condition**: Price touches or crosses below a grid buy level
**Semantics**: Bar-condition — `Low <= GridBuyLevel[i]`
**Execution**: Limit order at `GridBuyLevel[i]`
**Filter**: 
- No active long at same grid level
- ATR filter: ATR(14) > MinATR (avoid extremely low volatility)
- Optional trend filter: Price > EMA(200) * (1 - TrendThreshold)

## Short Entry Rules

**Condition**: Price touches or crosses above a grid sell level
**Semantics**: Bar-condition — `High >= GridSellLevel[i]`
**Execution**: Limit order at `GridSellLevel[i]`
**Filter**:
- No active short at same grid level
- ATR filter: ATR(14) > MinATR
- Optional trend filter: Price < EMA(200) * (1 + TrendThreshold)

## Long Exit Rules

**Take-profit**: Close long when price reaches next grid level above entry
- `ExitPrice = EntryPrice + GridSpacing`
- Semantics: Bar-condition — `High >= ExitPrice`

**Stop-loss**: ATR-based protective stop
- `StopPrice = EntryPrice - (ATR(14) * StopMultiplier)`
- Semantics: Bar-condition — `Low <= StopPrice`
- Optional engineering stop, switchable via parameter

## Short Exit Rules

**Take-profit**: Close short when price reaches next grid level below entry
- `ExitPrice = EntryPrice - GridSpacing`
- Semantics: Bar-condition — `Low <= ExitPrice`

**Stop-loss**: ATR-based protective stop
- `StopPrice = EntryPrice + (ATR(14) * StopMultiplier)`
- Semantics: Bar-condition — `High >= StopPrice`

## Stop Contract

| Attribute | Value |
|-----------|-------|
| Source series | ATR(14) |
| Update rule | Entry-anchored (fixed at entry) |
| Current bar policy | Bar-condition (Low/High touch) |
| Close allowed | No (use High/Low for more conservative trigger) |
| Auxiliary indicators | Yes (ATR only) |
| May loosen risk | No (stop only tightens or stays) |
| Result type | Dynamic protective (ATR-based) |

## Position Sizing

**Method**: Fixed fractional
- Risk per trade: 1% of capital
- Position size: `Size = (Capital * RiskPct) / (ATR * StopMultiplier)`
- Shares connection: Formula-based calculation

**Leverage**: 3x (conservative for crypto futures)
**Maximum position**: 20% of capital per grid level

## Commission and Slippage

**Commission model**: RelativeCommission
- Rate: 0.05% (Binance futures taker fee)
- Margin,%: 0 (crypto perpetual, no stock-borrow model)

**Slippage assumption**: 0.02% per trade (conservative for ADA)

## Parameters for Optimization

### Grid Parameters
- `GridMultiplier` — ATR multiplier (0.5, 0.75, 1.0, 1.25, 1.5)
- `GridLevels` — levels per side (3, 5, 7, 10)
- `RecalcBars` — recalculation frequency (6, 12, 24, 48 bars)

### Risk Parameters
- `StopMultiplier` — ATR stop multiplier (1.5, 2.0, 2.5, 3.0)
- `RiskPct` — risk per trade (0.5%, 1%, 1.5%, 2%)

### Filter Parameters
- `MinATR` — minimum ATR for trading (0.001, 0.002, 0.003)
- `TrendFilterEnabled` — enable EMA trend filter (true/false)
- `TrendThreshold` — EMA threshold (0.01, 0.02, 0.03)

## Visual Outputs

### Price Pane
- **Candlesticks** — price action
- **Grid levels** — horizontal lines at buy/sell levels (green for buy, red for sell)
- **EMA(200)** — optional trend filter line (blue)

### Indicator Pane
- **ATR(14)** — volatility measure for grid spacing
- **Position entries/exits** — arrows or markers

### Pane Map
| Series | Pane | Style |
|--------|------|-------|
| Close | Price | Candlestick |
| GridBuyLevel[i] | Price | Horizontal line, green |
| GridSellLevel[i] | Price | Horizontal line, red |
| EMA(200) | Price | Line, blue |
| ATR(14) | Separate | Line, orange |
| Entry signals | Price | Arrow up (long), arrow down (short) |

## Proof Plan

### Lifecycle
1. Create script with grid formula blocks
2. Map data source (Binance, ADAUSDT, 30m)
3. Build trade path with grid entries/exits
4. Add risk management (stop-loss, position sizing)
5. Run lifecycle: validate → build → load → run

### Metrics Check
- Net profit > 0
- Profit factor > 1.2
- Win rate > 50%
- Max drawdown < 15%
- Sharpe ratio > 1.0

### Visual Audit
- Grid levels visible on price chart
- Entries/exits marked correctly
- No dead blocks or unused formulas
- Clean pane assignment

### Intent Check
- Strategy logic matches design specification
- No hidden rules or silent assumptions
- Risk parameters documented and exposed
