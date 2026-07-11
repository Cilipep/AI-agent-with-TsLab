"""Enhanced backtest with trailing stop, dynamic sizing, transaction costs, and risk metrics."""
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader


def calculate_sharpe(equity, risk_free_rate=0.0, periods_per_year=365):
    """Calculate annualized Sharpe ratio."""
    returns = np.diff(equity) / equity[:-1]
    if len(returns) < 2 or np.std(returns) == 0:
        return 0.0
    excess_returns = returns - risk_free_rate / periods_per_year
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(periods_per_year)


def calculate_sortino(equity, risk_free_rate=0.0, periods_per_year=365):
    """Calculate annualized Sortino ratio (penalizes only downside volatility)."""
    returns = np.diff(equity) / equity[:-1]
    if len(returns) < 2:
        return 0.0
    excess_returns = returns - risk_free_rate / periods_per_year
    downside_returns = excess_returns[excess_returns < 0]
    if len(downside_returns) == 0 or np.std(downside_returns) == 0:
        return float("inf") if np.mean(excess_returns) > 0 else 0.0
    return np.mean(excess_returns) / np.std(downside_returns) * np.sqrt(periods_per_year)


def calculate_calmar(equity):
    """Calculate Calmar ratio (return / max drawdown)."""
    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100
    if max_dd == 0:
        return float("inf") if total_return > 0 else 0.0
    return total_return / abs(max_dd)


