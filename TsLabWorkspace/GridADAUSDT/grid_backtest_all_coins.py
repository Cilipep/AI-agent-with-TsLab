"""
Grid Bot — Бэктест на всех монетах с 20% реинвестом
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
from datetime import datetime

CONFIG = {
    'symbol': 'BTC/USDT',
    'timeframe': '30m',
    'initial_capital': 40.0,
    'leverage': 10,
    'grid_multiplier': 2.5,
    'stop_multiplier': 3.0,
    'risk_per_trade': 0.10,
    'reinvest_pct': 0.20,
    'commission': 0.0005,
    'atr_period': 14,
    'trailing_up_stop': 70000,
    'trailing_down_stop': 50000,
    'trailing_enabled': True,
    'use_atr_sl_tp': True,
    'stop_loss_pct': 0.03,
    'take_profit_pct': 0.05,
}

class GridBotBacktest:
    def __init__(self, config):
        self.config = config
        self.capital = config['initial_capital']
        self.leverage = config['leverage']
        self.position = None
        self.trades = []
        self.equity = []
        self.total_reinvested = 0
        self.total_commission = 0
        self.grid_lower = None
        self.grid_upper = None
        self.grid_shifts_up = 0
        self.grid_shifts_down = 0

    def calc_atr(self, df, p=14):
        h, l, c = df['High'], df['Low'], df['Close'].shift(1)
        return pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1).rolling(p).mean()

    def init_grid(self, price, atr):
        gs = atr * self.config['grid_multiplier']
        self.grid_lower = price - gs
        self.grid_upper = price + gs

    def check_trailing(self, close, atr):
        if not self.config['trailing_enabled']: return
        if self.grid_lower is None: self.init_grid(close, atr); return
        gs = atr * self.config['grid_multiplier']
        if close >= self.grid_upper:
            nu = self.grid_upper + gs
            if nu <= self.config['trailing_up_stop']:
                self.grid_upper = nu; self.grid_lower += gs; self.grid_shifts_up += 1
        if close <= self.grid_lower:
            nl = self.grid_lower - gs
            if nl >= self.config['trailing_down_stop']:
                self.grid_lower = nl; self.grid_upper -= gs; self.grid_shifts_down += 1

    def get_position_size(self, atr):
        sd = atr * self.config['stop_multiplier']
        if sd <= 0: return 0
        return (self.capital * self.config['risk_per_trade'] * self.leverage) / sd

    def open_position(self, pos_type, price, atr):
        qty = self.get_position_size(atr)
        if qty <= 0 or self.capital < 1: return False
        mv = qty * price / self.leverage
        if mv > self.capital * 0.95:
            qty = (self.capital * 0.95 * self.leverage) / price
        sd = atr * self.config['stop_multiplier']
        gs = atr * self.config['grid_multiplier']
        if pos_type == 'long':
            stop, tp = price - sd, price + gs
        else:
            stop, tp = price + sd, price - gs
        self.position = {'type': pos_type, 'entry': price, 'qty': qty, 'stop': stop, 'tp': tp, 'atr': atr}
        return True

    def close_position(self, exit_price, reason):
        if not self.position: return
        pos = self.position
        pnl = ((exit_price - pos['entry']) * pos['qty'] if pos['type'] == 'long'
                else (pos['entry'] - exit_price) * pos['qty'])
        comm = (pos['entry'] + exit_price) * pos['qty'] * self.config['commission']
        net_pnl = pnl - comm
        self.total_commission += comm
        reinvest = net_pnl * self.config['reinvest_pct'] if net_pnl > 0 else 0
        self.total_reinvested += reinvest
        self.capital += net_pnl + reinvest
        if self.capital <= 0:
            self.capital = 0
            self.trades.append({'type': pos['type'], 'entry': pos['entry'], 'exit': exit_price, 'qty': pos['qty'], 'pnl': net_pnl, 'pnl_pct': -100, 'reason': 'LIQUIDATED'})
            self.position = None; return
        margin = pos['qty'] * pos['entry'] / self.leverage
        self.trades.append({'type': pos['type'], 'entry': pos['entry'], 'exit': exit_price, 'qty': pos['qty'], 'pnl': net_pnl, 'pnl_pct': (net_pnl / margin) * 100, 'reason': reason})
        self.position = None

    def process_bar(self, close, low, high, atr):
        if not pd.isna(atr) and atr > 0: self.check_trailing(close, atr)
        if self.position:
            pos = self.position
            if pos['type'] == 'long':
                if low <= pos['stop']: self.close_position(pos['stop'], 'stop')
                elif high >= pos['tp']: self.close_position(pos['tp'], 'tp')
            else:
                if high >= pos['stop']: self.close_position(pos['stop'], 'stop')
                elif low <= pos['tp']: self.close_position(pos['tp'], 'tp')
        if self.position is None and self.capital > 1 and not pd.isna(atr) and atr > 0:
            prev = self.equity[-1]['close'] if self.equity else close
            if close < prev: self.open_position('long', close, atr)
            elif close > prev: self.open_position('short', close, atr)
        unr = 0
        if self.position:
            unr = ((close - self.position['entry']) if self.position['type'] == 'long'
                   else (self.position['entry'] - close)) * self.position['qty']
        self.equity.append({'close': close, 'equity': self.capital + unr, 'capital': self.capital})

    def backtest(self, df):
        df = df.copy()
        df['ATR'] = self.calc_atr(df, self.config['atr_period'])
        for i in range(20, len(df)):
            self.process_bar(df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i], df['ATR'].iloc[i])
        if self.position: self.close_position(df['Close'].iloc[-1], 'end')
        return self.get_metrics()

    def get_metrics(self):
        if not self.trades: return None
        pnl = self.capital - self.config['initial_capital']
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] <= 0]
        gp = sum(t['pnl'] for t in wins) if wins else 0
        gl = abs(sum(t['pnl'] for t in losses)) if losses else 0.001
        pk = self.config['initial_capital']; mdd = 0
        for e in self.equity:
            if e['equity'] > pk: pk = e['equity']
            dd = (pk - e['equity']) / pk
            if dd > mdd: mdd = dd
        ret = pd.Series([e['equity'] for e in self.equity]).pct_change().dropna()
        sh = (ret.mean() / ret.std() * np.sqrt(48*365)) if len(ret) > 1 and ret.std() > 0 else 0
        return {
            'initial': self.config['initial_capital'], 'final': self.capital,
            'pnl': pnl, 'pnl_pct': pnl / self.config['initial_capital'] * 100,
            'trades': len(self.trades), 'wins': len(wins), 'losses': len(losses),
            'wr': len(wins)/len(self.trades)*100, 'pf': gp/gl,
            'avg_win': np.mean([t['pnl'] for t in wins]) if wins else 0,
            'avg_loss': np.mean([t['pnl'] for t in losses]) if losses else 0,
            'mdd': mdd*100, 'sharpe': sh, 'commission': self.total_commission,
            'reinvested': self.total_reinvested,
            'tp': len([t for t in self.trades if t['reason']=='tp']),
            'sl': len([t for t in self.trades if t['reason']=='stop']),
            'longs': len([t for t in self.trades if t['type']=='long']),
            'shorts': len([t for t in self.trades if t['type']=='short']),
            'shifts_up': self.grid_shifts_up, 'shifts_down': self.grid_shifts_down,
        }


# Coins to test
coins = {
    'BTC': {'ticker': 'BTC-USD', 'trailing_up': 70000, 'trailing_down': 50000},
    'ETH': {'ticker': 'ETH-USD', 'trailing_up': 5000, 'trailing_down': 2000},
    'ADA': {'ticker': 'ADA-USD', 'trailing_up': 0.25, 'trailing_down': 0.10},
}

print("="*90)
print("  GRID BOT — БЭКТЕСТ НА ВСЕХ МОНЕТАХ (20% РЕИНВЕСТ)")
print("="*90)

all_results = []

for name, params in coins.items():
    print(f"\n--- {name} ---")
    df = yf.download(params['ticker'], period='1mo', interval='30m', progress=False)
    df.columns = df.columns.droplevel(1)
    print(f"  Данные: {len(df)} баров, ${df['Close'].iloc[0]:.2f} — ${df['Close'].iloc[-1]:.2f}")

    cfg = CONFIG.copy()
    cfg['symbol'] = name
    cfg['trailing_up_stop'] = params['trailing_up']
    cfg['trailing_down_stop'] = params['trailing_down']

    bot = GridBotBacktest(cfg)
    m = bot.backtest(df)

    if m:
        all_results.append({'coin': name, 'metrics': m, 'config': cfg})
        print(f"  PnL:       ${m['pnl']:.2f} ({m['pnl_pct']:.1f}%)")
        print(f"  Reinvest:  ${m['reinvested']:.2f}")
        print(f"  Trades:    {m['trades']} (L:{m['longs']} S:{m['shorts']})")
        print(f"  Win Rate:  {m['wr']:.0f}%")
        print(f"  PF:        {m['pf']:.2f}")
        print(f"  Max DD:    {m['mdd']:.1f}%")
        print(f"  Sharpe:    {m['sharpe']:.2f}")
        print(f"  Shifts:    ↑{m['shifts_up']} ↓{m['shifts_down']}")

# Summary table
print(f"\n{'='*90}")
print(f"  ИТОГИ НА ВСЕХ МОНЕТАХ (20% РЕИНВЕСТ, 10x ПЛЕЧО, 40 USDT)")
print(f"{'='*90}")
print(f"  {'Монета':<6} {'PnL$':>9} {'PnL%':>8} {'Reinvest$':>10} {'Trades':>6} {'Win%':>5} {'PF':>5} {'DD%':>6} {'Sharpe':>7} {'↑':>4} {'↓':>4}")
print(f"  {'-'*86}")
for r in all_results:
    m = r['metrics']
    print(f"  {r['coin']:<6} ${m['pnl']:>8.2f} {m['pnl_pct']:>7.1f}% ${m['reinvested']:>9.2f} {m['trades']:>6} {m['wr']:>4.0f}% {m['pf']:>5.2f} {m['mdd']:>5.1f}% {m['sharpe']:>7.2f} {m['shifts_up']:>4} {m['shifts_down']:>4}")

# Best coin
best = max(all_results, key=lambda x: x['metrics']['sharpe'])
print(f"\n  Лучшая монета: {best['coin']} (Sharpe: {best['metrics']['sharpe']:.2f}, PnL: {best['metrics']['pnl_pct']:.1f}%)")

# Save
with open('TsLabWorkspace/GridADAUSDT/backtest_all_coins.json', 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\n  Результаты сохранены: backtest_all_coins.json")
