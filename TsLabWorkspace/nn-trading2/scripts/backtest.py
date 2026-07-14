import numpy as np
import pandas as pd
import torch


def calculate_sharpe(equity, periods_per_year=365*24):
    returns = np.diff(equity) / equity[:-1]
    if len(returns) < 2 or np.std(returns) < 1e-10:
        return 0.0
    return np.mean(returns) / np.std(returns) * np.sqrt(periods_per_year)


def calculate_sortino(equity, periods_per_year=365*24):
    returns = np.diff(equity) / equity[:-1]
    if len(returns) < 2:
        return 0.0
    downside = returns[returns < 0]
    if len(downside) < 1 or np.std(downside) < 1e-10:
        return 0.0
    return np.mean(returns) / np.std(downside) * np.sqrt(periods_per_year)


def calculate_calmar(equity):
    if len(equity) < 2:
        return 0.0
    total_return = equity[-1] / equity[0] - 1
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min()
    if abs(max_dd) < 1e-10:
        return 0.0
    return total_return / abs(max_dd)


def run_backtest(model, test_ds, df, cfg, device="cpu", threshold=0.5,
                 use_trailing_stop=True, trailing_stop_pct=0.015,
                 use_dynamic_sizing=True, start_idx=0):
    model.eval()
    equity = [1.0]
    trades = []
    position = None
    peak_price = None

    for i in range(len(test_ds)):
        x, y = test_ds[i]
        x = x.unsqueeze(0).to(device)

        with torch.no_grad():
            pred = torch.sigmoid(model(x)).item()

        bar_idx = start_idx + cfg.window + i
        if bar_idx >= len(df):
            break

        price = df.iloc[bar_idx]['close']
        high = df.iloc[bar_idx]['high']
        low = df.iloc[bar_idx]['low']

        # Check stop loss / take profit
        if position is not None:
            hit_sl = False
            hit_tp = False

            if position['side'] == 'long':
                if low <= position['stop_loss']:
                    hit_sl = True
                    exit_price = position['stop_loss']
                elif high >= position['take_profit']:
                    hit_tp = True
                    exit_price = position['take_profit']
                elif use_trailing_stop:
                    if peak_price is None or high > peak_price:
                        peak_price = high
                    new_sl = peak_price * (1 - trailing_stop_pct)
                    if new_sl > position['stop_loss']:
                        position['stop_loss'] = new_sl
            else:
                if high >= position['stop_loss']:
                    hit_sl = True
                    exit_price = position['stop_loss']
                elif low <= position['take_profit']:
                    hit_tp = True
                    exit_price = position['take_profit']
                elif use_trailing_stop:
                    if peak_price is None or low < peak_price:
                        peak_price = low
                    new_sl = peak_price * (1 + trailing_stop_pct)
                    if new_sl < position['stop_loss']:
                        position['stop_loss'] = new_sl

            if hit_sl or hit_tp:
                if position['side'] == 'long':
                    pnl = (exit_price / position['entry'] - 1) * position['size']
                else:
                    pnl = (1 - exit_price / position['entry']) * position['size']
                pnl -= abs(pnl) * cfg.commission_pct

                equity.append(equity[-1] * (1 + pnl))
                trades.append({
                    'side': position['side'],
                    'entry': position['entry'],
                    'exit': exit_price,
                    'pnl': pnl,
                    'reason': 'stop_loss' if hit_sl else 'take_profit'
                })
                position = None
                peak_price = None
                continue

        # Generate signal
        signal = None
        if pred > threshold:
            signal = 'long'
        elif pred < (1 - threshold):
            signal = 'short'

        # Open position
        if signal and position is None:
            risk_pct = cfg.risk_per_trade if use_dynamic_sizing else 0.02
            size = risk_pct

            sl_pct = cfg.stop_loss_pct
            tp_pct = cfg.take_profit_pct

            if signal == 'long':
                sl = price * (1 - sl_pct)
                tp = price * (1 + tp_pct)
            else:
                sl = price * (1 + sl_pct)
                tp = price * (1 - tp_pct)

            position = {
                'side': signal,
                'entry': price,
                'size': size,
                'stop_loss': sl,
                'take_profit': tp,
            }
            peak_price = price

        # Record equity
        unrealized = 0
        if position:
            if position['side'] == 'long':
                unrealized = (price / position['entry'] - 1) * position['size']
            else:
                unrealized = (1 - price / position['entry']) * position['size']
        equity.append(equity[-1] * (1 + unrealized * 0.01))

    # Close open position
    if position:
        final_price = df.iloc[min(start_idx + cfg.window + len(test_ds) - 1, len(df) - 1)]['close']
        if position['side'] == 'long':
            pnl = (final_price / position['entry'] - 1) * position['size']
        else:
            pnl = (1 - final_price / position['entry']) * position['size']
        pnl -= abs(pnl) * cfg.commission_pct
        equity.append(equity[-1] * (1 + pnl))
        trades.append({
            'side': position['side'],
            'entry': position['entry'],
            'exit': final_price,
            'pnl': pnl,
            'reason': 'end_of_backtest'
        })

    equity = np.array(equity)
    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100

    winning = [t for t in trades if t['pnl'] > 0]
    win_rate = len(winning) / len(trades) * 100 if trades else 0

    return {
        'equity': equity,
        'total_return_pct': total_return,
        'max_drawdown_pct': max_dd,
        'n_trades': len(trades),
        'win_rate_pct': win_rate,
        'sharpe': calculate_sharpe(equity),
        'sortino': calculate_sortino(equity),
        'calmar': calculate_calmar(equity),
        'trades': trades,
    }
