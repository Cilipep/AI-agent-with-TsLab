"""Run walk-forward directly with best params from optimization."""
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import torch
torch.set_num_threads(2)

import json
import pandas as pd
import numpy as np
from config import Config
from features import prepare_features
from dataset import auto_select_features
from walk_forward import walk_forward


instruments = [
    ("BTC-USD", "Bitcoin"),
    ("ETH-USD", "Ethereum"),
    ("SOL-USD", "Solana"),
]

all_results = []

for symbol, name in instruments:
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    df = pd.read_csv(f"data/binance_{symbol.replace('/', '-')}_1d.csv", index_col=0, parse_dates=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    cfg = Config()
    # Use params from optimization
    cfg.hidden_size = 32
    cfg.num_layers = 2
    cfg.dropout = 0.35
    cfg.window = 30
    cfg.batch_size = 64
    cfg.learning_rate = 0.0002
    cfg.n_models = 3
    cfg.max_features = 40
    cfg.stop_loss_pct = 0.03
    cfg.take_profit_pct = 0.07
    cfg.n_cpu_threads = 2

    df = prepare_features(df, cfg)

    equity, results = walk_forward(df, cfg, "cpu", n_folds=5)

    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100
    total_trades = sum(r.n_trades for r in results)
    avg_win = np.mean([r.win_rate for r in results])

    all_results.append({
        "instrument": name,
        "total_return": round(total_return, 2),
        "max_drawdown": round(max_dd, 2),
        "total_trades": total_trades,
        "avg_win_rate": round(avg_win, 1),
        "folds": len(results),
    })

print("\n" + "=" * 60)
print("FINAL RESULTS (HybridEnsemble: 3 LSTM + 4 sklearn)")
print("=" * 60)

for r in all_results:
    print(f"\n{r['instrument']}:")
    print(f"  Return:    {r['total_return']:+.2f}%")
    print(f"  Drawdown:  {r['max_drawdown']:.2f}%")
    print(f"  Trades:    {r['total_trades']}")
    print(f"  Win Rate:  {r['avg_win_rate']:.1f}%")

if all_results:
    avg_ret = np.mean([r['total_return'] for r in all_results])
    avg_dd = np.mean([r['max_drawdown'] for r in all_results])
    print(f"\nPortfolio Average:")
    print(f"  Avg Return:   {avg_ret:+.2f}%")
    print(f"  Avg Drawdown: {avg_dd:.2f}%")

with open("results/walk_forward_v2_results.json", "w") as f:
    json.dump({"instruments": all_results}, f, indent=2)

print(f"\nSaved to results/walk_forward_v2_results.json")
