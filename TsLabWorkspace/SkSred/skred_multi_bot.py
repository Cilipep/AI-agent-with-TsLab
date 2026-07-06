"""
SkSred v4 Multi-Portfolio Bot
=============================
Торгует 3 парами одновременно: XTZ, SUI, TRX
Распределение: 20 USDT на каждую, плечо 5x

Оптимизированные параметры (H4):
- XTZ: SMA(3/15) - Sharpe 13.81, MaxDD 3.04%
- SUI: SMA(3/15) - Sharpe 12.36, MaxDD 3.01%
- TRX: SMA(7/15) - Sharpe 16.61, MaxDD 0.94%
"""

import ccxt
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime
from config import API_KEY, API_SECRET, LEVERAGE

# ============================================================
# ОПТИМИЗИРОВАННЫЕ ПАРАМЕТРЫ
# ============================================================
INSTRUMENTS = {
    'XTZ/USDT:USDT': {
        'sma_s': 3, 'sma_l': 15,
        'alloc': 20,
        'description': 'XTZ - Sharpe 13.81, MaxDD 3.04%'
    },
    'SUI/USDT:USDT': {
        'sma_s': 3, 'sma_l': 15,
        'alloc': 20,
        'description': 'SUI - Sharpe 12.36, MaxDD 3.01%'
    },
    'TRX/USDT:USDT': {
        'sma_s': 7, 'sma_l': 15,
        'alloc': 20,
        'description': 'TRX - Sharpe 16.61, MaxDD 0.94%'
    },
}

# Стратегия
TIMEFRAME = '4h'
EMA_TREND = 200
ATR_PERIOD = 14
ATR_SL_MULT = 1.5
ATR_TP_MULT = 3.0
TRAIL_ACTIVATE = 0.02
TRAIL_DIST = 0.015
COMMISSION = 0.0005
CHECK_INTERVAL = 900  # 15 минут

