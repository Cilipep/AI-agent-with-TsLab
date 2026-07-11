---
name: hybrid-ensemble
description: Combine neural network models (LSTM, Transformer) with sklearn models (XGBoost, CatBoost, LightGBM, RandomForest) into a weighted hybrid ensemble.
---

# Hybrid Ensemble

## When to use
- Need to combine multiple ML model types for better predictions
- User asks for "ensemble", "hybrid", or "combine models"
- Single model type underperforms

## Steps

1. Train N neural network models with different seeds
2. Train M sklearn models on flattened sequences
3. Wrap sklearn models to output logits (pre-sigmoid) for compatibility
4. Combine via weighted average: `logits = Σ(weight_i * model_i(x))`
5. Optimize weights on validation set

## Sklearn Wrapper

```python
class SklearnModelWrapper:
    def __init__(self, model, window, n_features):
        self.model = model
        self.window = window
        self.n_features = n_features

    def __call__(self, x):
        # x: (batch, seq, features) tensor
        x_np = x.detach().cpu().numpy()
        X_flat = x_np.reshape(x_np.shape[0], -1)  # flatten sequences
        proba = self.model.predict_proba(X_flat)[:, 1]
        eps = 1e-7
        proba = np.clip(proba, eps, 1 - eps)
        logits = np.log(proba / (1 - proba))  # convert to logit
        return torch.tensor(logits, dtype=torch.float32).unsqueeze(1)
```

## HybridEnsemble

```python
class HybridEnsemble:
    def __init__(self, neural_models, sklearn_wrappers, weights=None):
        self.all_models = neural_models + sklearn_wrappers
        if weights is None:
            self.weights = [1.0 / len(self.all_models)] * len(self.all_models)
        else:
            total = sum(weights)
            self.weights = [w / total for w in weights]

    def __call__(self, x):
        logits = torch.stack([m(x) for m in self.all_models])
        weights = torch.tensor(self.weights, device=x.device).view(-1, 1, 1)
        return (logits * weights).sum(dim=0)
```

## Key gotchas
- `build_sklearn_models()` returns list of `(name, wrapper)` tuples → must unpack: `[w for _, w in wrappers]`
- Sklearn models need flattened input: `(batch, seq*features)` not `(batch, seq, features)`
- Neural models output raw logits, sklearn outputs probabilities → convert via logit transform
- CPU throttling: set `OMP_NUM_THREADS=2`, `n_jobs=1` for sklearn, `torch.set_num_threads(2)`
- CatBoost uses `thread_count` not `n_jobs`
