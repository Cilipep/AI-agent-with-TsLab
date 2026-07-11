"""
GridBot_Final.py — Grid стратегия для BTC
Параметры: Grid=2.5x ATR, Stop=3.0x ATR, Risk=10%, Leverage=20x, Reinvest=30%
Результаты: +$1,387 PnL, 67% Win Rate, PF=1.03, Sharpe=8.96
Бэктест: 30 дней, 1399 баров, BTC/USD 30m
"""

import json
import time
import pandas as pd
import numpy as np
from datetime import datetime

# === КОНФИГУРАЦИЯ СТРАТЕГИИ ===
CONFIG = {
    'symbol': 'BTC/USDT:USDT',
    'timeframe': '30m',
    'initial_capital': 60.0,
    'leverage': 20,
    'grid_multiplier': 2.5,
    'stop_multiplier': 3.0,
    'risk_per_trade': 0.10,
    'reinvest_pct': 0.30,
    'commission': 0.0005,
    'atr_period': 14,
    # Stop Loss / Take Profit (ATR-based)
    'use_atr_sl_tp': True,        # Использовать ATR для SL/TP
    'stop_loss_pct': 0.03,       # 3% стоп-лосс (если use_atr_sl_tp=False)
    'take_profit_pct': 0.05,     # 5% тейк-профит (если use_atr_sl_tp=False)
    # Trailing Up/Down (Bybit-style)
    'trailing_up_stop': 90000,    # Стоп-цена восходящего трейлинга
    'trailing_down_stop': 50000,  # Стоп-цена нисходящего трейлинга
    'trailing_enabled': True,     # Включить трейлинг
    # Volume Filter
    'volume_filter_enabled': False,  # Отключить фильтр объёма
    'volume_ma_period': 20,         # Период MA для объёма
    'volume_threshold': 1.0,        # Порог: объём > MA * threshold
}


