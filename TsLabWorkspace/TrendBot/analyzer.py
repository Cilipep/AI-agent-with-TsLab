"""
TrendBot v1 — Trend Following Signal Generator
Strategy: EMA(50/200) + RSI correction + OBV confirmation
Entry: Pullback to EMA50, RSI 40-50, bullish engulfing + volume spike
SL: Under EMA200 | TP: Previous high
"""
import os
import json
import glob
import pandas as pd
import numpy as np
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

CSV_DIR = r"C:\Users\i59400f\Documents\TSLab 3.0"
SIGNALS_DIR = os.path.join(os.path.dirname(__file__), "signals")


def ema(arr, period):
    return pd.Series(arr).ewm(span=period, adjust=False).mean().values


def sma(arr, period):
    return pd.Series(arr).rolling(period, min_periods=period).mean().values


def rsi(close, period=14):
    delta = pd.Series(close).diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).values


def obv(close, volume):
    obv_vals = np.zeros(len(close))
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            obv_vals[i] = obv_vals[i-1] + volume[i]
        elif close[i] < close[i-1]:
            obv_vals[i] = obv_vals[i-1] - volume[i]
        else:
            obv_vals[i] = obv_vals[i-1]
    return obv_vals


def is_bullish_engulfing(open_arr, high_arr, low_arr, close_arr, i):
    """Check for bullish engulfing pattern"""
    if i < 1:
        return False

    # Current candle
    curr_body = close_arr[i] - open_arr[i]
    curr_range = high_arr[i] - low_arr[i]

    # Previous candle
    prev_body = close_arr[i-1] - open_arr[i-1]

    # Bullish engulfing:
    # 1. Previous candle is bearish (or small)
    # 2. Current candle is bullish
    # 3. Current body engulfs previous body
    prev_bearish = prev_body <= 0
    curr_bullish = curr_body > 0
    engulfs = close_arr[i] > open_arr[i-1] and open_arr[i] < close_arr[i-1]

    return prev_bearish and curr_bullish and engulfs


def resample_1h(df):
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    ohlcv = df.resample('1h').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min',
        'Close': 'last', 'Volume': 'sum'
    }).dropna()
    return ohlcv.reset_index()


