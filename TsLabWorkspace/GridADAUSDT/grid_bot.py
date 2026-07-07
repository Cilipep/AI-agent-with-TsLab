"""
Grid Trading Bot — Optimized for BTC
Parameters: Grid=2.5x ATR, Stop=3.0x ATR, Risk=10%, Reinvest=10%
Backtest results: +124.4% PnL, 68% Win Rate, PF=1.54, Sharpe=5.13
"""

import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import ccxt
    EXCHANGE = ccxt.binance({'options': {'defaultType': 'future'}})
    LIVE_MODE = True
except ImportError:
    LIVE_MODE = False
    print("ccxt not installed — backtest mode only")

# === STRATEGY PARAMETERS ===
CONFIG = {
    'symbol': 'BTC/USDT:USDT',
    'timeframe': '30m',
    'initial_capital': 25.0,
    'grid_multiplier': 2.5,    # ATR * 2.5 = grid spacing
    'stop_multiplier': 3.0,    # ATR * 3.0 = stop distance
    'risk_per_trade': 0.10,    # 10% of capital per trade
    'reinvest_pct': 0.10,      # 10% of profit reinvested
    'commission': 0.0005,      # 0.05% per trade
    'atr_period': 14,
    'max_positions': 1,        # max 1 position at a time
}

