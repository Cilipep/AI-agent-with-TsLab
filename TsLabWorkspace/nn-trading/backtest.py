"""Backtest with risk management: stop-loss, take-profit, position sizing."""
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader


def run_backtest(model, dataset, df: pd.DataFrame, config, device,
                 threshold: float = 0.5):
    """
    Backtest with risk management.

    Uses config.stop_loss_pct, config.take_profit_pct, config.risk_per_trade.
    """
    model.eval()
    loader = DataLoader(dataset, batch_size=256, shuffle=False)

    probs = []
    with torch.no_grad():
        for x, _ in loader:
            x = x.to(device)
            prob = torch.sigmoid(model(x)).cpu().numpy().flatten()
            probs.extend(prob)

    probs = np.array(probs)
    predictions = (probs > threshold).astype(int)

    start_idx = config.window
    preds = np.array(predictions[:len(df) - start_idx])
    prices = df["Close"].values[start_idx : start_idx + len(preds)].copy()
    highs = df["High"].values[start_idx : start_idx + len(preds)].copy()
    lows = df["Low"].values[start_idx : start_idx + len(preds)].copy()

    stop_loss = config.stop_loss_pct
    take_profit = config.take_profit_pct
    risk_per_trade = config.risk_per_trade

    # Simulation with risk management
    equity = [1.0]
    position = 0
    entry_price = 0
    position_size = 0
    stop_price = 0
    tp_price = 0
    trades = []

    for i in range(len(preds) - 1):
        current_equity = equity[-1]

        if position == 0:
            if preds[i] == 1:
                position = 1
                entry_price = prices[i]
                position_size = (current_equity * risk_per_trade) / stop_loss
                stop_price = entry_price * (1 - stop_loss)
                tp_price = entry_price * (1 + take_profit)
        else:
            hit_sl = lows[i] <= stop_price
            hit_tp = highs[i] >= tp_price

            if hit_sl:
                pnl = (stop_price - entry_price) / entry_price
                equity.append(current_equity + position_size * pnl)
                trades.append({"entry": entry_price, "exit": stop_price, "pnl": pnl, "reason": "SL"})
                position = 0
            elif hit_tp:
                pnl = (tp_price - entry_price) / entry_price
                equity.append(current_equity + position_size * pnl)
                trades.append({"entry": entry_price, "exit": tp_price, "pnl": pnl, "reason": "TP"})
                position = 0
            elif preds[i] == 0:
                pnl = (prices[i] - entry_price) / entry_price
                equity.append(current_equity + position_size * pnl)
                trades.append({"entry": entry_price, "exit": prices[i], "pnl": pnl, "reason": "SIG"})
                position = 0
            else:
                equity.append(current_equity)

    if position == 1:
        pnl = (prices[-1] - entry_price) / entry_price
        equity.append(equity[-1] + position_size * pnl)
        trades.append({"entry": entry_price, "exit": prices[-1], "pnl": pnl, "reason": "END"})

    equity = np.array(equity)
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()

    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100
    n_trades = len(trades)
    win_rate = (trades_df["pnl"] > 0).mean() * 100 if n_trades > 0 else 0
    profit_factor = (
        trades_df[trades_df["pnl"] > 0]["pnl"].sum() /
        abs(trades_df[trades_df["pnl"] < 0]["pnl"].sum())
        if n_trades > 0 and (trades_df["pnl"] < 0).any() else float("inf")
    )

    return {
        "equity": equity,
        "trades": trades_df,
        "total_return_pct": total_return,
        "max_drawdown_pct": max_dd,
        "n_trades": n_trades,
        "win_rate_pct": win_rate,
        "profit_factor": profit_factor,
    }
