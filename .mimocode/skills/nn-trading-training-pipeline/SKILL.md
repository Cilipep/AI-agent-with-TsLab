---
name: nn-trading-training-pipeline
description: Complete Python training pipeline for NN Trading models: download Binance data, compute indicators, auto-select features, train AttentionTransformer, export to ONNX with metadata + scaler. Use when user asks to train a trading model, export to ONNX, or create a training pipeline.
---

# NN Trading Training Pipeline

Complete pipeline for training neural network trading models and exporting to ONNX for TSLab integration.

## When to use
- User asks to "train model", "export to ONNX", "create training pipeline"
- Need to train on specific symbol/interval with custom parameters
- Want to export trained model for TSLab C# indicator use

## Prerequisites
- Python packages: `torch`, `talib`, `requests`, `scikit-learn`, `numpy`, `pandas`
- Binance API access (public, no key needed for klines)

## Usage

### Basic training
```bash
python train_and_export.py --symbol BTCUSDT --interval 1d --epochs 50
```

### Custom parameters
```bash
python train_and_export.py --symbol ETHUSDT --interval 1h --epochs 30 --window 60 --hidden 128 --layers 3 --max-features 50
```

### All parameters
```
--symbol        Binance symbol (default: BTCUSDT)
--interval      Kline interval: 1m,5m,15m,1h,4h,1d (default: 1d)
--days          Days of history (default: 1820)
--epochs        Training epochs (default: 50)
--window        Lookback window (default: 30)
--hidden        Hidden size (default: 64)
--layers        Number of transformer layers (default: 2)
--dropout       Dropout rate (default: 0.35)
--lr            Learning rate (default: 0.001)
--max-features  Max features to auto-select (default: 40)
--output-dir    Output directory (default: models)
```

## Pipeline Steps

### 1. Download data from Binance
- Uses public API: `https://api.binance.com/api/v3/klines`
- Automatic pagination for large datasets
- Rate limiting: 0.25s between requests

### 2. Compute features (50+ indicators)
- Trend: EMA(10,20,50), SMA(20), ADX, MACD
- Momentum: RSI(14,7), Stochastic, Williams %R, CCI, ROC
- Volatility: Bollinger Bands, ATR, NATR
- Volume: OBV, MFI
- Multi-timeframe: returns(3,5,10,20)
- Price relative to MAs: pvs_ema10, pvs_ema20, pvs_ema50

### 3. Auto-select features
- Random Forest importance + Mutual Information
- Combined score: `(rf_norm + mi_norm) / 2`
- Returns top N features (default: 40)

### 4. Train AttentionTransformer
- Architecture: Input → Projection → PositionalEncoding → N × TransformerEncoderLayer → FC head
- Training: AdamW + CosineAnnealingLR + EarlyStopping
- Split: 70/15/15 (train/val/test)
- Scaler: fitted on train only (no data leak)

### 5. Export to ONNX
- Dynamic axes for batch size flexibility
- Opset 18 (latest stable)
- Input: `[batch, window, features]`
- Output: `[batch, 1]` (prediction score)

### 6. Save metadata + scaler
- `{symbol}_{interval}_metadata.json` - model config, features, accuracy
- `{symbol}_{interval}_scaler.pkl` - StandardScaler for TSLab integration

## Output Files
```
models/
  BTCUSDT_1d.onnx           # ONNX model (166 KB)
  BTCUSDT_1d_metadata.json  # Model metadata
  BTCUSDT_1d_scaler.pkl     # Scaler for inference
```

## Model Architecture
```
AttentionTransformer(
  input_proj: Linear → LayerNorm → GELU → Dropout
  pos_enc: PositionalEncoding
  blocks: N × TransformerEncoderLayer(d_model=64, nhead=8, dim_ff=256)
  head: Linear → LayerNorm → GELU → Dropout → Linear(1)
)
```

## Results (trained on 1820 days daily data)
| Symbol | Accuracy | Features | Window |
|--------|----------|----------|--------|
| BTCUSDT | 65.48% | 31 | 30 |
| ETHUSDT | 66.74% | 40 | 30 |
| SOLUSDT | 67.55% | 40 | 30 |

## TSLab Integration
1. Export model: `python train_and_export.py --symbol BTCUSDT`
2. Copy ONNX to TSLab models directory
3. Use `NNFormulaIndicator.cs` (works without ONNX Runtime)
4. Or wait for ONNX Runtime compatibility fix in TSLab

## Files
- `train_and_export.py` - Main training script
- `models/*.onnx` - Exported ONNX models
- `models/*_metadata.json` - Model metadata
- `models/*_scaler.pkl` - Scalers

## Notes
- **CPU throttling**: Set `OMP_NUM_THREADS=2`, `MKL_NUM_THREADS=2`
- **ONNX Runtime**: Not compatible with TSLab .NET 10 (DLL conflicts)
- **Feature selection**: Uses RF importance + MI combined score
- **Scaler leak prevention**: Scaler fitted on train data only