def analyze_pair(ticker, df):
    """Analyze one pair and return signal"""
    cfg = CONFIG['strategy']
    risk_cfg = CONFIG['risk']

    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values
    opn = df['Open'].values
    volume = df['Volume'].values
    n = len(close)

    if n < 250:
        return None

    # Indicators
    ema_fast = ema(close, cfg['ema_fast'])
    ema_slow = ema(close, cfg['ema_slow'])
    rsi_vals = rsi(close, cfg['rsi_period'])
    obv_vals = obv(close, volume)
    obv_sma = sma(obv_vals, cfg['obv_sma_period'])
    vol_sma = sma(volume, 20)

    i = n - 1
    if np.isnan(ema_fast[i]) or np.isnan(ema_slow[i]) or np.isnan(rsi_vals[i]):
        return None

    # === TREND CHECK ===
    # EMA50 > EMA200 = uptrend
    uptrend = ema_fast[i] > ema_slow[i]
    downtrend = ema_fast[i] < ema_slow[i]

    # Price relative to EMAs
    above_ema50 = close[i] > ema_fast[i]
    below_ema50 = close[i] < ema_fast[i]
    above_ema200 = close[i] > ema_slow[i]
    below_ema200 = close[i] < ema_slow[i]

    # === RSI CORRECTION ===
    rsi_val = rsi_vals[i]
    rsi_in_correction = cfg['rsi_correction_low'] <= rsi_val <= cfg['rsi_correction_high']

    # === OBV CONFIRMATION ===
    obv_rising = obv_vals[i] > obv_sma[i] if not np.isnan(obv_sma[i]) else True

    # === VOLUME CHECK ===
    vol_avg = vol_sma[i] if not np.isnan(vol_sma[i]) else volume[i]
    vol_spike = volume[i] > vol_avg * cfg['min_volume_ratio']

    # === CANDLESTICK PATTERNS ===
    bullish_engulfing = is_bullish_engulfing(opn, high, low, close, i)
    bullish_candle = close[i] > opn[i]
    strong_bullish = bullish_candle and (close[i] - opn[i]) > (high[i] - low[i]) * 0.6

    # === PREVIOUS HIGH (for TP) ===
    lookback = risk_cfg['tp_lookback']
    prev_high = max(high[max(0, i-lookback):i]) if i >= lookback else high[i-1]

    # === SL LEVEL (EMA200) ===
    sl_level = ema_slow[i]

    # === SIGNAL SCORING ===
    signal = {
        'ticker': ticker,
        'price': round(close[i], 6),
        'timestamp': str(df['Date'].iloc[i]),
        'indicators': {
            'ema50': round(ema_fast[i], 6),
            'ema200': round(ema_slow[i], 6),
            'rsi': round(rsi_val, 2),
            'obv': round(obv_vals[i], 0),
            'obv_sma': round(obv_sma[i], 0) if not np.isnan(obv_sma[i]) else None,
            'volume': round(volume[i], 0),
            'vol_avg': round(vol_avg, 0),
        },
        'conditions': {
            'uptrend': uptrend,
            'downtrend': downtrend,
            'above_ema50': above_ema50,
            'below_ema50': below_ema50,
            'above_ema200': above_ema200,
            'below_ema200': below_ema200,
            'rsi_correction': rsi_in_correction,
            'obv_rising': obv_rising,
            'vol_spike': vol_spike,
            'bullish_engulfing': bullish_engulfing,
            'strong_bullish': strong_bullish,
        }
    }

    # LONG conditions (from article):
    # 1. Uptrend (EMA50 > EMA200)
    # 2. Pullback to EMA50 (price near/below EMA50 but above EMA200)
    # 3. RSI 40-50 (correction, not oversold)
    # 4. OBV rising
    # 5. Bullish engulfing or strong bullish candle
    # 6. Volume spike

    long_score = 0
    long_reasons = []

    if uptrend:
        long_score += 2
        long_reasons.append("uptrend")
    if below_ema50 and above_ema200:
        long_score += 1.5
        long_reasons.append("pullback_to_ema50")
    elif above_ema50:
        long_score += 0.5
        long_reasons.append("above_ema50")
    if rsi_in_correction:
        long_score += 1
        long_reasons.append("rsi_correction")
    if obv_rising:
        long_score += 0.5
        long_reasons.append("obv_rising")
    if bullish_engulfing:
        long_score += 1.5
        long_reasons.append("bullish_engulfing")
    elif strong_bullish:
        long_score += 1
        long_reasons.append("strong_bullish")
    if vol_spike:
        long_score += 0.5
        long_reasons.append("vol_spike")

    # SHORT conditions (mirror)
    short_score = 0
    short_reasons = []

    if downtrend:
        short_score += 2
        short_reasons.append("downtrend")
    if above_ema50 and below_ema200:
        short_score += 1.5
        short_reasons.append("rally_to_ema50")
    if rsi_val > 60:
        short_score += 1
        short_reasons.append("rsi_overbought")
    if not obv_rising:
        short_score += 0.5
        short_reasons.append("obv_falling")
    if close[i] < opn[i]:
        short_score += 1
        short_reasons.append("bearish_candle")

    signal['score'] = {
        'long': round(long_score, 1),
        'short': round(short_score, 1),
    }
    signal['reasons'] = {
        'long': long_reasons,
        'short': short_reasons,
    }

    # Decision
    min_score = 4.0

    if long_score >= min_score:
        # Calculate risk/reward
        risk = close[i] - sl_level
        reward = prev_high - close[i]
        rr = reward / risk if risk > 0 else 0

        if rr >= risk_cfg['risk_reward_min']:
            signal['action'] = 'LONG'
            signal['confidence'] = round(long_score / 7.0 * 100, 1)
            signal['sl'] = round(sl_level, 6)
            signal['tp'] = round(prev_high, 6)
            signal['rr'] = round(rr, 2)
        else:
            signal['action'] = 'HOLD'
            signal['confidence'] = 0
            signal['skip_reason'] = f"RR={rr:.2f} < {risk_cfg['risk_reward_min']}"
    elif short_score >= min_score:
        signal['action'] = 'SHORT'
        signal['confidence'] = round(short_score / 5.0 * 100, 1)
        signal['sl'] = round(ema_slow[i], 6)
        signal['tp'] = round(min(low[max(0, i-20):i]), 6) if i >= 20 else round(low[i-1], 6)
    else:
        signal['action'] = 'HOLD'
        signal['confidence'] = 0

    return signal


