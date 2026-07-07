# Execution Plan — Grid ADAUSDT

## Goal
Production-ready Grid trading strategy for ADAUSDT Perpetual 30m with full risk management.

## Phase 1: Create Script

**Artifact**: New TSLab script `GridADAUSDT`
**Action**: 
1. Create script via TSLab Web API
2. Map data source: Binance, ADAUSDT Perpetual, 30m
3. Confirm provider connection and data availability

**Proof**: Script created, data mapped, bars visible in TSLab
**Blocker**: If provider unavailable or instrument not found → stop and report

## Phase 2: Build Grid Calculation

**Artifact**: Grid formula blocks
**Action**:
1. Add ATR(14) indicator block
2. Add grid calculation formulas:
   - `GridSpacing = ATR * GridMultiplier`
   - `GridBuyLevel[i] = Close - (i * GridSpacing)`
   - `GridSellLevel[i] = Close + (i * GridSpacing)`
3. Add grid level display (horizontal lines)

**Proof**: Grid levels calculated and visible on chart
**Blocker**: If grid levels not displaying → repair formula connections

## Phase 3: Build Trade Path

**Artifact**: Entry/exit logic
**Action**:
1. Add long entry conditions:
   - `Low <= GridBuyLevel[i]` (bar-condition)
   - No active long at same level
2. Add short entry conditions:
   - `High >= GridSellLevel[i]` (bar-condition)
   - No active short at same level
3. Add take-profit exits:
   - Long: `High >= EntryPrice + GridSpacing`
   - Short: `Low <= EntryPrice - GridSpacing`

**Proof**: Entries and exits trigger at expected grid levels
**Blocker**: If entries not triggering → check condition logic

## Phase 4: Add Risk Management

**Artifact**: Stop-loss and position sizing
**Action**:
1. Add ATR-based stop-loss:
   - Long stop: `EntryPrice - (ATR * StopMultiplier)`
   - Short stop: `EntryPrice + (ATR * StopMultiplier)`
2. Add position sizing formula:
   - `RiskMoney = Capital * RiskPct`
   - `RiskPerUnit = ATR * StopMultiplier`
   - `Shares = RiskMoney / RiskPerUnit`
3. Connect `Shares` to entry blocks

**Proof**: Stop-loss levels calculated, position size connected
**Blocker**: If `Shares` disconnected → repair sizing formula

## Phase 5: Add Risk Controls

**Artifact**: Account-level risk limits
**Action**:
1. Add maximum drawdown check (20%)
2. Add maximum position limit (20% of capital)
3. Add minimum ATR filter (avoid low volatility)
4. Add optional trend filter (EMA 200)

**Proof**: Risk limits enforced, no excessive positions
**Blocker**: If risk limits not working → repair control logic

## Phase 6: Clean Graph

**Artifact**: Remove unnecessary blocks
**Action**:
1. Remove debug blocks
2. Remove temporary thresholds
3. Remove auto-visualization blocks
4. Verify no dead blocks

**Proof**: Clean graph with only strategy logic
**Blocker**: If essential blocks removed → restore from backup

## Phase 7: Lifecycle Proof

**Artifact**: TSLab lifecycle run
**Action**:
1. Validate script
2. Build script
3. Load script
4. Run script
5. Check metrics

**Proof**: Script runs without errors, metrics calculated
**Blocker**: If lifecycle fails → repair based on error

## Phase 8: Metrics Inspection

**Artifact**: Performance report
**Action**:
1. Net profit > 0
2. Profit factor > 1.2
3. Win rate > 50%
4. Max drawdown < 15%
5. Sharpe ratio > 1.0

**Proof**: All metrics meet thresholds
**Blocker**: If metrics poor → analyze and decide: repair or accept prototype

## Phase 9: Visual Audit

**Artifact**: Chart inspection
**Action**:
1. Grid levels visible on price chart
2. Entries/exits marked correctly
3. Stop-loss levels visible
4. No chart artifacts

**Proof**: Clean visual inspection
**Blocker**: If visual issues → repair display

## Phase 10: Documentation

**Artifact**: Strategy documentation
**Action**:
1. Final strategy description
2. Parameter list
3. Risk documentation
4. Visual guide

**Proof**: Complete documentation exists
**Blocker**: If documentation missing → create before finalization

## Decision Gate

After Phase 10:
- If metrics acceptable → proceed to optimization or finalization
- If metrics poor → repair loop or accept as prototype
- If visual issues → repair display

## Stop Contract Summary

| Item | Value |
|------|-------|
| Source | ATR(14) |
| Long stop | Entry - ATR * StopMultiplier |
| Short stop | Entry + ATR * StopMultiplier |
| Update | Entry-anchored (fixed) |
| Policy | Bar-condition (High/Low touch) |
| Close allowed | No |
| Auxiliary | ATR only |
| May loosen | No |
| Type | Dynamic protective |
| Optional | Yes, switchable via StopEnabled parameter |

## Risk Contract Summary

| Item | Value |
|------|-------|
| Entry price | Limit order at grid level |
| Protective stop | ATR-based |
| Risk per unit | ATR * StopMultiplier |
| Account risk | 1% per trade |
| Capital base | Initial deposit (25 USDT) |
| Position size | RiskMoney / RiskPerUnit |
| Shares connection | Formula-based |
| Stop missing | Skip trade |
| Engineering stop | Optional, switchable |
| Commission | 0.05% relative |
| Margin,% | 0 (crypto) |
| Sizing | Fixed fractional, optimization-ready |
