# Skill: NN Threshold Optimization

## When to use
- Optimizing prediction thresholds for neural network trading models
- Grid search over threshold values (0.3-0.7)
- Finding optimal threshold per instrument

## Workflow

### 1. Load trained ensemble model
```python
checkpoint = torch.load(f'models/{symbol}_ensemble.pt', weights_only=False)
lstm = LSTMModel(input_size=25, hidden_size=64, num_layers=2, dropout=0.3)
lstm.load_state_dict(checkpoint['lstm'])
att = AttentionTransformer(input_size=25, hidden_size=64, num_layers=2, dropout=0.3)
att.load_state_dict(checkpoint['attention'])
```

### 2. Grid search thresholds
```python
for thresh in [0.3, 0.4, 0.5, 0.6, 0.7]:
    preds = []
    for i in range(window, len(X_val)):
        x = X_val[i-window:i].reshape(1, window, -1)
        with torch.no_grad():
            p1 = torch.sigmoid(lstm(torch.FloatTensor(x))).item()
            p2 = torch.sigmoid(att(torch.FloatTensor(x))).item()
            preds.append((p1 + p2) / 2)
    
    preds = np.array(preds)
    sigs = (preds > thresh).astype(int)
    rets = np.diff(close) / close[:-1]
    sr = sigs[:-1] * rets
    tr = (1+sr).prod()-1
    print(f'Threshold {thresh}: Return={tr*100:+.2f}%')
```

### 3. Select best threshold
- Pick threshold with highest return
- Verify not overfitting (check validation set)

## Results Pattern
- BTC: 0.3 (conservative)
- ETH, SOL, XLM, AAVE, ADA, NEAR: 0.5 (balanced)
- LINK: 0.6 (aggressive)
- UNI, AVAX: 0.4 (moderate)

## Files
- models/*_ensemble.pt - Trained models
- data/*_15m.csv - Historical data