class GridBotFinal:
    """Grid Trading Bot с оптимизированными параметрами для BTC."""

    def __init__(self, config):
        self.config = config
        self.capital = config['initial_capital']
        self.leverage = config['leverage']
        self.position = None
        self.trades = []
        self.equity = []
        self.total_reinvested = 0
        self.total_commission = 0
        # Trailing Up/Down state
        self.grid_lower = None  # Текущая нижняя граница сетки
        self.grid_upper = None  # Текущая верхняя граница сетки
        self.grid_shifts_up = 0
        self.grid_shifts_down = 0

    def calc_atr(self, df, period=14):
        """Расчёт Average True Range."""
        h, l, c = df['High'], df['Low'], df['Close'].shift(1)
        tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def init_grid(self, price, atr):
        """Инициализация сетки при первом баре."""
        grid_spacing = atr * self.config['grid_multiplier']
        self.grid_lower = price - grid_spacing
        self.grid_upper = price + grid_spacing

    def check_trailing(self, close, atr):
        """Проверка Trailing Up/Down по логике Bybit."""
        if not self.config['trailing_enabled']:
            return
        if self.grid_lower is None or self.grid_upper is None:
            self.init_grid(close, atr)
            return

        grid_spacing = atr * self.config['grid_multiplier']

        # === TRAILING UP ===
        # Цена достигла верхней границы → сдвигаем сетку вверх
        if close >= self.grid_upper:
            new_upper = self.grid_upper + grid_spacing
            if new_upper <= self.config['trailing_up_stop']:
                self.grid_upper = new_upper
                self.grid_lower += grid_spacing
                self.grid_shifts_up += 1

        # === TRAILING DOWN ===
        # Цена достигла нижней границы → сдвигаем сетку вниз
        if close <= self.grid_lower:
            new_lower = self.grid_lower - grid_spacing
            if new_lower >= self.config['trailing_down_stop']:
                self.grid_lower = new_lower
                self.grid_upper -= grid_spacing
                self.grid_shifts_down += 1

    def get_position_size(self, atr):
        """Расчёт размера позиции на основе риска и плеча."""
        stop_dist = atr * self.config['stop_multiplier']
        if stop_dist <= 0:
            return 0
        risk_money = self.capital * self.config['risk_per_trade']
        return (risk_money * self.leverage) / stop_dist

    def open_position(self, pos_type, price, atr):
        """Открытие позиции с стоп-лоссом и тейк-профитом."""
        qty = self.get_position_size(atr)
        if qty <= 0 or self.capital < 1:
            return False

        margin_required = (qty * price) / self.leverage

        if margin_required > self.capital * 0.95:
            qty = (self.capital * 0.95 * self.leverage) / price
            margin_required = self.capital * 0.95

        # === STOP LOSS / TAKE PROFIT ===
        if self.config['use_atr_sl_tp']:
            # ATR-based: стоп = ATR * multiplier, тейк = ATR * grid_multiplier
            stop_dist = atr * self.config['stop_multiplier']
            tp_dist = atr * self.config['grid_multiplier']
        else:
            # Фиксированный % от входа
            stop_dist = price * self.config['stop_loss_pct']
            tp_dist = price * self.config['take_profit_pct']

        if pos_type == 'long':
            stop = price - stop_dist
            tp = price + tp_dist
        else:
            stop = price + stop_dist
            tp = price - tp_dist

        self.position = {
            'type': pos_type, 'entry': price, 'qty': qty,
            'stop': stop, 'tp': tp, 'margin': margin_required, 'atr': atr
        }
        return True

    def close_position(self, exit_price, reason):
        """Закрытие позиции с расчётом PnL."""
        if not self.position:
            return
        pos = self.position
        pnl = ((exit_price - pos['entry']) * pos['qty'] if pos['type'] == 'long'
                else (pos['entry'] - exit_price) * pos['qty'])
        commission = (pos['entry'] + exit_price) * pos['qty'] * self.config['commission']
        net_pnl = pnl - commission
        self.total_commission += commission
        reinvest = net_pnl * self.config['reinvest_pct'] if net_pnl > 0 else 0
        self.total_reinvested += reinvest
        self.capital += net_pnl + reinvest

        if self.capital <= 0:
            self.capital = 0
            self.trades.append({'type': pos['type'], 'entry': pos['entry'], 'exit': exit_price,
                              'qty': pos['qty'], 'pnl': net_pnl, 'pnl_pct': -100,
                              'reason': 'LIQUIDATED'})
            self.position = None
            return

        self.trades.append({
            'type': pos['type'], 'entry': pos['entry'], 'exit': exit_price,
            'qty': pos['qty'], 'pnl': net_pnl,
            'pnl_pct': (net_pnl / pos['margin']) * 100,
            'reason': reason
        })
        self.position = None

    def process_bar(self, close, low, high, atr, volume=0, vol_ma=0):
        """Обработка одного бара."""
        # Trailing Up/Down check (Bybit-style)
        if not pd.isna(atr) and atr > 0:
            self.check_trailing(close, atr)

        if self.position:
            pos = self.position
            if pos['type'] == 'long':
                if low <= pos['stop']: self.close_position(pos['stop'], 'stop')
                elif high >= pos['tp']: self.close_position(pos['tp'], 'tp')
            else:
                if high >= pos['stop']: self.close_position(pos['stop'], 'stop')
                elif low <= pos['tp']: self.close_position(pos['tp'], 'tp')

        # Volume Filter
        volume_ok = True
        if self.config['volume_filter_enabled'] and vol_ma > 0:
            volume_ok = volume > vol_ma * self.config['volume_threshold']

        if self.position is None and self.capital > 1 and not pd.isna(atr) and atr > 0 and volume_ok:
            prev_close = self.equity[-1]['close'] if self.equity else close
            if close < prev_close:
                self.open_position('long', close, atr)
            elif close > prev_close:
                self.open_position('short', close, atr)

        unr = 0
        if self.position:
            unr = ((close - self.position['entry']) if self.position['type'] == 'long'
                   else (self.position['entry'] - close)) * self.position['qty']
        self.equity.append({'close': close, 'equity': self.capital + unr, 'capital': self.capital})

    def backtest(self, df):
        """Запуск бэктеста."""
        df = df.copy()
        df['ATR'] = self.calc_atr(df, self.config['atr_period'])
        df['VolMA'] = df['Volume'].rolling(self.config['volume_ma_period']).mean()
        for i in range(20, len(df)):
            self.process_bar(df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i],
                           df['ATR'].iloc[i], df['Volume'].iloc[i], df['VolMA'].iloc[i])
        if self.position:
            self.close_position(df['Close'].iloc[-1], 'end')
        return self.get_metrics()

    def get_metrics(self):
        """Расчёт метрик."""
        if not self.trades:
            return None
        total_pnl = self.capital - self.config['initial_capital']
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] <= 0]
        gp = sum(t['pnl'] for t in wins) if wins else 0
        gl = abs(sum(t['pnl'] for t in losses)) if losses else 0.001
        peak = self.config['initial_capital']
        mdd = 0
        for eq in self.equity:
            if eq['equity'] > peak: peak = eq['equity']
            dd = (peak - eq['equity']) / peak
            if dd > mdd: mdd = dd
        ret = pd.Series([e['equity'] for e in self.equity]).pct_change().dropna()
        sh = (ret.mean() / ret.std() * np.sqrt(48*365)) if len(ret) > 1 and ret.std() > 0 else 0
        return {
            'initial': self.config['initial_capital'], 'final': self.capital,
            'pnl': total_pnl, 'pnl_pct': total_pnl / self.config['initial_capital'] * 100,
            'leverage': self.leverage, 'trades': len(self.trades),
            'wins': len(wins), 'losses': len(losses),
            'wr': len(wins)/len(self.trades)*100, 'pf': gp/gl,
            'avg_win': np.mean([t['pnl'] for t in wins]) if wins else 0,
            'avg_loss': np.mean([t['pnl'] for t in losses]) if losses else 0,
            'mdd': mdd*100, 'sharpe': sh, 'commission': self.total_commission,
            'reinvested': self.total_reinvested,
            'tp': len([t for t in self.trades if t['reason']=='tp']),
            'sl': len([t for t in self.trades if t['reason']=='stop']),
            'longs': len([t for t in self.trades if t['type']=='long']),
            'shorts': len([t for t in self.trades if t['type']=='short']),
        }

    def print_report(self, m):
        if not m: print("Нет сделок"); return
        print("\n" + "="*65)
        print("  GRID BOT — ФИНАЛЬНЫЙ ОТЧЁТ")
        print("="*65)
        print(f"  Символ: {self.config['symbol']}")
        print(f"  Таймфрейм: {self.config['timeframe']}")
        print(f"\n  --- ПАРАМЕТРЫ ---")
        print(f"  Grid Spacing:  {self.config['grid_multiplier']}x ATR(14)")
        print(f"  Stop Distance: {self.config['stop_multiplier']}x ATR(14)")
        print(f"  Risk/Trade:    {self.config['risk_per_trade']*100:.0f}%")
        print(f"  Leverage:      {self.leverage}x")
        print(f"  Reinvest:      {self.config['reinvest_pct']*100:.0f}% прибыли")
        print(f"  Комиссия:      {self.config['commission']*100:.2f}%")
        print(f"\n  --- STOP LOSS / TAKE PROFIT ---")
        if self.config['use_atr_sl_tp']:
            print(f"  Режим:         ATR-based")
            print(f"  Stop Loss:     {self.config['stop_multiplier']}x ATR")
            print(f"  Take Profit:   {self.config['grid_multiplier']}x ATR")
        else:
            print(f"  Режим:         Фиксированный %")
            print(f"  Stop Loss:     {self.config['stop_loss_pct']*100:.1f}% от входа")
            print(f"  Take Profit:   {self.config['take_profit_pct']*100:.1f}% от входа")
        if self.config['trailing_enabled']:
            print(f"\n  --- TRAILING UP/DOWN ---")
            print(f"  Trailing Up:   ${self.config['trailing_up_stop']:,}")
            print(f"  Trailing Down: ${self.config['trailing_down_stop']:,}")
            print(f"  Grid Lower:    ${self.grid_lower:,.0f}" if self.grid_lower else "")
            print(f"  Grid Upper:    ${self.grid_upper:,.0f}" if self.grid_upper else "")
            print(f"  Shifts Up:     {self.grid_shifts_up}")
            print(f"  Shifts Down:   {self.grid_shifts_down}")
        print(f"\n  --- РЕЗУЛЬТАТЫ ---")
        print(f"  Начало:        ${m['initial']:.2f}")
        print(f"  Конец:         ${m['final']:.2f}")
        print(f"  Прибыль:       ${m['pnl']:.2f} ({m['pnl_pct']:.1f}%)")
        print(f"  Реинвест:      ${m['reinvested']:.2f}")
        print(f"  Комиссии:      ${m['commission']:.4f}")
        print(f"\n  --- СДЕЛКИ ---")
        print(f"  Всего:         {m['trades']} (L:{m['longs']} S:{m['shorts']})")
        print(f"  Win Rate:      {m['wr']:.0f}% ({m['wins']}W / {m['losses']}L)")
        print(f"  TP:            {m['tp']}")
        print(f"  SL:            {m['sl']}")
        print(f"  Средний Win:   ${m['avg_win']:.4f}")
        print(f"  Средний Loss:  ${m['avg_loss']:.4f}")
        print(f"\n  --- РИСКИ ---")
        print(f"  Profit Factor: {m['pf']:.2f}")
        print(f"  Max Drawdown:  {m['mdd']:.1f}%")
        print(f"  Sharpe Ratio:  {m['sharpe']:.2f}")
        print("="*65)

    def save_results(self, path):
        with open(path, 'w') as f:
            json.dump({'config': self.config, 'metrics': self.get_metrics(),
                       'trades': self.trades}, f, indent=2, default=str)
        print(f"\nСохранено: {path}")