def main():
    os.makedirs(SIGNALS_DIR, exist_ok=True)

    pairs = CONFIG['pairs']
    all_signals = []
    actions = {'LONG': [], 'SHORT': [], 'HOLD': []}

    print(f"TrendBot v1 — Trend Following Signals")
    print(f"{'='*70}")
    print(f"Strategy: EMA({CONFIG['strategy']['ema_fast']}/{CONFIG['strategy']['ema_slow']}) + RSI + OBV")
    print(f"Entry: Pullback to EMA50 + RSI correction + Engulfing + Volume")
    print(f"SL: EMA200 | TP: Previous {CONFIG['risk']['tp_lookback']} bars high")
    print(f"{'='*70}")

    for ticker in pairs:
        csv_path = os.path.join(CSV_DIR, f"{ticker}USD_PERP.csv")
        if not os.path.exists(csv_path):
            print(f"{ticker}: CSV not found")
            continue

        try:
            df = pd.read_csv(csv_path)
            df_1h = resample_1h(df)
            signal = analyze_pair(ticker, df_1h)

            if signal:
                all_signals.append(signal)
                actions[signal['action']].append(signal)

                emoji = '🟢' if signal['action'] == 'LONG' else '🔴' if signal['action'] == 'SHORT' else '⚪'
                rr_str = f"RR={signal['rr']}" if 'rr' in signal else ""
                print(f"{emoji} {ticker:<6} {signal['action']:<6} "
                      f"Score={signal['score']['long']:.1f}/{signal['score']['short']:.1f} "
                      f"RSI={signal['indicators']['rsi']:.1f} {rr_str}")
        except Exception as e:
            print(f"{ticker}: Error - {e}")

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"LONG signals:  {len(actions['LONG'])}")
    print(f"SHORT signals: {len(actions['SHORT'])}")
    print(f"HOLD:          {len(actions['HOLD'])}")

    if actions['LONG']:
        print(f"\n🟢 LONG (Trend Following):")
        for s in sorted(actions['LONG'], key=lambda x: x['confidence'], reverse=True):
            reasons = ", ".join(s['reasons']['long'][:3])
            print(f"  {s['ticker']:<6} conf={s['confidence']:.0f}% "
                  f"SL={s['sl']} TP={s['tp']} RR={s['rr']}")
            print(f"         reasons: {reasons}")

    if actions['SHORT']:
        print(f"\n🔴 SHORT:")
        for s in sorted(actions['SHORT'], key=lambda x: x['confidence'], reverse=True):
            print(f"  {s['ticker']:<6} conf={s['confidence']:.0f}%")

    # Save
    output = {
        'timestamp': datetime.now().isoformat(),
        'config': CONFIG['strategy'],
        'signals': all_signals,
        'summary': {
            'long': len(actions['LONG']),
            'short': len(actions['SHORT']),
            'hold': len(actions['HOLD']),
        }
    }

    out_path = os.path.join(SIGNALS_DIR, f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    latest_path = os.path.join(SIGNALS_DIR, "latest.json")
    with open(latest_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSignals saved to {out_path}")


if __name__ == "__main__":
    main()
