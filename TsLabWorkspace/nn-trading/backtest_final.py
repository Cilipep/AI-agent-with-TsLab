"""
Final Optimized Ensemble Backtest
- LSTM + Attention ensemble
- Feature selection (25 features)
- Trained on SOL, tested on all instruments
"""
import pandas as pd
import numpy as np
import torch
from model import LSTMModel, AttentionTransformer
from features_talib import add_talib_indicators, make_label
from sklearn.preprocessing import StandardScaler
import os

# Configuration
WINDOW = 30
HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.3
MODEL_PATH = 'models/final_ensemble.pt'

def load_ensemble():
    """Load trained ensemble from checkpoint."""
    checkpoint = torch.load(MODEL_PATH, weights_only=False, map_location='cpu')
    config = checkpoint['config']
    feat_idx = checkpoint['feature_idx']
    
    # Rebuild models
    lstm = LSTMModel(input_size=25, hidden_size=HIDDEN_SIZE, num_layers=NUM_LAYERS, dropout=DROPOUT)
    lstm.load_state_dict(checkpoint['lstm'])
    lstm.eval()
    
    att = AttentionTransformer(input_size=25, hidden_size=HIDDEN_SIZE, num_layers=NUM_LAYERS, dropout=DROPOUT)
    att.load_state_dict(checkpoint['attention'])
    att.eval()
    
    # Load scaler
    scaler = StandardScaler()
    scaler.mean_ = checkpoint['scaler_mean']
    scaler.scale_ = checkpoint['scaler_scale']
    
    return lstm, att, scaler, feat_idx, config['window']

def predict(lstm, att, scaler, feat_idx, df, window):
    """Generate ensemble predictions for a dataframe."""
    exclude_cols = {'Open', 'High', 'Low', 'Close', 'Volume', 'label'}
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    
    X_all = df[feature_cols].values
    X_sel = X_all[:, feat_idx]
    X_scaled = scaler.transform(X_sel)
    
    preds = []
    for i in range(window, len(X_scaled)):
        x = X_scaled[i-window:i].reshape(1, window, -1)
        with torch.no_grad():
            p1 = torch.sigmoid(lstm(torch.FloatTensor(x))).item()
            p2 = torch.sigmoid(att(torch.FloatTensor(x))).item()
            preds.append((p1 + p2) / 2)
    
    return np.array(preds)

def calculate_metrics(predictions, close_prices, window):
    """Calculate trading metrics from predictions."""
    sigs = (predictions > 0.5).astype(int)
    rets = np.diff(close_prices) / close_prices[:-1]
    strat_ret = sigs[:-1] * rets
    
    total_return = (1 + strat_ret).prod() - 1
    win_rate = (strat_ret > 0).sum() / len(strat_ret) * 100
    max_dd = ((1 + np.cumsum(strat_ret)) / np.maximum.accumulate(1 + np.cumsum(strat_ret)) - 1).min() * 100
    trades = (np.diff(sigs) != 0).sum()
    
    wins = strat_ret[strat_ret > 0]
    losses = strat_ret[strat_ret < 0]
    pf = wins.sum() / abs(losses.sum()) if len(losses) > 0 else 99
    avg_win = wins.mean() * 100 if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) * 100 if len(losses) > 0 else 0
    sharpe = np.mean(strat_ret) / np.std(strat_ret) * np.sqrt(252 * 24 * 4) if np.std(strat_ret) > 0 else 0
    calmar = total_return * 100 / abs(max_dd) if max_dd != 0 else 0
    
    return {
        'return': total_return * 100,
        'win_rate': win_rate,
        'max_dd': max_dd,
        'trades': trades,
        'pf': pf,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'sharpe': sharpe,
        'calmar': calmar
    }

def run_backtest():
    """Run backtest on all instruments."""
    lstm, att, scaler, feat_idx, window = load_ensemble()
    
    symbols = ['SOLUSDT', 'AAVEUSDT', 'XLMUSDT', 'NEARUSDT', 'TRXUSDT', 
               'LINKUSDT', 'SUIUSDT', 'ADAUSDT', 'BCHUSDT', 'UNIUSDT']
    names = ['SOL', 'AAVE', 'XLM', 'NEAR', 'TRX', 'LINK', 'SUI', 'ADA', 'BCH', 'UNI']
    
    print('=' * 90)
    print('FINAL OPTIMIZED ENSEMBLE BACKTEST (LSTM+Attention)')
    print('Feature Selection: 25 | Window: 30 | Trained on SOL')
    print('=' * 90)
    print()
    print('Symbol   Return    Win%    MaxDD   Trades   PF    AvgWin  AvgLoss  Sharpe  Calmar')
    print('-' * 90)
    
    results = []
    for idx, symbol in enumerate(symbols):
        df = pd.read_csv('data/' + symbol + '_15m.csv', index_col=0, parse_dates=True)
        df = add_talib_indicators(df)
        df['label'] = make_label(df, horizon=5, threshold=0.001)
        df = df.dropna()
        
        predictions = predict(lstm, att, scaler, feat_idx, df, window)
        close = df['Close'].values[window:]
        
        metrics = calculate_metrics(predictions, close, window)
        metrics['symbol'] = names[idx]
        results.append(metrics)
        
        print(names[idx].ljust(8) + 
              ('{:+.2f}%'.format(metrics['return'])).rjust(10) +
              ('{:.1f}%'.format(metrics['win_rate'])).rjust(7) +
              ('{:.2f}%'.format(metrics['max_dd'])).rjust(9) +
              str(metrics['trades']).rjust(7) +
              ('{:.2f}'.format(metrics['pf'])).rjust(7) +
              ('{:.2f}%'.format(metrics['avg_win'])).rjust(8) +
              ('{:.2f}%'.format(metrics['avg_loss'])).rjust(8) +
              ('{:.2f}'.format(metrics['sharpe'])).rjust(8) +
              ('{:.2f}'.format(metrics['calmar'])).rjust(8))
    
    print('-' * 90)
    
    # Summary
    avg_return = np.mean([r['return'] for r in results])
    avg_win_rate = np.mean([r['win_rate'] for r in results])
    total_trades = sum([r['trades'] for r in results])
    profitable = sum(1 for r in results if r['return'] > 0)
    
    print('Average'.ljust(8) + 
          ('{:+.2f}%'.format(avg_return)).rjust(10) +
          ('{:.1f}%'.format(avg_win_rate)).rjust(7) +
          str(total_trades).rjust(26))
    print()
    print(f'Profitable instruments: {profitable}/{len(results)}')
    
    best = max(results, key=lambda x: x['return'])
    worst = min(results, key=lambda x: x['return'])
    print(f'Best: {best["symbol"]} ({best["return"]:+.2f}%, Sharpe {best["sharpe"]:.2f})')
    print(f'Worst: {worst["symbol"]} ({worst["return"]:+.2f}%, Sharpe {worst["sharpe"]:.2f})')
    print('=' * 90)
    
    return results

if __name__ == '__main__':
    results = run_backtest()
