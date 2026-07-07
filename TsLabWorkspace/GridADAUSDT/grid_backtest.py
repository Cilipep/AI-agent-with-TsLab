import yfinance as yf
import pandas as pd
import numpy as np

# Download ADA data 30m
df = yf.download('ADA-USD', period='5d', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"Data: {len(df)} bars, {df.index[0]} — {df.index[-1]}")
print(f"Price range: {df['Low'].min():.4f} — {df['High'].max():.4f}")

# Parameters
INITIAL_CAPITAL = 25.0
SHARES = 10
REINVEST_PCT = 0.10
GRID_MULT = 1.0
STOP_MULT = 2.0
COMMISSION = 0.0005

# ATR calculation
def calc_atr(df, period=14):
    h = df['High']
    l = df['Low']
    c = df['Close'].shift(1)
    tr = pd.concat([h - l, (h - c).abs(), (l - c).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

df['ATR'] = calc_atr(df, 14)

# Grid strategy
capital = INITIAL_CAPITAL
positions = []  # list of {type, entry, shares, stop}
trades = []
equity_curve = []

for i in range(15, len(df)):
    row = df.iloc[i]
    prev = df.iloc[i-1]
    atr = df['ATR'].iloc[i]

    if pd.isna(atr) or atr <= 0:
        equity_curve.append(capital)
        continue

    grid_spacing = atr * GRID_MULT
    stop_level = atr * STOP_MULT

    close = row['Close']
    low = row['Low']
    high = row['High']

    # Check exits for existing positions
    closed = []
    for pos in positions:
        if pos['type'] == 'long':
            # Stop loss
            if low <= pos['stop']:
                pnl = (pos['stop'] - pos['entry']) * pos['shares']
                commission = pos['entry'] * pos['shares'] * COMMISSION + pos['stop'] * pos['shares'] * COMMISSION
                capital += pnl - commission
                trades.append({'type': 'long', 'entry': pos['entry'], 'exit': pos['stop'], 'pnl': pnl - commission, 'reason': 'stop'})
                closed.append(pos)
            # Take profit
            elif high >= pos['tp']:
                pnl = (pos['tp'] - pos['entry']) * pos['shares']
                commission = pos['entry'] * pos['shares'] * COMMISSION + pos['tp'] * pos['shares'] * COMMISSION
                reinvest = pnl * REINVEST_PCT
                capital += pnl - commission
                trades.append({'type': 'long', 'entry': pos['entry'], 'exit': pos['tp'], 'pnl': pnl - commission, 'reason': 'tp'})
                closed.append(pos)
        elif pos['type'] == 'short':
            if high >= pos['stop']:
                pnl = (pos['entry'] - pos['stop']) * pos['shares']
                commission = pos['entry'] * pos['shares'] * COMMISSION + pos['stop'] * pos['shares'] * COMMISSION
                capital += pnl - commission
                trades.append({'type': 'short', 'entry': pos['entry'], 'exit': pos['stop'], 'pnl': pnl - commission, 'reason': 'stop'})
                closed.append(pos)
            elif low <= pos['tp']:
                pnl = (pos['entry'] - pos['tp']) * pos['shares']
                commission = pos['entry'] * pos['shares'] * COMMISSION + pos['tp'] * pos['shares'] * COMMISSION
                capital += pnl - commission
                trades.append({'type': 'short', 'entry': pos['entry'], 'exit': pos['tp'], 'pnl': pnl - commission, 'reason': 'tp'})
                closed.append(pos)
    for p in closed:
        positions.remove(p)

    # Entry logic: price drops below close - ATR
    if close < prev['Close'] and len([p for p in positions if p['type'] == 'long']) == 0:
        entry_price = close
        positions.append({
            'type': 'long',
            'entry': entry_price,
            'shares': SHARES,
            'stop': entry_price - stop_level,
            'tp': entry_price + grid_spacing
        })

    # Entry: price rises above close + ATR
    elif close > prev['Close'] and len([p for p in positions if p['type'] == 'short']) == 0:
        entry_price = close
        positions.append({
            'type': 'short',
            'entry': entry_price,
            'shares': SHARES,
            'stop': entry_price + stop_level,
            'tp': entry_price - grid_spacing
        })

    # Mark-to-market
    unrealized = 0
    for pos in positions:
        if pos['type'] == 'long':
            unrealized += (close - pos['entry']) * pos['shares']
        else:
            unrealized += (pos['entry'] - close) * pos['shares']

    equity_curve.append(capital + unrealized)

# Close remaining positions at last price
for pos in positions:
    last_price = df['Close'].iloc[-1]
    if pos['type'] == 'long':
        pnl = (last_price - pos['entry']) * pos['shares']
    else:
        pnl = (pos['entry'] - last_price) * pos['shares']
    commission = pos['entry'] * pos['shares'] * COMMISSION + last_price * pos['shares'] * COMMISSION
    capital += pnl - commission
    trades.append({'type': pos['type'], 'entry': pos['entry'], 'exit': last_price, 'pnl': pnl - commission, 'reason': 'close'})

# Results
print("\n" + "="*50)
print("GRID ADAUSDT BACKTEST RESULTS")
print("="*50)
print(f"Period: {df.index[0]} — {df.index[-1]}")
print(f"Bars: {len(df)}")
print(f"Initial capital: ${INITIAL_CAPITAL:.2f}")
print(f"Final capital: ${capital:.2f}")
print(f"Net profit: ${capital - INITIAL_CAPITAL:.2f} ({(capital/INITIAL_CAPITAL - 1)*100:.1f}%)")
print(f"Total trades: {len(trades)}")

if trades:
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    print(f"Winning trades: {len(wins)} ({len(wins)/len(trades)*100:.0f}%)")
    print(f"Losing trades: {len(losses)}")

    if wins:
        print(f"Avg win: ${np.mean([t['pnl'] for t in wins]):.4f}")
    if losses:
        print(f"Avg loss: ${np.mean([t['pnl'] for t in losses]):.4f}")

    gross_profit = sum(t['pnl'] for t in wins) if wins else 0
    gross_loss = abs(sum(t['pnl'] for t in losses)) if losses else 0.01
    print(f"Profit factor: {gross_profit/gross_loss:.2f}")

    # Max drawdown
    peak = equity_curve[0]
    max_dd = 0
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak
        if dd > max_dd:
            max_dd = dd
    print(f"Max drawdown: {max_dd*100:.1f}%")

    # Sharpe
    returns = pd.Series(equity_curve).pct_change().dropna()
    if len(returns) > 0 and returns.std() > 0:
        sharpe = returns.mean() / returns.std() * np.sqrt(48 * 365)
        print(f"Sharpe ratio: {sharpe:.2f}")

    print(f"\nReinvested: 10% of profit per trade")
    print(f"Grid spacing: 1x ATR(14)")
    print(f"Stop loss: {STOP_MULT}x ATR(14)")
    print(f"Commission: {COMMISSION*100:.2f}%")
