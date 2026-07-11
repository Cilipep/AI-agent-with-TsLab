---
name: bybit-trailing-implementation
description: "Implement Bybit-style Trailing Up/Down for grid strategies: shifting the entire grid range when price breaks boundaries. Use when the user asks to add trailing functionality to a grid bot."
---

# Bybit Trailing Up/Down Implementation

## When to use

- User asks to add trailing to a grid strategy
- User wants the grid to follow price movements
- User references Bybit's trailing functionality

## How It Works

### Trailing Up (Восходящий трейлинг)
When price reaches or crosses the **upper boundary**:
1. Shift entire grid UP by one grid interval
2. Cancel lowest buy order
3. Place new sell order at previous upper boundary + interval
4. Stop shifting if new upper > Trailing Up Stop price

### Trailing Down (Нисходящий трейлинг)
When price reaches or crosses the **lower boundary**:
1. Shift entire grid DOWN by one grid interval
2. Cancel highest sell order
3. Place new buy order at previous lower boundary - interval
4. Stop shifting if new lower < Trailing Down Stop price

## Implementation

```python
class GridTrailing:
    def __init__(self, config):
        self.grid_lower = None
        self.grid_upper = None
        self.shifts_up = 0
        self.shifts_down = 0

    def init_grid(self, price, atr):
        gs = atr * self.config['grid_multiplier']
        self.grid_lower = price - gs
        self.grid_upper = price + gs

    def check_trailing(self, close, atr):
        if self.grid_lower is None:
            self.init_grid(close, atr)
            return

        gs = atr * self.config['grid_multiplier']

        # Trailing Up
        if close >= self.grid_upper:
            new_upper = self.grid_upper + gs
            if new_upper <= self.config['trailing_up_stop']:
                self.grid_upper = new_upper
                self.grid_lower += gs
                self.shifts_up += 1

        # Trailing Down
        if close <= self.grid_lower:
            new_lower = self.grid_lower - gs
            if new_lower >= self.config['trailing_down_stop']:
                self.grid_lower = new_lower
                self.grid_upper -= gs
                self.shifts_down += 1
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| trailing_up_stop | Upper limit for grid shift | $70,000 |
| trailing_down_stop | Lower limit for grid shift | $50,000 |
| trailing_enabled | Enable/disable trailing | True |

## Long vs Short Mode

### Neutral Mode
- Trailing Up: cancel lowest buy, place new sell above
- Trailing Down: cancel highest sell, place new buy below

### Long Mode
- Trailing Up: shift range up, keep highest sell (close-only)
- Trailing Down: shift range down, add new buy below

### Short Mode
- Trailing Up: shift range up, add new sell above
- Trailing Down: shift range down, keep lowest buy (close-only)

## Impact on Results

| Without Trailing | With Trailing |
|------------------|---------------|
| Grid static | Grid follows price |
| Miss trends | Capture trend moves |
| Lower DD | Similar DD |
| Lower Sharpe | Higher Sharpe |

## Key Rules

1. **One grid shift per boundary touch** — not multiple
2. **Respect stop prices** — don't shift beyond limits
3. **Close-only orders** — some orders are for closing only, don't cancel them
4. **Dynamic sizing** — if insufficient funds, cancel farthest orders
