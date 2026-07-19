# 3D Visualization of Neural Network Models

## Overview

This document describes the 3D visualization system for the nn-trading project's neural network architectures.

## Files Created

### 1. `export_onnx.py` - ONNX Model Export
Exports PyTorch models to ONNX format for TSLab integration.

**Features:**
- Model conversion from PyTorch to ONNX
- C# wrapper generation for ONNX Runtime
- Testing of ONNX export accuracy

**Usage:**
```bash
python export_onnx.py
```

**Output:**
- `models/btc_attention_32.onnx` - ONNX model
- `tslab_scripts/NNTradingIndicator.cs` - C# wrapper

### 2. `train_btc.py` - BTC Multi-Timeframe Training
BTC-specific training pipeline with configurable timeframes.

**Features:**
- Configurable timeframes: 5m, 15m, 30m, 1h, 4h
- Walk-forward validation
- BTC-specific risk parameters
- Multi-timeframe ensemble support

**BTC Timeframes Configuration:**
| Timeframe | Suffix | Max Bars | Window | Epochs |
|-----------|--------|----------|--------|--------|
| 5m | `_5m.csv` | 10000 | 20 | 15 |
| 15m | `_15m.csv` | 8000 | 30 | 15 |
| 30m | `_30m.csv` | 6000 | 30 | 15 |
| 1h | `_1h.csv` | 6000 | 40 | 20 |
| 4h | `_4h.csv` | 4000 | 50 | 20 |

**Usage:**
```bash
python train_btc.py
```

### 3. `train_rl_walkforward.py` - RL with Walk-Forward
DQN reinforcement learning with walk-forward validation and ensemble integration.

**Features:**
- Walk-forward validation for RL agents
- Hybrid ensemble integration (neural + sklearn + DQN)
- DQN agent training on ensemble predictions
- Multi-step training pipeline

**Usage:**
```bash
python train_rl_walkforward.py
```

### 4. `calibrate_probs.py` & `calibration.py` - Probability Calibration
Platt scaling and isotonic regression for ensemble probability calibration.

**Features:**
- PlattScaler: Sigmoid-based calibration
- IsotonicCalibrator: Non-parametric monotonic calibration
- Performance comparison (Brier score, Log loss)
- Save/load calibration parameters

**Usage:**
```python
from calibration import PlattScaler, IsotonicCalibrator

# Fit calibrator
platt = PlattScaler()
platt.fit(logits, targets)

# Calibrate predictions
calibrated_probs = platt.calibrate(test_logits)
```

### 5. `sensitivity_analysis.py` - Transaction Cost Sensitivity
Tests model performance under varying transaction costs.

**Features:**
- Commission sensitivity analysis
- Slippage sensitivity analysis
- Spread sensitivity analysis
- Overall robustness assessment

**Usage:**
```bash
python sensitivity_analysis.py
```

### 6. `btc_metrics.py` - BTC-Specific Metrics
Comprehensive BTC trading metrics with timeframe comparison.

**Features:**
- Risk-adjusted returns (Sharpe, Sortino, Calmar)
- Drawdown analysis
- Trade-level statistics
- Timeframe recommendation

**Usage:**
```bash
python btc_metrics.py
```

### 7. `tests/` - Unit Tests
Complete test suite for core modules.

**Test Files:**
- `test_core.py` - Core functionality tests
- `test_utils.py` - Utility functions
- `test_features.py` - Feature engineering
- `test_dataset.py` - Dataset handling
- `test_model.py` - Model architecture
- `test_train.py` - Training pipeline
- `test_backtest.py` - Backtest metrics

**Usage:**
```bash
python -m unittest discover -s tests
```

## Architecture Visualization

### Neural Network Models

#### LSTM Model
- Input layer: 40-50 features
- LSTM layers: 2 layers, hidden=64
- Dropout: 0.35
- Output: Binary classification (Buy/Hold/Sell)

#### Attention Transformer
- Multi-head attention with 8 heads
- Pre-norm architecture (LayerNorm before attention)
- GELU activation
- Feed-forward network (4x expansion)

