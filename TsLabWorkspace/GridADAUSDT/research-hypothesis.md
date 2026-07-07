# Research Hypothesis

## Strategy Type
Grid Trading Strategy — Mean Reversion in Range-Bound Markets

## Market Context
- **Asset**: ADA (Cardano) — mid-cap altcoin with moderate volatility
- **Instrument**: ADAUSDT Perpetual Futures
- **Exchange**: Binance Coin-M Futures
- **Timeframe**: 30-minute bars
- **Expected regime**: Sideways/ranging markets (60-70% of time for ADA)

## Hypothesis Statement

**This strategy tries to profit from** repeated price oscillations within a defined grid range by placing symmetric buy and sell limit orders at regular intervals.

**It should trade when**:
- ADA price is range-bound (no strong trend)
- Volatility is moderate (enough movement to trigger grid levels, not so much that stops are hit)
- Price is within the defined grid boundaries

**It should avoid trading when**:
- Strong directional trend (price breaks out of grid range)
- Extremely low volatility (grid levels never reached)
- Extreme volatility (stops triggered before take-profit)

## Signal Source and Predictive Value

**Signal source**: Price position relative to grid levels
- **Predictive value**: In ranging markets, price tends to revert to mean after touching grid boundaries. Each grid level acts as a mini-support/resistance.

**Why it should work**:
- ADA spends 60-70% of time in ranges
- Grid captures profit from each oscillation
- Symmetric long/short grid profits from both directions
- 30m timeframe provides enough bars for grid triggers without excessive noise

**Why it might fail**:
- Strong trends cause grid levels to be hit sequentially (accumulating losses)
- Gap moves can skip grid levels
- High volatility can trigger stops before take-profit

## Entry Logic

**Long entries**:
- Buy limit orders placed at GridLevel[i] = CurrentPrice - (i * GridSpacing)
- Orders trigger when price touches or crosses below the level
- Each level can have fixed position size or pyramid sizing

**Short entries**:
- Sell limit orders placed at GridLevel[i] = CurrentPrice + (i * GridSpacing)
- Orders trigger when price touches or crosses above the level
- Symmetric to long entries

## Exit Logic

**Take-profit**:
- Long exit: Close position when price reaches next grid level above entry
- Short exit: Close position when price reaches next grid level below entry
- Profit per grid = GridSpacing - Commission

**Stop-loss** (engineering stop for baseline safety):
- Per-position stop: ATR-based stop below/above entry
- Account-level stop: Maximum drawdown limit
- Optional and switchable

## Position Sizing

**Per-trade risk**: 1% of capital
**Grid level sizing**: Fixed fractional (equal size per level)
**Maximum positions**: Limited by grid levels and risk per trade
**Leverage**: 3x (conservative for crypto futures)

## Data Requirements

- Historical ADAUSDT 30m data: 3-6 months for backtest
- Real-time 30m bars for live trading
- Volume data optional (grid doesn't depend on volume)

## Falsification Criteria

**Idea is worth keeping if**:
- Profit factor > 1.2
- Win rate > 50%
- Maximum drawdown < 15%
- Sharpe ratio > 1.0

**Idea is falsified if**:
- Profit factor < 1.0 (net loss)
- Maximum drawdown > 25%
- Strategy cannot recover from drawdown within 30 days

## First TSLab Prototype Should Prove

1. Grid levels are correctly calculated and displayed
2. Long and short grid orders trigger at expected price levels
3. Take-profit closes positions at next grid level
4. Stop-loss protects against excessive losses
5. Position sizing respects risk limits
6. Visual inspection shows clean grid structure on chart