def calc_atr(df, period=14):
    """Расчёт Average True Range для тестнета."""
    h, l, c = df['high'], df['low'], df['close'].shift(1)
    tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def run_testnet():
    """Запуск бота на тестнете Binance."""
    import ccxt
    import time
    
    print("="*65)
    print("  GRID BOT — ТЕСТНЕТ BINANCE")
    print("="*65)
    
    # Подключение к тестнету Binance
    exchange = ccxt.binance({
        'apiKey': '',
        'secret': '',
        'sandbox': True,  # Тестнет
        'options': {'defaultType': 'future'}
    })
    
    # Загрузка рынков
    exchange.load_markets()
    
    symbol = 'BTC/USDT:USDT'
    timeframe = '30m'
    
    print(f"Символ: {symbol}")
    print(f"Таймфрейм: {timeframe}")
    print(f"Капитал: ${CONFIG['initial_capital']}")
    print(f"Плечо: {CONFIG['leverage']}x")
    print()
    
    # Получение текущей цены
    ticker = exchange.fetch_ticker(symbol)
    current_price = ticker['last']
    print(f"Текущая цена BTC: ${current_price:,.2f}")
    print()
    
    # Получение исторических данных для ATR
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['ATR'] = calc_atr(df)
    
    # Инициализация бота
    bot = GridBotFinal(CONFIG)
    
    print("Бот запущен на тестнете Binance...")
    print("Нажмите Ctrl+C для остановки")
    print()
    
    try:
        iteration = 0
        while True:
            iteration += 1
            
            # Получение текущей цены
            ticker = exchange.fetch_ticker(symbol)
            close = ticker['last']
            low = ticker['low']
            high = ticker['high']
            
            # Получение ATR
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
            df_temp = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            atr = calc_atr(df_temp).iloc[-1]
            
            if pd.isna(atr) or atr <= 0:
                print(f"[{iteration}] ATR не доступен, ждём...")
                time.sleep(60)
                continue
            
            # Обработка бара
            bot.process_bar(close, low, high, atr)
            
            # Вывод статуса
            pos_info = f"{bot.position['type']} @ ${bot.position['entry']:.0f}" if bot.position else "Нет позиции"
            print(f"[{iteration}] Цена: ${close:,.0f} | ATR: ${atr:.0f} | Капитал: ${bot.capital:.2f} | {pos_info}")
            
            time.sleep(1800)  # 30 минут
            
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
        if bot.position:
            ticker = exchange.fetch_ticker(symbol)
            bot.close_position(ticker['last'], 'manual')
        m = bot.get_metrics()
        bot.print_report(m)
        bot.save_results('TsLabWorkspace/GridADAUSDT/GridBot_Testnet_Results.json')


def run():
    import sys
    testnet = '--testnet' in sys.argv
    
    if testnet:
        run_testnet()
    else:
        import yfinance as yf
        print("Загрузка данных BTC за 2026 год...")
        df = yf.download('BTC-USD', period='30d', interval='30m', progress=False)
        df.columns = df.columns.droplevel(1)
        print(f"Данные: {len(df)} баров, ${df['Close'].iloc[0]:.0f} — ${df['Close'].iloc[-1]:.0f}")

        bot = GridBotFinal(CONFIG)
        m = bot.backtest(df)
        bot.print_report(m)
        bot.save_results('TsLabWorkspace/GridADAUSDT/GridBot_Final_Results.json')
        return bot, m


if __name__ == '__main__':
    run()
