# Skill: NN Per-Instrument Training

## When to use
- Training separate neural network models for each trading instrument
- Feature selection with mutual information
- LSTM + Attention ensemble training

## Workflow

### 1. Load and prepare data
```python
df = pd.read_csv(f'data/{symbol}_15m.csv', index_col=0, parse_dates=True)
df = add_talib_indicators(df)
df['label'] = make_label(df, horizon=5, threshold=0.001)
df = df.dropna()
```

### 2. Feature selection (25 from 55)
```python
from sklearn.feature_selection import mutual_info_classif

exclude_cols = {'Open', 'High', 'Low', 'Close', 'Volume', 'label'}
feature_cols = [c for c in df.columns if c not in exclude_cols]
X_all = df[feature_cols].values
y_all = df['label'].values

mi = mutual_info_classif(X_all, y_all, random_state=42)
feat_idx = np.argsort(mi)[-25:]
X_sel = X_all[:, feat_idx]
```

### 3. Train LSTM + Attention ensemble
```python
# Split 70/30
split = int(len(X_sel) * 0.7)
X_train, X_val = X_sel[:split], X_sel[split:]
y_train, y_val = y_all[:split], y_all[split:]

# Scale
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)

# Train LSTM
lstm = LSTMModel(input_size=25, hidden_size=64, num_layers=2, dropout=0.3)
opt = torch.optim.AdamW(lstm.parameters(), lr=0.001, weight_decay=0.01)
crit = nn.BCEWithLogitsLoss()

for epoch in range(15):
    # Training loop with gradient clipping
    pass

# Train Attention
att = AttentionTransformer(input_size=25, hidden_size=64, num_layers=2, dropout=0.3)
# Similar training loop

# Save
torch.save({
    'lstm': lstm.state_dict(),
    'attention': att.state_dict(),
    'scaler_mean': scaler.mean_,
    'scaler_scale': scaler.scale_,
    'feature_idx': feat_idx.tolist(),
    'config': {'input_size': 25, 'hidden_size': 64, 'num_layers': 2, 'dropout': 0.3, 'window': window}
}, f'models/{symbol.lower()}_ensemble.pt')
```

## Key Parameters
- Window: 30
- Hidden: 64
- Layers: 2
- Dropout: 0.3
- Features: 25
- Epochs: 15
- LR: 0.001
- Weight Decay: 0.01

## Files
- model.py - LSTM, AttentionTransformer classes
- features_talib.py - TA-Lib indicators
- models/*_ensemble.pt - Trained models
