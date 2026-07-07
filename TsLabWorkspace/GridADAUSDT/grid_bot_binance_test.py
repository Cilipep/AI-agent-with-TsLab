"""
Grid Bot — Binance Test Configuration
Capital: 40 USDT, Leverage: 10x
Strategy: Grid=2.5x ATR, Stop=3.0x ATR, Risk=10%, Reinvest=10%
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
from datetime import datetime

# === CONFIGURATION ===
CONFIG = {
    'symbol': 'BTC/USDT',
    'timeframe': '30m',
    'initial_capital': 40.0,    # 40 USDT
    'leverage': 10,             # 10x leverage
    'grid_multiplier': 2.5,
    'stop_multiplier': 3.0,
    'risk_per_trade': 0.10,     # 10% of capital per trade
    'reinvest_pct': 0.10,
    'commission': 0.0005,       # 0.05% taker fee
    'atr_period': 14,
}

class GridBotBinance:
    def __init__(self, config):
        self.config = config
        self.capital = config['initial_capital']
        self.leverage = config['leverage']
        self.position = None
        self.trades = []
        self.equity = []
        self.total_reinvested = 0
        self.total_commission = 0
        self.max_positions = 0

    def calc_atr(self, df, period=14):
        h, l, c = df['High'], df['Low'], df['Close'].shift(1)
        tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def get_position_size(self, atr):
        stop_dist = atr * self.config['stop_multiplier']
        if stop_dist <= 0:
            return 0
        risk_money = self.capital * self.config['risk_per_trade']
        # With leverage, effective position = risk_money * leverage / stop_distance
        qty = (risk_money * self.leverage) / stop_dist
        return qty

    def open_position(self, pos_type, price, atr):
        qty = self.get_position_size(atr)
        if qty <= 0 or self.capital < 1:
            return False

        stop_dist = atr * self.config['stop_multiplier']
        grid = atr * self.config['grid_multiplier']

        # Position value with leverage
        position_value = qty * price
        margin_required = position_value / self.leverage

        if margin_required > self.capital * 0.95:  # don't use more than 95% as margin
            qty = (self.capital * 0.95 * self.leverage) / price
            margin_required = self.capital * 0.95

        if pos_type == 'long':
            stop = price - stop_dist
            tp = price + grid
        else:
            stop = price + stop_dist
            tp = price - grid

        self.position = {
            'type': pos_type,
            'entry': price,
            'qty': qty,
            'stop': stop,
            'tp': tp,
            'margin': margin_required,
            'position_value': qty * price,
            'entry_time': datetime.now(),
            'atr': atr
        }
        self.max_positions = max(self.max_positions, 1)
        return True

    def close_position(self, exit_price, reason):
        if not self.position:
            return

        pos = self.position
        if pos['type'] == 'long':
            pnl = (exit_price - pos['entry']) * pos['qty']
        else:
            pnl = (pos['entry'] - exit_price) * pos['qty']

        commission = (pos['entry'] + exit_price) * pos['qty'] * self.config['commission']
        net_pnl = pnl - commission
        self.total_commission += commission

        # Reinvest profit
        reinvest = net_pnl * self.config['reinvest_pct'] if net_pnl > 0 else 0
        self.total_reinvested += reinvest

        self.capital += net_pnl + reinvest  # add reinvested amount
        self.trades.append({
            'type': pos['type'],
            'entry': pos['entry'],
            'exit': exit_price,
            'qty': pos['qty'],
            'margin': pos['margin'],
            'pnl': net_pnl,
            'pnl_pct': (net_pnl / pos['margin']) * 100,
            'reinvest': reinvest,
            'reason': reason,
            'leverage': self.leverage,
        })
        self.position = None

    def process_bar(self, close, low, high, atr):
        if self.position:
            pos = self.position
            if pos['type'] == 'long':
                if low <= pos['stop']:
                    self.close_position(pos['stop'], 'stop')
                elif high >= pos['tp']:
                    self.close_position(pos['tp'], 'tp')
            else:
                if high >= pos['stop']:
                    self.close_position(pos['stop'], 'stop')
                elif low <= pos['tp']:
                    self.close_position(pos['tp'], 'tp')

        if self.position is None and not pd.isna(atr) and atr > 0:
            prev_close = self.equity[-1]['close'] if self.equity else close
            if close < prev_close:
                self.open_position('long', close, atr)
            elif close > prev_close:
                self.open_position('short', close, atr)

        unrealized = 0
        if self.position:
            if self.position['type'] == 'long':
                unrealized = (close - self.position['entry']) * self.position['qty']
            else:
                unrealized = (self.position['entry'] - close) * self.position['qty']

        self.equity.append({
            'close': close,
            'equity': self.capital + unrealized,
            'capital': self.capital,
        })

    def backtest(self, df):
        df = df.copy()
        df['ATR'] = self.calc_atr(df, self.config['atr_period'])

        for i in range(20, len(df)):
            self.process_bar(
                df['Close'].iloc[i], df['Low'].iloc[i],
                df['High'].iloc[i], df['ATR'].iloc[i]
            )

        if self.position:
            self.close_position(df['Close'].iloc[-1], 'end')

        return self.get_metrics()

    def get_metrics(self):
        if not self.trades:
            return None

        total_pnl = self.capital - self.config['initial_capital']
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] <= 0]

        gross_profit = sum(t['pnl'] for t in wins) if wins else 0
        gross_loss = abs(sum(t['pnl'] for t in losses)) if losses else 0.001

        peak = self.config['initial_capital']
        max_dd = 0
        for eq in self.equity:
            if eq['equity'] > peak: peak = eq['equity']
            dd = (peak - eq['equity']) / peak
            if dd > max_dd: max_dd = dd

        returns = pd.Series([e['equity'] for e in self.equity]).pct_change().dropna()
        sharpe = (returns.mean() / returns.std() * np.sqrt(48 * 365)) if len(returns) > 1 and returns.std() > 0 else 0

        return {
            'initial_capital': self.config['initial_capital'],
            'final_capital': self.capital,
            'net_pnl': total_pnl,
            'net_pnl_pct': total_pnl / self.config['initial_capital'] * 100,
            'leverage': self.leverage,
            'total_trades': len(self.trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(self.trades) * 100,
            'profit_factor': gross_profit / gross_loss,
            'avg_win': np.mean([t['pnl'] for t in wins]) if wins else 0,
            'avg_loss': np.mean([t['pnl'] for t in losses]) if losses else 0,
            'max_drawdown_pct': max_dd * 100,
            'sharpe_ratio': sharpe,
            'total_commission': self.total_commission,
            'total_reinvested': self.total_reinvested,
            'tp_exits': len([t for t in self.trades if t['reason'] == 'tp']),
            'sl_exits': len([t for t in self.trades if t['reason'] == 'stop']),
            'long_trades': len([t for t in self.trades if t['type'] == 'long']),
            'short_trades': len([t for t in self.trades if t['type'] == 'short']),
        }

    def print_report(self, metrics):
        if not metrics:
            print("No trades"); return

        print("\n" + "="*65)
        print("  GRID BOT — BINANCE TEST (40 USDT, 10x LEVERAGE)")
        print("="*65)
        print(f"  Symbol: {self.config['symbol']} Perpetual")
        print(f"  Timeframe: {self.config['timeframe']}")
        print(f"\n  --- PARAMETERS ---")
        print(f"  Grid Spacing:  {self.config['grid_multiplier']}x ATR(14)")
        print(f"  Stop Distance: {self.config['stop_multiplier']}x ATR(14)")
        print(f"  Risk/Trade:    {self.config['risk_per_trade']*100:.0f}%")
        print(f"  Leverage:      {self.leverage}x")
        print(f"  Reinvest:      {self.config['reinvest_pct']*100:.0f}% of profit")
        print(f"  Commission:    {self.config['commission']*100:.2f}%")
        print(f"\n  --- RESULTS ---")
        print(f"  Initial:       ${metrics['initial_capital']:.2f} USDT")
        print(f"  Final:         ${metrics['final_capital']:.2f} USDT")
        print(f"  Net PnL:       ${metrics['net_pnl']:.2f} ({metrics['net_pnl_pct']:.1f}%)")
        print(f"  Reinvested:    ${metrics['total_reinvested']:.2f}")
        print(f"  Commission:    ${metrics['total_commission']:.4f}")
        print(f"\n  --- TRADES ---")
        print(f"  Total:         {metrics['total_trades']} (L:{metrics['long_trades']} S:{metrics['short_trades']})")
        print(f"  Win Rate:      {metrics['win_rate']:.0f}% ({metrics['winning_trades']}W / {metrics['losing_trades']}L)")
        print(f"  TP exits:      {metrics['tp_exits']}")
        print(f"  SL exits:      {metrics['sl_exits']}")
        print(f"  Avg Win:       ${metrics['avg_win']:.4f}")
        print(f"  Avg Loss:      ${metrics['avg_loss']:.4f}")
        print(f"\n  --- RISK ---")
        print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"  Max Drawdown:  {metrics['max_drawdown_pct']:.1f}%")
        print(f"  Sharpe Ratio:  {metrics['sharpe_ratio']:.2f}")
        print("="*65)

        # Trade log (last 10)
        print(f"\n  --- LAST 10 TRADES ---")
        print(f"  {'#':>3} {'Type':>5} {'Entry':>10} {'Exit':>10} {'PnL$':>8} {'PnL%':>7} {'Reason':>6}")
        for i, t in enumerate(self.trades[-10:]):
            print(f"  {i+1:>3} {t['type']:>5} ${t['entry']:>9.0f} ${t['exit']:>9.0f} ${t['pnl']:>7.4f} {t['pnl_pct']:>6.1f}% {t['reason']:>6}")


# Run backtest
print("Downloading BTC data (1 month)...")
df = yf.download('BTC-USD', period='1mo', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"Data: {len(df)} bars, ${df['Close'].iloc[0]:.0f} — ${df['Close'].iloc[-1]:.0f}")

bot = GridBotBinance(CONFIG)
metrics = bot.backtest(df)
bot.print_report(metrics)

# Save
with open('TsLabWorkspace/GridADAUSDT/grid_bot_binance_test.json', 'w') as f:
    json.dump({
        'config': CONFIG,
        'metrics': metrics,
        'trades': bot.trades[-20:],
        'equity_snapshots': [{'time': str(i), 'equity': e['equity']} for i, e in enumerate(bot.equity[::48])]
    }, f, indent=2, default=str)
print("\nResults saved to grid_bot_binance_test.json")
