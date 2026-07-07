"""
Grid Bot — Binance Test: 40 USDT, 20x Leverage
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json

CONFIG = {
    'symbol': 'BTC/USDT',
    'timeframe': '30m',
    'initial_capital': 40.0,
    'leverage': 20,             # 20x
    'grid_multiplier': 2.5,
    'stop_multiplier': 3.0,
    'risk_per_trade': 0.10,
    'reinvest_pct': 0.10,
    'commission': 0.0005,
    'atr_period': 14,
}

class GridBot20x:
    def __init__(self, config):
        self.config = config
        self.capital = config['initial_capital']
        self.leverage = config['leverage']
        self.position = None
        self.trades = []
        self.equity = []
        self.total_reinvested = 0
        self.total_commission = 0

    def calc_atr(self, df, period=14):
        h, l, c = df['High'], df['Low'], df['Close'].shift(1)
        tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def get_position_size(self, atr):
        stop_dist = atr * self.config['stop_multiplier']
        if stop_dist <= 0: return 0
        risk_money = self.capital * self.config['risk_per_trade']
        return (risk_money * self.leverage) / stop_dist

    def open_position(self, pos_type, price, atr):
        qty = self.get_position_size(atr)
        if qty <= 0 or self.capital < 1: return False
        stop_dist = atr * self.config['stop_multiplier']
        grid = atr * self.config['grid_multiplier']
        position_value = qty * price
        margin_required = position_value / self.leverage
        if margin_required > self.capital * 0.95:
            qty = (self.capital * 0.95 * self.leverage) / price
            margin_required = self.capital * 0.95

        if pos_type == 'long':
            stop, tp = price - stop_dist, price + grid
        else:
            stop, tp = price + stop_dist, price - grid

        self.position = {'type': pos_type, 'entry': price, 'qty': qty,
                        'stop': stop, 'tp': tp, 'margin': margin_required, 'atr': atr}
        return True

    def close_position(self, exit_price, reason):
        if not self.position: return
        pos = self.position
        pnl = ((exit_price - pos['entry']) * pos['qty'] if pos['type'] == 'long'
                else (pos['entry'] - exit_price) * pos['qty'])
        commission = (pos['entry'] + exit_price) * pos['qty'] * self.config['commission']
        net_pnl = pnl - commission
        self.total_commission += commission
        reinvest = net_pnl * self.config['reinvest_pct'] if net_pnl > 0 else 0
        self.total_reinvested += reinvest
        self.capital += net_pnl + reinvest

        # Liquidation check — if equity drops to 0
        if self.capital <= 0:
            self.capital = 0
            self.trades.append({'type': pos['type'], 'entry': pos['entry'], 'exit': exit_price,
                              'qty': pos['qty'], 'pnl': net_pnl, 'pnl_pct': -100,
                              'reason': 'LIQUIDATED', 'leverage': self.leverage})
            self.position = None
            return

        self.trades.append({'type': pos['type'], 'entry': pos['entry'], 'exit': exit_price,
                          'qty': pos['qty'], 'pnl': net_pnl,
                          'pnl_pct': (net_pnl / pos['margin']) * 100,
                          'reason': reason, 'leverage': self.leverage})
        self.position = None

    def process_bar(self, close, low, high, atr):
        if self.position:
            pos = self.position
            if pos['type'] == 'long':
                if low <= pos['stop']: self.close_position(pos['stop'], 'stop')
                elif high >= pos['tp']: self.close_position(pos['tp'], 'tp')
            else:
                if high >= pos['stop']: self.close_position(pos['stop'], 'stop')
                elif low <= pos['tp']: self.close_position(pos['tp'], 'tp')

        if self.position is None and self.capital > 1 and not pd.isna(atr) and atr > 0:
            prev_close = self.equity[-1]['close'] if self.equity else close
            if close < prev_close: self.open_position('long', close, atr)
            elif close > prev_close: self.open_position('short', close, atr)

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
        sharpe = (returns.mean() / returns.std() * np.sqrt(48*365)) if len(returns) > 1 and returns.std() > 0 else 0
        return {
            'initial': self.config['initial_capital'], 'final': self.capital,
            'pnl': total_pnl, 'pnl_pct': total_pnl / self.config['initial_capital'] * 100,
            'trades': len(self.trades), 'wins': len(wins), 'losses': len(losses),
            'wr': len(wins)/len(self.trades)*100, 'pf': gross_profit/gross_loss,
            'avg_win': np.mean([t['pnl'] for t in wins]) if wins else 0,
            'avg_loss': np.mean([t['pnl'] for t in losses]) if losses else 0,
            'mdd': max_dd*100, 'sharpe': sharpe, 'commission': self.total_commission,
            'reinvested': self.total_reinvested,
            'tp': len([t for t in self.trades if t['reason']=='tp']),
            'sl': len([t for t in self.trades if t['reason']=='stop']),
            'longs': len([t for t in self.trades if t['type']=='long']),
            'shorts': len([t for t in self.trades if t['type']=='short']),
        }


# Run all leverage tests
print("="*70)
print("  GRID BOT — LEVERAGE COMPARISON (40 USDT)")
print("="*70)

df = yf.download('BTC-USD', period='1mo', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"  BTC: {len(df)} bars, ${df['Close'].iloc[0]:.0f} — ${df['Close'].iloc[-1]:.0f}\n")

leverages = [1, 3, 5, 10, 15, 20, 25, 30]
all_results = []

print(f"  {'Lever':>6} {'Final$':>8} {'PnL%':>8} {'Trades':>6} {'Win%':>5} {'PF':>5} {'DD%':>6} {'Sharpe':>7} {'Comm$':>7}")
print(f"  {'-'*66}")

for lev in leverages:
    cfg = CONFIG.copy()
    cfg['leverage'] = lev
    bot = GridBot20x(cfg)
    m = bot.backtest(df)
    if m:
        all_results.append((lev, m, bot.trades))
        flag = " *" if lev == 20 else ""
        print(f"  {lev:>5}x ${m['final']:>7.2f} {m['pnl_pct']:>7.1f}% {m['trades']:>6} {m['wr']:>4.0f}% {m['pf']:>5.2f} {m['mdd']:>5.1f}% {m['sharpe']:>7.2f} ${m['commission']:>6.4f}{flag}")

# 20x detailed report
print(f"\n{'='*70}")
print(f"  DETAILED REPORT: 20x LEVERAGE")
print(f"{'='*70}")
bot20 = GridBot20x(CONFIG.copy())
bot20.config['leverage'] = 20
m20 = bot20.backtest(df)

print(f"\n  --- PARAMETERS ---")
print(f"  Capital:        ${CONFIG['initial_capital']:.0f} USDT")
print(f"  Leverage:       20x")
print(f"  Grid Spacing:   {CONFIG['grid_multiplier']}x ATR(14)")
print(f"  Stop Distance:  {CONFIG['stop_multiplier']}x ATR(14)")
print(f"  Risk/Trade:     {CONFIG['risk_per_trade']*100:.0f}%")
print(f"  Reinvest:       {CONFIG['reinvest_pct']*100:.0f}% of profit")
print(f"\n  --- RESULTS ---")
print(f"  Initial:        ${m20['initial']:.2f} USDT")
print(f"  Final:          ${m20['final']:.2f} USDT")
print(f"  Net PnL:        ${m20['pnl']:.2f} ({m20['pnl_pct']:.1f}%)")
print(f"  Reinvested:     ${m20['reinvested']:.2f}")
print(f"  Commission:     ${m20['commission']:.4f}")
print(f"\n  --- TRADES ---")
print(f"  Total:          {m20['trades']} (L:{m20['longs']} S:{m20['shorts']})")
print(f"  Win Rate:       {m20['wr']:.0f}% ({m20['wins']}W / {m20['losses']}L)")
print(f"  TP exits:       {m20['tp']}")
print(f"  SL exits:       {m20['sl']}")
print(f"  Avg Win:        ${m20['avg_win']:.4f}")
print(f"  Avg Loss:       ${m20['avg_loss']:.4f}")
print(f"\n  --- RISK ---")
print(f"  Profit Factor:  {m20['pf']:.2f}")
print(f"  Max Drawdown:   {m20['mdd']:.1f}%")
print(f"  Sharpe Ratio:   {m20['sharpe']:.2f}")
print(f"{'='*70}")

# Trade log
print(f"\n  --- ALL TRADES (20x) ---")
print(f"  {'#':>3} {'Type':>5} {'Entry':>10} {'Exit':>10} {'PnL$':>8} {'PnL%':>7} {'Reason':>10}")
for i, t in enumerate(bot20.trades):
    print(f"  {i+1:>3} {t['type']:>5} ${t['entry']:>9.0f} ${t['exit']:>9.0f} ${t['pnl']:>7.4f} {t['pnl_pct']:>6.1f}% {t['reason']:>10}")

# Save
with open('TsLabWorkspace/GridADAUSDT/grid_bot_20x_results.json', 'w') as f:
    json.dump({'leverage_comparison': [{'lev': l, **m} for l, m, _ in all_results],
               'detailed_20x': m20, 'trades_20x': bot20.trades,
               'config': CONFIG}, f, indent=2, default=str)
print(f"\n  Saved to grid_bot_20x_results.json")