def run_backtest_v2(model, dataset, df: pd.DataFrame, config, device,
                    threshold: float = 0.5, use_trailing_stop: bool = True,
                    trailing_stop_pct: float = 0.02, use_dynamic_sizing: bool = True,
                    start_idx: int = None,
                    commission_pct: float = 0.001,  # 0.1% taker fee
                    slippage_pct: float = 0.0005,    # 0.05% slippage
                    spread_pct: float = 0.0005):     # 0.05% spread (liquid pairs)
    """
    Enhanced backtest with trailing stop, dynamic sizing, and transaction costs.

    Args:
        use_trailing_stop: Enable trailing stop loss
        trailing_stop_pct: Trailing stop distance from highest price
        use_dynamic_sizing: Enable dynamic position sizing based on volatility
        start_idx: Starting index in df for price alignment (default: config.window)
        commission_pct: Exchange commission (0.1% = 0.001)
        slippage_pct: Slippage (0.05% = 0.0005)
        spread_pct: Spread for liquid pairs (0.05% = 0.0005)
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
    # Short signals: prob > threshold → long, prob < (1-threshold) → short
    predictions = np.where(probs > threshold, 1, np.where(probs < (1 - threshold), -1, 0))

    if start_idx is None:
        start_idx = config.window
    preds = np.array(predictions)
    prices = df["Close"].values[start_idx : start_idx + len(preds)].copy()
    highs = df["High"].values[start_idx : start_idx + len(preds)].copy()
    lows = df["Low"].values[start_idx : start_idx + len(preds)].copy()

    # Calculate ATR for dynamic sizing
    if use_dynamic_sizing and "atr" in df.columns:
        atr = df["atr"].values[start_idx : start_idx + len(preds)].copy()
    else:
        atr = np.full(len(preds), np.mean(prices) * 0.02)  # Default 2%

    stop_loss = config.stop_loss_pct
    take_profit = config.take_profit_pct
    risk_per_trade = config.risk_per_trade

    # Total transaction cost per trade (entry + exit)
    total_cost_pct = commission_pct * 2 + slippage_pct * 2 + spread_pct

    # Simulation with long + short support
    equity = [1.0]
    position = 0  # 0=flat, 1=long, -1=short
    entry_price = 0
    position_size = 0
    stop_price = 0
    tp_price = 0
    trailing_ref = 0  # highest for long, lowest for short
    trades = []

    for i in range(len(preds) - 1):
        current_equity = equity[-1]
        signal = preds[i]

        if position == 0:
            # Open new position
            if signal == 1:  # LONG
                position = 1
                entry_price = prices[i]
                trailing_ref = prices[i]
                if use_dynamic_sizing:
                    vol = atr[i] / prices[i] if prices[i] > 0 else 0.02
                    size_mult = min(1.0, 0.02 / max(vol, 0.01))
                    position_size = (current_equity * risk_per_trade * size_mult) / stop_loss
                else:
                    position_size = (current_equity * risk_per_trade) / stop_loss
                stop_price = entry_price * (1 - stop_loss)
                tp_price = entry_price * (1 + take_profit)

            elif signal == -1:  # SHORT
                position = -1
                entry_price = prices[i]
                trailing_ref = prices[i]
                if use_dynamic_sizing:
                    vol = atr[i] / prices[i] if prices[i] > 0 else 0.02
                    size_mult = min(1.0, 0.02 / max(vol, 0.01))
                    position_size = (current_equity * risk_per_trade * size_mult) / stop_loss
                else:
                    position_size = (current_equity * risk_per_trade) / stop_loss
                stop_price = entry_price * (1 + stop_loss)   # short stop is ABOVE entry
                tp_price = entry_price * (1 - take_profit)   # short TP is BELOW entry

        else:
            # Manage open position
            if position == 1:  # LONG
                trailing_ref = max(trailing_ref, prices[i])
                if use_trailing_stop:
                    ts = trailing_ref * (1 - trailing_stop_pct)
                    stop_price = max(stop_price, ts)
                hit_sl = lows[i] <= stop_price
                hit_tp = highs[i] >= tp_price
                exit_price = None
                reason = None
                if hit_sl:
                    exit_price = stop_price; reason = "TS" if stop_price > entry_price * (1 - stop_loss) else "SL"
                elif hit_tp:
                    exit_price = tp_price; reason = "TP"
                elif signal != 1:
                    exit_price = prices[i]; reason = "SIG"
                if exit_price is not None:
                    pnl = (exit_price - entry_price) / entry_price - total_cost_pct
                    equity.append(current_equity + position_size * pnl)
                    trades.append({"entry": entry_price, "exit": exit_price, "pnl": pnl, "side": "long", "reason": reason})
                    position = 0

            elif position == -1:  # SHORT
                trailing_ref = min(trailing_ref, prices[i])
                if use_trailing_stop:
                    ts = trailing_ref * (1 + trailing_stop_pct)
                    stop_price = min(stop_price, ts)
                hit_sl = highs[i] >= stop_price
                hit_tp = lows[i] <= tp_price
                exit_price = None
                reason = None
                if hit_sl:
                    exit_price = stop_price; reason = "TS" if stop_price < entry_price * (1 + stop_loss) else "SL"
                elif hit_tp:
                    exit_price = tp_price; reason = "TP"
                elif signal != -1:
                    exit_price = prices[i]; reason = "SIG"
                if exit_price is not None:
                    pnl = (entry_price - exit_price) / entry_price - total_cost_pct  # short profit
                    equity.append(current_equity + position_size * pnl)
                    trades.append({"entry": entry_price, "exit": exit_price, "pnl": pnl, "side": "short", "reason": reason})
                    position = 0

        if equity[-1] == current_equity and position != 0:
            equity.append(current_equity)

    # Close open position at end
    if position == 1:
        pnl = (prices[-1] - entry_price) / entry_price - total_cost_pct
        equity.append(equity[-1] + position_size * pnl)
        trades.append({"entry": entry_price, "exit": prices[-1], "pnl": pnl, "side": "long", "reason": "END"})
    elif position == -1:
        pnl = (entry_price - prices[-1]) / entry_price - total_cost_pct
        equity.append(equity[-1] + position_size * pnl)
        trades.append({"entry": entry_price, "exit": prices[-1], "pnl": pnl, "side": "short", "reason": "END"})

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

    # Risk metrics
    sharpe = calculate_sharpe(equity)
    sortino = calculate_sortino(equity)
    calmar = calculate_calmar(equity)

    return {
        "equity": equity,
        "trades": trades_df,
        "total_return_pct": total_return,
        "max_drawdown_pct": max_dd,
        "n_trades": n_trades,
        "win_rate_pct": win_rate,
        "profit_factor": profit_factor,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "calmar_ratio": calmar,
        "total_cost_pct": total_cost_pct * 100,
    }


def run_backtest_original(model, dataset, df: pd.DataFrame, config, device,
                          threshold: float = 0.5):
    """Original backtest for comparison."""
    model.eval()
    loader = DataLoader(dataset, batch_size=256, shuffle=False)

    probs = []
    with torch.no_grad():
        for x, _ in loader:
            x = x.to(device)
            prob = torch.sigmoid(model(x)).cpu().numpy().flatten()
            probs.extend(prob)

    probs = np.array(probs)
    # Short signals: prob > threshold → long, prob < (1-threshold) → short
    predictions = np.where(probs > threshold, 1, np.where(probs < (1 - threshold), -1, 0))

    start_idx = config.window
    preds = np.array(predictions[:len(df) - start_idx])
    prices = df["Close"].values[start_idx : start_idx + len(preds)].copy()
    highs = df["High"].values[start_idx : start_idx + len(preds)].copy()
    lows = df["Low"].values[start_idx : start_idx + len(preds)].copy()

    stop_loss = config.stop_loss_pct
    take_profit = config.take_profit_pct
    risk_per_trade = config.risk_per_trade

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
