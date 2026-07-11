---
name: walk-forward-validation
description: Anchored expanding-window walk-forward validation for time-series ML models. Trains per fold, optimizes threshold, reports per-fold metrics.
---

# Walk-Forward Validation

## When to use
- Evaluating time-series trading models without look-ahead bias
- User asks for "walk-forward", "backtest", or "out-of-sample testing"
- Need honest performance metrics

## Steps

1. Split data into N folds with expanding training window
2. For each fold: train models on [0..train_end], test on [test_start..test_end]
3. Optimize prediction threshold on validation subset (0.3-0.6 range)
4. Run backtest with stop-loss, take-profit, trailing stop, transaction costs
5. Concatenate equity curves, compute aggregate metrics

## Template

```python
def walk_forward(df, config, n_folds=5):
    total = len(df) - config.window
    test_size = total // (n_folds + 1)
    min_train = total // (n_folds + 1)
    equity_parts = []

    for fold in range(n_folds):
        train_end = min_train + fold * test_size
        test_start = train_end
        test_end = min(test_start + test_size, total)

        # Split: train / val / test
        train_indices = list(range(0, train_end - config.window))
        val_split = int(len(train_indices) * 0.85)

        # Train models, optimize threshold on val
        # Evaluate on test

        # Concatenate equity
        part = result["equity"].copy()
        if equity_parts: part = part * equity_parts[-1][-1]
        equity_parts.append(part)

    full_equity = np.concatenate(equity_parts)
    total_return = (full_equity[-1] / full_equity[0] - 1) * 100
    max_dd = ((full_equity / np.maximum.accumulate(full_equity)) - 1).min() * 100
    sharpe = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(365)
    return full_equity, fold_results
```

## Key gotchas
- Train window EXPANDS each fold (anchored), not slides
- Always split train→val (85/15) for threshold optimization BEFORE test
- Equity curves must be chained: `part = part * equity_parts[-1][-1]`
- Use `start_idx=test_start` in backtest to align prices with predictions
- Min 3 trades per fold to avoid noise
