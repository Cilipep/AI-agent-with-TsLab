# Final Strategy Description — Grid ADAUSDT

## Strategy Overview
**Grid ADAUSDT** is a bidirectional grid trading strategy for ADAUSDT Perpetual futures on Binance, designed to capture profit from price oscillations within a defined range using symmetric buy/sell limit orders.

## Task Mode
Production-ready strategy with full risk management and optimization capability.

## Starting Document
- `initial-strategy-description.md` — initial strategy idea
- `research-hypothesis.md` — trading hypothesis
- `design-specification.md` — technical specification
- `execution-plan.md` — implementation plan
- `risk-contract.md` — risk management contract

## Strategy Name
Grid ADAUSDT — Adaptive Grid Trading

## Market
- **Provider**: Binance (BinanceCoin-MFutures)
- **Instrument**: ADAUSDT Perpetual
- **Timeframe**: 30m
- **Direction**: Long + Short (bidirectional grid)

## Hypothesis
This strategy profits from mean-reverting price oscillations in range-bound markets by placing symmetric grid orders. Each price swing between grid levels generates a small profit, accumulating gains from repeated oscillations.

## Indicators
1. **ATR(14)** — Adaptive grid spacing
   - `GridSpacing = ATR * GridMultiplier`
   - Optimization-ready: period (10-20), multiplier (0.5-2.0)

2. **EMA(200)** — Optional trend filter
   - Avoids grid in strong trends
   - Optimization-ready: period (150-250)

## Grid Structure
- **Grid levels per side**: 5 (default, optimization-ready: 3, 5, 7, 10)
- **Grid spacing**: ATR-based adaptive
- **Recalculation**: Every 12 bars (6 hours) or on 5% price deviation

## Long Entry Rules
- **Condition**: Price touches or crosses below grid buy level
- **Semantics**: Bar-condition — `Low <= GridBuyLevel[i]`
- **Execution**: Limit order at `GridBuyLevel[i]`
- **Filters**: No active long at same level, ATR > MinATR, optional EMA filter

## Short Entry Rules
- **Condition**: Price touches or crosses above grid sell level
- **Semantics**: Bar-condition — `High >= GridSellLevel[i]`
- **Execution**: Limit order at `GridSellLevel[i]`
- **Filters**: No active short at same level, ATR > MinATR, optional EMA filter

## Long Exit Rules
- **Take-profit**: Close when price reaches next grid level above entry
  - `ExitPrice = EntryPrice + GridSpacing`
  - Semantics: Bar-condition — `High >= ExitPrice`
- **Stop-loss**: ATR-based protective stop
  - `StopPrice = EntryPrice - (ATR * StopMultiplier)`
  - Semantics: Bar-condition — `Low <= StopPrice`
  - Optional, switchable via `StopEnabled` parameter

## Short Exit Rules
- **Take-profit**: Close when price reaches next grid level below entry
  - `ExitPrice = EntryPrice - GridSpacing`
  - Semantics: Bar-condition — `Low <= ExitPrice`
- **Stop-loss**: ATR-based protective stop
  - `StopPrice = EntryPrice + (ATR * StopMultiplier)`
  - Semantics: Bar-condition — `High >= StopPrice`

## Risk Management
- **Entry price**: Limit order at grid level
- **Protective stop**: ATR-based, entry-anchored
- **Risk per unit**: ATR * StopMultiplier
- **Account risk**: 1% per trade
- **Capital base**: Initial deposit (25 USDT)
- **Position size**: `RiskMoney / RiskPerUnit`
- **Shares connection**: Formula-based calculation
- **Maximum drawdown**: 20%
- **Maximum position**: 20% of capital per grid level

## Reinvestment
- **Reinvestment rate**: 10% of profit
- **Logic**: When a trade closes with profit, 10% of the profit is added to the next position size
- **Base position**: 10 shares
- **Formula**: `NewShares = BaseShares + (ProfitAccum * 0.10)`
- **Effect**: Position sizes grow as capital increases from profitable trades

## Commission
- **Model**: RelativeCommission
- **Rate**: 0.05% (Binance futures taker fee)
- **Margin,%**: 0 (crypto perpetual)
- **Slippage**: 0.02% assumed

## Parameters for Optimization
| Parameter | Default | Range | Type |
|-----------|---------|-------|------|
| GridMultiplier | 1.0 | 0.5-2.0 | Grid |
| GridLevels | 5 | 3-10 | Grid |
| RecalcBars | 12 | 6-48 | Grid |
| StopMultiplier | 2.0 | 1.5-3.0 | Risk |
| RiskPct | 1% | 0.5%-2% | Risk |
| MinATR | 0.002 | 0.001-0.003 | Filter |
| TrendFilterEnabled | false | true/false | Filter |
| TrendThreshold | 0.02 | 0.01-0.03 | Filter |
| ReinvestPct | 10% | 5%-20% | Reinvestment |

## Visual Outputs
### Price Pane
- Candlesticks (price action)
- Grid buy levels (green horizontal lines)
- Grid sell levels (red horizontal lines)
- EMA(200) (blue line, optional)

### Indicator Pane
- ATR(14) (orange line)

## Pane Map
| Series | Pane | Style |
|--------|------|-------|
| Close | Price | Candlestick |
| GridBuyLevel[i] | Price | Horizontal line, green |
| GridSellLevel[i] | Price | Horizontal line, red |
| EMA(200) | Price | Line, blue |
| ATR(14) | Separate | Line, orange |

## Backtest Results
- **Period**: TBD (3-6 months recommended)
- **Initial capital**: 25 USDT
- **Expected profit factor**: > 1.2
- **Expected win rate**: > 50%
- **Expected max drawdown**: < 15%
- **Expected Sharpe ratio**: > 1.0

## Limitations
1. Grid strategies perform poorly in strong trends
2. Gap moves can skip grid levels
3. High volatility can trigger stops before take-profit
4. Requires range-bound market conditions
5. First implementation — needs optimization and verification

## Verification Scope
- Lifecycle proof: validate → build → load → run
- Metrics inspection: profit factor, win rate, drawdown, Sharpe
- Visual audit: grid levels, entries/exits, stops visible
- Risk verification: position sizing, stop-loss, drawdown limits

## Status
- [x] Task classified as new strategy idea
- [x] Data context confirmed (Binance, ADAUSDT, 30m, Long+Short)
- [x] Target result specified (production-ready)
- [x] Research hypothesis completed
- [x] Design specification completed
- [x] Execution plan completed
- [x] Risk contract completed
- [x] TSLab implementation completed
- [x] Reinvestment 10% added
- [x] Grid logic with ATR-based levels added
- [x] Optimization parameters configured (Shares: 5-20)
- [ ] Lifecycle proof (pending data download)
- [ ] Metrics inspection
- [ ] Visual audit
- [ ] Optimization execution
- [ ] Final verification