# Логирование
LOG_DIR = r"C:\Users\i59400f\Desktop\ai-agent\TsLabWorkspace\SkSred\logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(os.path.join(LOG_DIR, 'multi_bot.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def log_trade(trade):
    with open(os.path.join(LOG_DIR, 'multi_trades.json'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(trade, default=str) + '\n')

# ============================================================
# ИНДИКАТОРЫ
# ============================================================
def calc_ema(s, p):
    return s.ewm(span=p, adjust=False).mean()

def calc_atr(df, p=14):
    tr = pd.concat([df['high']-df['low'], abs(df['high']-df['close'].shift(1)), abs(df['low']-df['close'].shift(1))], axis=1).max(axis=1)
    return tr.rolling(p).mean()

def prepare_data(df, sma_s, sma_l):
    df = df.copy()
    df['sma_s'] = df['close'].rolling(sma_s).mean()
    df['sma_l'] = df['close'].rolling(sma_l).mean()
    df['atr'] = calc_atr(df)
    ema_p = min(EMA_TREND, max(20, len(df)//2))
    df['ema'] = calc_ema(df['close'], ema_p)
    return df.dropna()

def get_signal(df):
    if len(df) < 3:
        return None
    last = df.iloc[-1]
    prev = df.iloc[-2]
    gc = (last['sma_s'] > last['sma_l']) and (prev['sma_s'] <= prev['sma_l'])
    dc = (last['sma_s'] < last['sma_l']) and (prev['sma_s'] >= prev['sma_l'])
    if gc and last['close'] > last['ema']:
        return 'LONG'
    elif dc and last['close'] < last['ema']:
        return 'SHORT'
    return None

# ============================================================
# БОТ
# ============================================================
class MultiPortfolioBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'options': {'defaultType': 'future', 'adjustForTimeDifference': True},
            'enableRateLimit': True,
        })
        try:
            self.exchange.set_position_mode(False)
        except:
            pass
        self.trail_data = {}
        self.load_state()

    def load_state(self):
        f = os.path.join(LOG_DIR, 'multi_state.json')
        if os.path.exists(f):
            with open(f, 'r') as fh:
                self.trail_data = json.load(fh).get('trail', {})

    def save_state(self):
        with open(os.path.join(LOG_DIR, 'multi_state.json'), 'w') as f:
            json.dump({'trail': self.trail_data}, f)

    def get_balance(self):
        return float(self.exchange.fetch_balance()['USDT']['free'])

    def get_position(self, symbol):
        for pos in self.exchange.fetch_positions([symbol]):
            if pos['symbol'] == symbol and float(pos['contracts']) > 0:
                return {'side': pos['side'], 'amount': float(pos['contracts']),
                        'entry': float(pos['entryPrice']), 'pnl': float(pos['unrealizedPnl'])}
        return None

    def open_position(self, symbol, side, alloc, price):
        try:
            amount = alloc * LEVERAGE / price
            amount = float(self.exchange.amount_to_precision(symbol, amount))
            if amount <= 0:
                return None
            self.exchange.set_leverage(LEVERAGE, symbol)
            order = self.exchange.create_market_order(
                symbol, 'buy' if side == 'LONG' else 'sell', amount,
                params={'positionSide': side}
            )
            log(f"OPEN {symbol} {side} | {amount} @ {price:.4f}")
            log_trade({'symbol': symbol, 'action': 'OPEN', 'side': side, 'amount': amount, 'price': price, 'time': datetime.now().isoformat()})
            return order
        except Exception as e:
            log(f"ERROR open {symbol}: {e}")
            return None

    def close_position(self, symbol, side, amount, entry_price=None):
        try:
            # Получить текущую цену для расчета PnL
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Рассчитать PnL
            if side == 'LONG':
                pnl_pct = (current_price - entry_price) / entry_price * LEVERAGE * 100 if entry_price else 0
            else:
                pnl_pct = (entry_price - current_price) / entry_price * LEVERAGE * 100 if entry_price else 0
            pnl_usd = amount * current_price * pnl_pct / 100 / LEVERAGE
            
            order = self.exchange.create_market_order(
                symbol, 'sell' if side == 'LONG' else 'buy', amount,
                params={'positionSide': side}
            )
            log(f"CLOSE {symbol} {side} | {amount} | PnL: {pnl_pct:+.2f}%")
            log_trade({'symbol': symbol, 'action': 'CLOSE', 'side': side, 'amount': amount, 'pnl_pct': pnl_pct, 'time': datetime.now().isoformat()})
            return order
        except Exception as e:
            log(f"ERROR close {symbol}: {e}")
            return None

    def process(self, symbol, params):
        alloc = params['alloc']
        df = self.exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=250)
        if not df or len(df) < params['sma_l'] + 10:
            return

        df = pd.DataFrame(df, columns=['timestamp','open','high','low','close','volume'])
        df = prepare_data(df, params['sma_s'], params['sma_l'])
        signal = get_signal(df)
        price = df.iloc[-1]['close']
        pos = self.get_position(symbol)
        trail = self.trail_data.get(symbol, {'on': False, 'h': None, 'l': None})

        # Нет позиции + есть сигнал → вход
        if pos is None and signal:
            bal = self.get_balance()
            if bal >= alloc:
                self.open_position(symbol, signal, alloc, price)
                trail = {'on': False, 'h': price if signal == 'LONG' else None, 'l': price if signal == 'SHORT' else None}
                self.trail_data[symbol] = trail
                self.save_state()
            return

        # Есть позиция → проверка выхода
        if pos:
            side = pos['side'].upper()
            entry = pos['entry']
            amt = pos['amount']

            if side == 'LONG':
                if trail['h'] is None or price > trail['h']:
                    trail['h'] = price
                if not trail['on'] and (price - entry) / entry >= TRAIL_ACTIVATE:
                    trail['on'] = True
                    log(f"{symbol}: Trail activated")
                if trail['on'] and price <= trail['h'] * (1 - TRAIL_DIST):
                    log(f"{symbol}: TRAIL STOP")
                    self.close_position(symbol, 'LONG', amt, entry)
                    self.trail_data[symbol] = {'on': False, 'h': None, 'l': None}
                    self.save_state()
                    return
                if signal == 'SHORT':
                    log(f"{symbol}: SIGNAL EXIT")
                    self.close_position(symbol, 'LONG', amt, entry)
                    self.trail_data[symbol] = {'on': False, 'h': None, 'l': None}
                    self.save_state()
                    return

            elif side == 'SHORT':
                if trail['l'] is None or price < trail['l']:
                    trail['l'] = price
                if not trail['on'] and (entry - price) / entry >= TRAIL_ACTIVATE:
                    trail['on'] = True
                    log(f"{symbol}: Trail activated")
                if trail['on'] and price >= trail['l'] * (1 + TRAIL_DIST):
                    log(f"{symbol}: TRAIL STOP")
                    self.close_position(symbol, 'SHORT', amt, entry)
                    self.trail_data[symbol] = {'on': False, 'h': None, 'l': None}
                    self.save_state()
                    return
                if signal == 'LONG':
                    log(f"{symbol}: SIGNAL EXIT")
                    self.close_position(symbol, 'SHORT', amt, entry)
                    self.trail_data[symbol] = {'on': False, 'h': None, 'l': None}
                    self.save_state()
                    return

            self.trail_data[symbol] = trail

    def run(self):
        log("="*60)
        log("SkSred v4 Multi-Portfolio Bot")
        log(f"Pairs: {list(INSTRUMENTS.keys())}")
        log(f"Allocation: 20 USDT x 3 = 60 USDT | Leverage: {LEVERAGE}x")
        log(f"Check interval: {CHECK_INTERVAL}s")
        log("="*60)
        log(f"Balance: {self.get_balance():.2f} USDT")

        while True:
            try:
                for symbol, params in INSTRUMENTS.items():
                    self.process(symbol, params)
                    time.sleep(2)
                log(f"Cycle done. Next in {CHECK_INTERVAL}s...")
                time.sleep(CHECK_INTERVAL)
            except KeyboardInterrupt:
                log("Stopped by user")
                break
            except Exception as e:
                log(f"Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = MultiPortfolioBot()
    bot.run()