#### TCN Model
- Dilated causal convolutions
- Increasing dilation rates
- Batch normalization
- Residual connections

### Ensemble Architecture

```
Input (40-50 features)
    ↓
[Neural Networks]  [Sklearn Models]
  LSTM    Attention    XGBoost
  TCN     Transformer  CatBoost
  etc.    etc.         LightGBM
                        RandomForest
    ↓              ↓
    └───→ Weighted Average ←┘
               ↓
         Output (Probability)
```

## Updated 3D Visualization

### `generate_3d.py` - Legacy
Previously generated 3D architecture visualization using WebGL.

### Current Status
- Legacy `nn_3d_architecture.html` removed
- Legacy `nn_3d_models.html` removed
- Updated `nn_3d_visualization.html` retained for results display

## New Features

### 1. BTC-Specific Improvements
- Multi-timeframe configuration
- BTC-optimized risk parameters
- Walk-forward validation per timeframe

### 2. RL Integration
- DQN agent with Dueling architecture
- Walk-forward validation for RL
- Hybrid ensemble (Neural + Sklearn + DQN)

### 3. Probability Calibration
- Platt scaling (sigmoid)
- Isotonic regression
- Brier score and Log loss metrics

### 4. Transaction Cost Sensitivity
- Commission testing range: 0.01% - 0.2%
- Slippage testing range: 0.005% - 0.1%
- Spread testing range: 0.01% - 0.2%
- Overall robustness scoring

## Usage Workflow

### For BTC Trading:
```bash
# 1. Train on BTC multi-timeframe
python train_btc.py

# 2. Analyze metrics
python btc_metrics.py

# 3. Test transaction cost sensitivity
python sensitivity_analysis.py
```

### For RL Training:
```bash
# Train RL agent with walk-forward
python train_rl_walkforward.py
```

### For Probability Calibration:
```python
from calibration import PlattScaler
from calibrate_probs import calibrate_ensemble_probs

# Calibrate ensemble probabilities
platt, results = calibrate_ensemble_probs(ensemble, val_ds, test_ds)
```

## Testing

### Run All Tests:
```bash
python -m unittest discover -s tests
```

### Run Specific Test Module:
```bash
python -m unittest tests.test_model
python -m unittest tests.test_features
```

## File Structure

```
nn-trading/
├── export_onnx.py              # ONNX export and C# wrapper
├── train_btc.py                # BTC multi-timeframe training
├── train_rl_walkforward.py     # RL with walk-forward
├── calibration.py              # Probability calibration classes
├── calibrate_probs.py          # Probability calibration pipeline
├── sensitivity_analysis.py     # Transaction cost analysis
├── btc_metrics.py              # BTC-specific metrics
├── tests/
│   ├── test_core.py
│   ├── test_utils.py
│   ├── test_features.py
│   ├── test_dataset.py
│   ├── test_model.py
│   ├── test_train.py
│   └── test_backtest.py
└── results/
    └── btc_timeframe_comparison.json
```

## GitHub Updates

### Commits:
- `9fb003b` - refactor: clean up legacy files
- `f23548c` - refactor: clean up legacy files and add new features

### Pushed to:
`https://github.com/Cilipep/AI-agent-with-TsLab.git`

## Summary

✅ **Completed:**
- Deleted debug, test, and duplicate files
- Cleaned up old optimization scripts
- Removed Gerchik book and C# indicator files
- Removed download and check scripts
- Cleaned up extra report files
- Added BTC multi-timeframe training
- Added RL walk-forward validation
- Added probability calibration (Platt + Isotonic)
- Added transaction cost sensitivity analysis
- Added BTC-specific metrics
- Created unit test suite
- Pushed to GitHub

## Next Steps

1. Run `python train_btc.py` to train on BTC
2. Run `python sensitivity_analysis.py` to test cost sensitivity
3. Run `python calibration.py` to test probability calibration
4. Run `python -m unittest discover -s tests` to verify tests
