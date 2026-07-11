---
name: parameter-sensitivity-sweep
description: "Systematically test multiple parameter combinations (leverage, reinvest, risk, etc.) and produce comparison tables. Use when the user wants to find optimal parameters or understand parameter sensitivity."
---

# Parameter Sensitivity Sweep

## When to use

- User wants to test multiple leverage levels
- User wants to compare different reinvestment percentages
- User wants to find optimal risk/return balance
- User asks "what happens if I change X parameter"

## Workflow

### 1. Define Parameter Grid

```python
param_grid = {
    'leverage': [1, 3, 5, 10, 15, 20, 25, 30],
    'reinvest_pct': [0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 1.00],
    'risk_per_trade': [0.05, 0.10, 0.15, 0.20],
}
```

### 2. Run Sweep

```python
results = []
for lev in param_grid['leverage']:
    for reinvest in param_grid['reinvest_pct']:
        cfg = base_config.copy()
        cfg['leverage'] = lev
        cfg['reinvest_pct'] = reinvest
        bot = GridBot(cfg)
        m = bot.backtest(df)
        results.append({'leverage': lev, 'reinvest': reinvest, **m})
```

### 3. Analysis Table

```python
# Sort by Sharpe
results.sort(key=lambda x: x['sharpe'], reverse=True)

# Print comparison
print(f"{'Leverage':>8} {'Reinvest':>8} {'PnL%':>8} {'PF':>6} {'DD%':>6} {'Sharpe':>7}")
for r in results[:10]:
    print(f"{r['leverage']:>7}x {r['reinvest']*100:>7.0f}% {r['pnl_pct']:>7.1f}% {r['pf']:>6.2f} {r['mdd']:>5.1f}% {r['sharpe']:>7.2f}")
```

### 4. Key Insights Pattern

| Finding | Implication |
|---------|-------------|
| 50x → liquidation | Leverage > 30x too risky |
| 100% reinvest → PF < 1.0 | Over-compounding hurts |
| 30-45% reinvest → best balance | Optimal risk/return |
| ATR-based SL/TP > fixed % | Dynamic beats static |

### 5. Visualization

```python
# Heatmap of PnL by leverage × reinvest
import seaborn as sns
pivot = pd.pivot_table(df, values='pnl_pct', index='leverage', columns='reinvest')
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='RdYlGn')
```

## Decision Framework

| If PF > 1.2 and Sharpe > 8 | → Good candidate |
| If PF > 1.0 but Sharpe < 5 | → Acceptable, monitor |
| If PF < 1.0 | → Rejected, find better params |
| If DD > 50% | → Too risky, reduce leverage |
| If lever > 30x and DD > 80% | → Liquidation risk |

## Output Format

Always produce:
1. Comparison table (top 10 by Sharpe)
2. Best configuration recommendation
3. Risk warnings
4. Save results to JSON
