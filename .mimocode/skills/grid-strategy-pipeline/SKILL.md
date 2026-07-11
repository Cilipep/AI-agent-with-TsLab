---
name: grid-strategy-pipeline
description: "End-to-end pipeline for creating grid trading strategies: from initial idea through Python backtesting, parameter optimization, leverage/reinvest testing, equity curve generation, TSLab script creation, and docx documentation. Use when the user asks to create a grid strategy."
---

# Grid Strategy Pipeline

## When to use

- User asks to create a grid trading strategy
- User wants to test grid levels, trailing up/down, or grid spacing
- User needs a complete grid strategy from idea to TSLab implementation

## Workflow

### 1. Strategy Definition

```python
CONFIG = {
    'symbol': 'BTC/USDT:USDT',
    'timeframe': '30m',
    'initial_capital': 40.0,
    'leverage': 20,
    'grid_multiplier': 2.5,      # ATR multiplier for grid spacing
    'stop_multiplier': 3.0,      # ATR multiplier for stop loss
    'risk_per_trade': 0.10,
    'reinvest_pct': 0.30,
    'commission': 0.0005,
    'atr_period': 14,
    'trailing_up_stop': 70000,
    'trailing_down_stop': 50000,
    'trailing_enabled': True,
}
```

### 2. Python Backtest Class

```python
class GridBot:
    def __init__(self, config):
        self.config = config
        self.capital = config['initial_capital']
        self.position = None
        self.trades = []
        self.equity = []
        self.grid_lower = None
        self.grid_upper = None

    def calc_atr(self, df, period=14):
        h, l, c = df['High'], df['Low'], df['Close'].shift(1)
        tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def check_trailing(self, close, atr):
        """Bybit-style Trailing Up/Down"""
        if self.grid_lower is None:
            self.grid_lower = close - atr * self.config['grid_multiplier']
            self.grid_upper = close + atr * self.config['grid_multiplier']
            return
        gs = atr * self.config['grid_multiplier']
        if close >= self.grid_upper:
            new_upper = self.grid_upper + gs
            if new_upper <= self.config['trailing_up_stop']:
                self.grid_upper = new_upper
                self.grid_lower += gs
        if close <= self.grid_lower:
            new_lower = self.grid_lower - gs
            if new_lower >= self.config['trailing_down_stop']:
                self.grid_lower = new_lower
                self.grid_upper -= gs

    def open_position(self, pos_type, price, atr):
        stop_dist = atr * self.config['stop_multiplier']
        tp_dist = atr * self.config['grid_multiplier']
        if pos_type == 'long':
            stop, tp = price - stop_dist, price + tp_dist
        else:
            stop, tp = price + stop_dist, price - tp_dist
        # ... position sizing logic

    def process_bar(self, close, low, high, atr):
        self.check_trailing(close, atr)
        # ... exit checks, entry logic, equity tracking
```

### 3. Parameter Sweep Pattern

```python
leverages = [1, 3, 5, 10, 15, 20, 25, 30]
reinvests = [0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 1.00]

for lev in leverages:
    for reinvest in reinvests:
        cfg = CONFIG.copy()
        cfg['leverage'] = lev
        cfg['reinvest_pct'] = reinvest
        bot = GridBot(cfg)
        metrics = bot.backtest(df)
        results.append(metrics)
```

### 4. Multi-Coin Comparison

```python
coins = {
    'BTC': {'ticker': 'BTC-USD', 'trailing_up': 70000, 'trailing_down': 50000},
    'ETH': {'ticker': 'ETH-USD', 'trailing_up': 5000, 'trailing_down': 2000},
    'ADA': {'ticker': 'ADA-USD', 'trailing_up': 0.25, 'trailing_down': 0.10},
}
```

### 5. Equity Curve Visualization

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 1, figsize=(14, 10))
# Panel 1: Equity curve with fill
# Panel 2: Underlying price
# Panel 3: Drawdown %
```

### 6. TSLab Script Creation

Grid levels in TSLab:
- ATR14 → GridSpacing (ATR × GridMultiplier)
- GridLevelBuy = Close - GridSpacing
- GridLevelSell = Close + GridSpacing
- StopLevelLong = Close - StopDist
- StopLevelShort = Close + StopDist

### 7. Documentation

Create docx with:
- Strategy overview
- Parameters table
- Backtest results
- Leverage/reinvest comparison
- Risk management
- File listing

## Key Metrics to Track

| Metric | Target |
|--------|--------|
| PnL | Positive |
| Win Rate | > 60% |
| Profit Factor | > 1.0 |
| Max Drawdown | < 50% |
| Sharpe Ratio | > 5.0 |

## Common Pitfalls

1. **50x leverage** → liquidation risk too high
2. **100% reinvest** → PF drops below 1.0
3. **Fixed % SL/TP** → worse than ATR-based
4. **Ignoring trailing** → missed profit in trends
