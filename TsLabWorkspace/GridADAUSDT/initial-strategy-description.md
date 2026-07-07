# Initial Strategy Description

## Strategy Name
Grid ADAUSDT — Grid Trading with Adaptive Grid Spacing

## Task Mode
New strategy idea

## Data Context
- **Provider**: Binance (BinanceCoin-MFutures)
- **Instrument**: ADAUSDT Perpetual
- **Timeframe**: 30m
- **Direction**: Long + Short (bidirectional)

## Trading Hypothesis
This strategy tries to profit from **mean-reverting price oscillations** within a defined range by placing a grid of limit orders at regular intervals. The grid captures profit from each price swing between grid levels, accumulating small gains from repeated oscillations.

**Core idea**: In ranging or slowly trending markets, price tends to oscillate between support and resistance levels. A grid strategy places buy orders below current price and sell orders above, profiting from each completed cycle.

**Expected market regime**: Sideways or range-bound markets with moderate volatility. The strategy should perform best when ADA trades within a defined price corridor.

## Target Result
Production-ready strategy with:
- Full risk management
- Position sizing
- Stop-loss protection
- Grid parameter optimization capability
- Clean visual inspection in TSLab

## Open Questions for Design
1. Grid spacing: fixed percentage or ATR-based adaptive?
2. Number of grid levels (how many orders per side)?
3. Order sizing: equal size per level or pyramid?
4. Take-profit per grid level or only at grid extremes?
5. Stop-loss: per-position or account-level?
6. Rebalancing logic when price breaks out of grid range?
7. Maximum position size limits?

## Expected Entries and Exits
- **Long entries**: Buy limit orders placed at grid levels below current price
- **Short entries**: Sell limit orders placed at grid levels above current price
- **Long exits**: Take-profit at next grid level above entry, or stop-loss
- **Short exits**: Take-profit at next grid level below entry, or stop-loss

## Initial Risk Intent
- Per-trade risk: 1-2% of capital
- Maximum drawdown limit: 20%
- Position sizing: Fixed fractional or Kelly criterion
- Engineering stop: Optional, switchable

## Status
- [x] Task classified as new strategy idea
- [x] Data context confirmed (Binance, ADAUSDT, 30m, Long+Short)
- [x] Target result specified (production-ready)
- [ ] Research hypothesis needed
- [ ] Design specification needed
- [ ] Execution plan needed