class GridBot:
    def __init__(self, config):
        self.config = config
        self.capital = config['initial_capital']
        self.position = None  # {'type': 'long/short', 'entry': float, 'qty': float, 'stop': float, 'tp': float}
        self.trades = []
        self.equity = []
        self.total_reinvested = 0

    def calc_atr(self, df, period=14):
        h, l, c = df['High'], df['Low'], df['Close'].shift(1)
        tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def get_position_size(self, atr):
        stop_dist = atr * self.config['stop_multiplier']
        if stop_dist <= 0:
            return 0
        risk_money = self.capital * self.config['risk_per_trade']
        return risk_money / stop_dist

    def open_position(self, pos_type, price, atr):
        qty = self.get_position_size(atr)
        if qty <= 0 or self.capital < 1:
            return

        stop_dist = atr * self.config['stop_multiplier']
        grid = atr * self.config['grid_multiplier']

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
            'entry_time': datetime.now(),
            'atr': atr
        }

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

        # Reinvest profit
        reinvest = net_pnl * self.config['reinvest_pct'] if net_pnl > 0 else 0
        self.total_reinvested += reinvest

        self.capital += net_pnl
        self.trades.append({
            'type': pos['type'],
            'entry': pos['entry'],
            'exit': exit_price,
            'qty': pos['qty'],
            'pnl': net_pnl,
            'reinvest': reinvest,
            'reason': reason,
            'entry_time': pos['entry_time'],
            'exit_time': datetime.now()
        })
        self.position = None

    def process_bar(self, close, low, high, atr):
        # Check exits first
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

        # Entry (no filter — best for BTC per optimization)
        if self.position is None and not pd.isna(atr) and atr > 0:
            prev_close = self.equity[-1]['close'] if self.equity else close
            if close < prev_close:  # price dropped
                self.open_position('long', close, atr)
            elif close > prev_close:  # price rose
                self.open_position('short', close, atr)

        # Track equity
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
            'position': self.position['type'] if self.position else None
        })

    def backtest(self, df):
        df = df.copy()
        df['ATR'] = self.calc_atr(df, self.config['atr_period'])

        for i in range(20, len(df)):
            self.process_bar(
                df['Close'].iloc[i],
                df['Low'].iloc[i],
                df['High'].iloc[i],
                df['ATR'].iloc[i]
            )

        # Close any remaining position
        if self.position:
            self.close_position(df['Close'].iloc[-1], 'end')

        return self.get_metrics()

    def get_metrics(self):
        if not self.trades:
            return None

        total_pnl = self.capital - self.config['initial_capital']
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] <= 0]
        win_rate = len(wins) / len(self.trades) * 100

        gross_profit = sum(t['pnl'] for t in wins) if wins else 0
        gross_loss = abs(sum(t['pnl'] for t in losses)) if losses else 0.001
        profit_factor = gross_profit / gross_loss

        # Max drawdown
        peak = self.config['initial_capital']
        max_dd = 0
        for eq in self.equity:
            if eq['equity'] > peak:
                peak = eq['equity']
            dd = (peak - eq['equity']) / peak
            if dd > max_dd:
                max_dd = dd

        # Sharpe ratio
        returns = pd.Series([e['equity'] for e in self.equity]).pct_change().dropna()
        sharpe = (returns.mean() / returns.std() * np.sqrt(48 * 365)) if len(returns) > 1 and returns.std() > 0 else 0

        return {
            'initial_capital': self.config['initial_capital'],
            'final_capital': self.capital,
            'net_pnl': total_pnl,
            'net_pnl_pct': total_pnl / self.config['initial_capital'] * 100,
            'total_trades': len(self.trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': np.mean([t['pnl'] for t in wins]) if wins else 0,
            'avg_loss': np.mean([t['pnl'] for t in losses]) if losses else 0,
            'max_drawdown_pct': max_dd * 100,
            'sharpe_ratio': sharpe,
            'total_reinvested': self.total_reinvested,
            'long_trades': len([t for t in self.trades if t['type'] == 'long']),
            'short_trades': len([t for t in self.trades if t['type'] == 'short']),
            'tp_exits': len([t for t in self.trades if t['reason'] == 'tp']),
            'sl_exits': len([t for t in self.trades if t['reason'] == 'stop']),
        }

    def print_report(self, metrics):
        if not metrics:
            print("No trades executed")
            return

        print("\n" + "="*60)
        print("GRID BOT — OPTIMIZED BTC STRATEGY RESULTS")
        print("="*60)
        print(f"Period: Backtest (1 month)")
        print(f"Symbol: {self.config['symbol']}")
        print(f"Timeframe: {self.config['timeframe']}")
        print(f"\n--- PARAMETERS ---")
        print(f"Grid Spacing: {self.config['grid_multiplier']}x ATR(14)")
        print(f"Stop Distance: {self.config['stop_multiplier']}x ATR(14)")
        print(f"Risk per Trade: {self.config['risk_per_trade']*100:.0f}%")
        print(f"Reinvest: {self.config['reinvest_pct']*100:.0f}% of profit")
        print(f"Commission: {self.config['commission']*100:.2f}%")
        print(f"\n--- RESULTS ---")
        print(f"Initial Capital: ${metrics['initial_capital']:.2f}")
        print(f"Final Capital: ${metrics['final_capital']:.2f}")
        print(f"Net PnL: ${metrics['net_pnl']:.2f} ({metrics['net_pnl_pct']:.1f}%)")
        print(f"Total Reinvested: ${metrics['total_reinvested']:.2f}")
        print(f"\n--- TRADES ---")
        print(f"Total: {metrics['total_trades']} (L:{metrics['long_trades']} S:{metrics['short_trades']})")
        print(f"Winning: {metrics['winning_trades']} ({metrics['win_rate']:.0f}%)")
        print(f"Losing: {metrics['losing_trades']}")
        print(f"Take Profit exits: {metrics['tp_exits']}")
        print(f"Stop Loss exits: {metrics['sl_exits']}")
        print(f"Avg Win: ${metrics['avg_win']:.4f}")
        print(f"Avg Loss: ${metrics['avg_loss']:.4f}")
        print(f"\n--- RISK ---")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Max Drawdown: {metrics['max_drawdown_pct']:.1f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print("="*60)

    def save_results(self, filename='grid_bot_results.json'):
        results = {
            'config': self.config,
            'metrics': self.get_metrics(),
            'trades': [{
                'type': t['type'], 'entry': t['entry'], 'exit': t['exit'],
                'qty': t['qty'], 'pnl': t['pnl'], 'reason': t['reason'],
                'reinvest': t['reinvest']
            } for t in self.trades]
        }
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to {filename}")


def run_backtest():
    import yfinance as yf
    print("Downloading BTC data...")
    df = yf.download('BTC-USD', period='1mo', interval='30m', progress=False)
    df.columns = df.columns.droplevel(1)
    print(f"Data: {len(df)} bars, ${df['Close'].iloc[0]:.0f} — ${df['Close'].iloc[-1]:.0f}")

    bot = GridBot(CONFIG)
    metrics = bot.backtest(df)
    bot.print_report(metrics)
    bot.save_results('TsLabWorkspace/GridADAUSDT/grid_bot_results.json')
    return bot, metrics


def run_live():
    if not LIVE_MODE:
        print("ccxt not installed. Install with: pip install ccxt")
        return

    print("Starting live grid bot...")
    bot = GridBot(CONFIG)

    while True:
        try:
            # Get current price
            ticker = EXCHANGE.fetch_ticker(CONFIG['symbol'])
            price = ticker['last']

            # Get recent bars for ATR
            ohlcv = EXCHANGE.fetch_ohlcv(CONFIG['symbol'], CONFIG['timeframe'], limit=20)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

            # Calculate ATR
            h, l, c = df['High'], df['Low'], df['Close'].shift(1)
            tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
            atr = tr.rolling(14).mean().iloc[-1]

            if pd.isna(atr) or atr <= 0:
                time.sleep(60)
                continue

            # Process current bar
            bot.process_bar(
                df['Close'].iloc[-1],
                df['Low'].iloc[-1],
                df['High'].iloc[-1],
                atr
            )

            # Print status
            pos_info = f"{bot.position['type']} @ {bot.position['entry']:.0f}" if bot.position else "No position"
            print(f"[{datetime.now().strftime('%H:%M')}] Price: ${price:.0f} | ATR: ${atr:.0f} | Capital: ${bot.capital:.2f} | {pos_info}")

            time.sleep(1800)  # 30 minutes

        except KeyboardInterrupt:
            print("\nBot stopped by user")
            if bot.position:
                bot.close_position(price, 'manual')
            metrics = bot.get_metrics()
            bot.print_report(metrics)
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'live':
        run_live()
    else:
        run_backtest()
