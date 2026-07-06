"""
SkSred v4 Trading Bot for Binance Futures
==========================================
Торговый бот на основе стратегии SkSred v4
3 пары: XTZ, SUI, TRX | 20 USDT каждая | Плечо 5x

ВАЖНО: Сначала протестируйте на тестовой сети (testnet)!
"""

import ccxt
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime
from config import (API_KEY, API_SECRET, USE_TESTNET, LEVERAGE, TIMEFRAME,
                    INSTRUMENTS, EMA_TREND, ATR_PERIOD, ATR_SL_MULT, ATR_TP_MULT,
                    TRAIL_ACTIVATE, TRAIL_DIST, COMMISSION, CHECK_INTERVAL)

# ============================================================
# ЛОГИРОВАНИЕ
# ============================================================
LOG_DIR = r"C:\Users\i59400f\Desktop\ai-agent\TsLabWorkspace\SkSred\logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(os.path.join(LOG_DIR, 'bot.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def log_trade(trade):
    with open(os.path.join(LOG_DIR, 'trades.json'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(trade, default=str) + '\n')

# ============================================================
# ИНДИКАТОРЫ
# ============================================================
def calc_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calc_atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def prepare_data(df, sma_s, sma_l):
    df = df.copy()
    df['sma_s'] = df['close'].rolling(window=sma_s).mean()
    df['sma_l'] = df['close'].rolling(window=sma_l).mean()
    df['atr'] = calc_atr(df, ATR_PERIOD)
    ema_p = min(EMA_TREND, max(20, len(df)//2))
    df['ema'] = calc_ema(df['close'], ema_p)
    df = df.dropna()
    return df

def get_signals(df):
    """Получить торговые сигналы"""
    if len(df) < 3:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    sma_s = last['sma_s']
    sma_l = last['sma_l']
    sma_s_prev = prev['sma_s']
    sma_l_prev = prev['sma_l']
    ema = last['ema']
    atr = last['atr']
    price = last['close']

    golden_cross = (sma_s > sma_l) and (sma_s_prev <= sma_l_prev)
    death_cross = (sma_s < sma_l) and (sma_s_prev >= sma_l_prev)

    signal = None
    if golden_cross and price > ema:
        signal = 'LONG'
    elif death_cross and price < ema:
        signal = 'SHORT'

    return {
        'signal': signal,
        'price': price,
        'atr': atr,
        'sl_long': price - atr * ATR_SL_MULT,
        'tp_long': price + atr * ATR_TP_MULT,
        'sl_short': price + atr * ATR_SL_MULT,
        'tp_short': price - atr * ATR_TP_MULT,
    }

# ============================================================
# КЛАСС БОТА
# ============================================================
class SkSredBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True,
            },
            'enableRateLimit': True,
        })

        if USE_TESTNET:
            self.exchange.set_sandbox_mode(True)
            log("РЕЖИМ: Testnet (тестовая сеть)")
        else:
            log("РЕЖИМ: Реальная торговля!")

        # Настройка hedge mode
        try:
            self.exchange.set_position_mode(False)  # One-way mode
            log("Position mode: One-way")
        except Exception as e:
            log(f"Position mode already set or error: {e}")

        self.positions = {}
        self.trail_data = {}
        self.load_state()

    def load_state(self):
        """Загрузить состояние из файла"""
        state_file = os.path.join(LOG_DIR, 'state.json')
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
                self.positions = state.get('positions', {})
                self.trail_data = state.get('trail_data', {})
            log(f"Состояние загружено: {len(self.positions)} позиций")

    def save_state(self):
        """Сохранить состояние"""
        state_file = os.path.join(LOG_DIR, 'state.json')
        with open(state_file, 'w') as f:
            json.dump({
                'positions': self.positions,
                'trail_data': self.trail_data,
                'updated': datetime.now().isoformat()
            }, f, default=str)

    def setup_leverage(self, symbol):
        """Установить плечо"""
        try:
            self.exchange.set_leverage(LEVERAGE, symbol)
            log(f"{symbol}: плечо установлено {LEVERAGE}x")
        except Exception as e:
            log(f"{symbol}: ошибка установки плеча: {e}")

    def get_ohlcv(self, symbol, limit=250):
        """Получить свечи"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            log(f"{symbol}: ошибка получения данных: {e}")
            return None

    def get_balance(self):
        """Получить баланс"""
        try:
            balance = self.exchange.fetch_balance()
            return float(balance['USDT']['free'])
        except Exception as e:
            log(f"Ошибка получения баланса: {e}")
            return 0

    def get_position(self, symbol):
        """Получить текущую позицию"""
        try:
            positions = self.exchange.fetch_positions([symbol])
            for pos in positions:
                if pos['symbol'] == symbol and float(pos['contracts']) > 0:
                    return {
                        'side': pos['side'],
                        'amount': float(pos['contracts']),
                        'entry_price': float(pos['entryPrice']),
                        'unrealized_pnl': float(pos['unrealizedPnl']),
                    }
            return None
        except Exception as e:
            log(f"{symbol}: ошибка получения позиции: {e}")
            return None

    def open_position(self, symbol, side, amount_usdt, price):
        """Открыть позицию"""
        try:
            # Рассчитать количество контрактов
            amount = amount_usdt * LEVERAGE / price

            # Округлить до допустимого количества знаков
            market = self.exchange.market(symbol)
            amount = self.exchange.amount_to_precision(symbol, amount)
            amount = float(amount)

            if amount <= 0:
                log(f"{symbol}: слишком маленький размер позиции")
                return None

            # Разместить ордер с указанием стороны позиции
            params = {'positionSide': side}
            order = self.exchange.create_market_order(
                symbol, 'buy' if side == 'LONG' else 'sell', amount, params=params
            )

            log(f"{symbol}: ОТКРЫТ {side} | Количество: {amount} | Цена: {price}")

            trade = {
                'symbol': symbol,
                'action': 'OPEN',
                'side': side,
                'amount': amount,
                'price': price,
                'time': datetime.now().isoformat(),
            }
            log_trade(trade)

            return order

        except Exception as e:
            log(f"{symbol}: ошибка открытия позиции: {e}")
            return None

    def close_position(self, symbol, side, amount):
        """Закрыть позицию"""
        try:
            # Закрыть позицию с указанием стороны
            params = {'positionSide': side}
            order = self.exchange.create_market_order(
                symbol, 'sell' if side == 'LONG' else 'buy', amount, params=params
            )

            log(f"{symbol}: ЗАКРЫТ {side} | Количество: {amount}")

            trade = {
                'symbol': symbol,
                'action': 'CLOSE',
                'side': side,
                'amount': amount,
                'time': datetime.now().isoformat(),
            }
            log_trade(trade)

            return order

        except Exception as e:
            log(f"{symbol}: ошибка закрытия позиции: {e}")
            return None

    def process_symbol(self, symbol, params):
        """Обработать один инструмент"""
        alloc = params['alloc']
        sma_s = params['sma_s']
        sma_l = params['sma_l']

        # Получить данные
        df = self.get_ohlcv(symbol)
        if df is None or len(df) < sma_l + 10:
            return

        # Подготовить данные
        df = prepare_data(df, sma_s, sma_l)
        signals = get_signals(df)
        if signals is None:
            return

        current_pos = self.get_position(symbol)
        signal = signals['signal']
        price = signals['price']

        # Если нет позиции и есть сигнал — открыть
        if current_pos is None and signal:
            balance = self.get_balance()
            if balance >= alloc:
                self.setup_leverage(symbol)
                self.open_position(symbol, signal, alloc, price)

                # Инициализировать trailing stop
                self.trail_data[symbol] = {
                    'activated': False,
                    'high': price if signal == 'LONG' else None,
                    'low': price if signal == 'SHORT' else None,
                }
                self.save_state()

        # Если есть позиция — проверить выход
        elif current_pos:
            side = current_pos['side'].upper()
            entry = current_pos['entry_price']
            amount = current_pos['amount']

            # Trailing stop логика
            trail = self.trail_data.get(symbol, {'activated': False, 'high': None, 'low': None})

            if side == 'LONG':
                # Обновить максимум
                if trail['high'] is None or price > trail['high']:
                    trail['high'] = price

                # Активация trailing
                if not trail['activated']:
                    unrealized = (price - entry) / entry
                    if unrealized >= TRAIL_ACTIVATE:
                        trail['activated'] = True
                        log(f"{symbol}: Trailing activated at {price}")

                # Проверка trailing stop
                if trail['activated']:
                    trail_price = trail['high'] * (1 - TRAIL_DIST)
                    if price <= trail_price:
                        log(f"{symbol}: TRAIL STOP hit at {price}")
                        self.close_position(symbol, 'LONG', amount)
                        self.trail_data[symbol] = {'activated': False, 'high': None, 'low': None}
                        self.save_state()
                        return

                # Проверка signal exit
                if signal == 'SHORT':
                    log(f"{symbol}: SIGNAL EXIT (death cross)")
                    self.close_position(symbol, 'LONG', amount)
                    self.trail_data[symbol] = {'activated': False, 'high': None, 'low': None}
                    self.save_state()

            elif side == 'SHORT':
                # Обновить минимум
                if trail['low'] is None or price < trail['low']:
                    trail['low'] = price

                # Активация trailing
                if not trail['activated']:
                    unrealized = (entry - price) / entry
                    if unrealized >= TRAIL_ACTIVATE:
                        trail['activated'] = True
                        log(f"{symbol}: Trailing activated at {price}")

                # Проверка trailing stop
                if trail['activated']:
                    trail_price = trail['low'] * (1 + TRAIL_DIST)
                    if price >= trail_price:
                        log(f"{symbol}: TRAIL STOP hit at {price}")
                        self.close_position(symbol, 'SHORT', amount)
                        self.trail_data[symbol] = {'activated': False, 'high': None, 'low': None}
                        self.save_state()
                        return

                # Проверка signal exit
                if signal == 'LONG':
                    log(f"{symbol}: SIGNAL EXIT (golden cross)")
                    self.close_position(symbol, 'SHORT', amount)
                    self.trail_data[symbol] = {'activated': False, 'high': None, 'low': None}
                    self.save_state()

            self.trail_data[symbol] = trail

    def run(self):
        """Главный цикл бота"""
        log("="*60)
        log("SkSred v4 Trading Bot запущен")
        log(f"Инструменты: {list(INSTRUMENTS.keys())}")
        log(f"Плечо: {LEVERAGE}x | Таймфрейм: {TIMEFRAME}")
        log(f"Интервал проверки: {CHECK_INTERVAL} сек")
        log("="*60)

        balance = self.get_balance()
        log(f"Баланс: {balance:.2f} USDT")

        while True:
            try:
                for symbol, params in INSTRUMENTS.items():
                    self.process_symbol(symbol, params)
                    time.sleep(1)  # Задержка между запросами

                log(f"Цикл завершен. Следующий через {CHECK_INTERVAL} сек...")
                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                log("Бот остановлен пользователем")
                break
            except Exception as e:
                log(f"Ошибка в главном цикле: {e}")
                time.sleep(60)

# ============================================================
# ТЕСТОВЫЙ РЕЖИМ (без реальных ордеров)
# ============================================================
class SkSredBotTest(SkSredBot):
    """Тестовый бот — логирует сигналы без исполнения"""

    def open_position(self, symbol, side, amount_usdt, price):
        log(f"[ТЕСТ] {symbol}: СИГНАЛ {side} | Сумма: {amount_usdt} USDT | Цена: {price}")
        return {'test': True}

    def close_position(self, symbol, side, amount):
        log(f"[ТЕСТ] {symbol}: ЗАКРЫТИЕ {side} | Количество: {amount}")
        return {'test': True}

    def get_position(self, symbol):
        return None

    def get_balance(self):
        return 100  # Тестовый баланс

# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("SkSred v4 Trading Bot")
    print("="*60)
    print()

    # Автозапуск на основе конфигурации
    if USE_TESTNET:
        print("Режим: Testnet")
        bot = SkSredBotTest()
    else:
        print("Режим: MAINNET (реальная торговля)")
        bot = SkSredBot()

    bot.run()
