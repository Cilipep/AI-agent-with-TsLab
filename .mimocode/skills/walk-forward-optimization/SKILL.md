---
name: walk-forward-optimization
description: Walk-forward validation workflow for ML trading models with leak-proof data splitting, threshold/weight optimization, and ensemble creation
---

# Walk-Forward Optimization Playbook

Reusable workflow for time-series ML model validation and optimization.

## Core Principles

1. **No look-ahead bias** — scaler fit on train only, transform on val/test
2. **Proper validation split** — 85/15 train/val within each fold's training data
3. **Threshold optimization** — find optimal decision threshold on validation
4. **Weight optimization** — grid search over weight combinations for ensembles
5. **Result aggregation** — concatenate equity curves across folds

## Workflow Steps

### Step 1: Data Preparation

```python
from sklearn.preprocessing import StandardScaler

# Create dataset with external scaler
scaler = StandardScaler()
scaler.fit(train_data)  # Fit ONLY on training data
train_scaled = scaler.transform(train_data)
val_scaled = scaler.transform(val_data)  # Transform with fitted scaler
test_scaled = scaler.transform(test_data)
```

### Step 2: Walk-Forward Loop

```python
for fold in range(n_folds):
    # Split into train/val/test
    full_train_indices = list(range(0, train_end - window))
    val_split = int(len(full_train_indices) * 0.85)
    train_indices = full_train_indices[:val_split]
    val_indices = full_train_indices[val_split:]
    
    # Train models
    models = []
    for seed in seeds:
        model = build_model(config)
        model = train(model, train_ds, val_ds, config)  # Early stop on val
        models.append(model)
```

### Step 3: Threshold Optimization

```python
def find_best_threshold(model, val_ds, df, config, start_idx):
    best_threshold = 0.5
    best_return = -float("inf")
    
    for threshold in [0.3, 0.35, 0.4, 0.45, 0.5]:
        result = run_backtest(model, val_ds, df, config, 
                            threshold=threshold, start_idx=start_idx)
        if result["n_trades"] > 0 and result["total_return_pct"] > best_return:
            best_return = result["total_return_pct"]
            best_threshold = threshold
    
    return best_threshold
```

### Step 4: Weight Optimization (for ensembles)

```python
def find_best_weights(models, val_ds, df, config, start_idx):
    best_weights = [1.0 / len(models)] * len(models)
    best_return = -float("inf")
    
    # Grid search
    steps = [0.1, 0.2, 0.3, 0.4, 0.5]
    for combo in product(steps, repeat=len(models)):
        if abs(sum(combo) - 1.0) > 0.01:
            continue  # Weights must sum to 1
        
        ensemble = Ensemble(models, list(combo))
        result = run_backtest(ensemble, val_ds, df, config, 
                            threshold=0.5, start_idx=start_idx)
        
        if result["n_trades"] > 0 and result["total_return_pct"] > best_return:
            best_return = result["total_return_pct"]
            best_weights = list(combo)
    
    return best_weights
```

### Step 5: Test Set Evaluation

```python
# Use optimized weights and threshold on test set
ensemble = Ensemble(models, best_weights)
result = run_backtest(ensemble, test_ds, df, config, 
                    threshold=best_threshold, start_idx=test_start)
```

## Common Pitfalls to Avoid

1. **Variable shadowing** — don't reuse `total` as loop counter when it's dataset size
2. **Scaler on all data** — always fit scaler on train only
3. **Val == Train** — never pass same dataset for train and validation
4. **Wrong start_idx** — ensure backtest uses correct price alignment
5. **Fixed threshold** — always optimize threshold on validation

## Output Format

```json
{
  "fold": 1,
  "weights": [0.4, 0.1, 0.5],
  "threshold": 0.3,
  "return_pct": 2.61,
  "drawdown_pct": -2.96,
  "win_rate_pct": 35.8,
  "profit_factor": 1.16
}
```
