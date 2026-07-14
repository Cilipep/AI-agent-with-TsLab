import json, urllib.request, math

# Получаем данные
url = 'https://api.binance.com/api/v3/klines?symbol=DOGEUSDT&interval=1h&limit=168'
data = json.loads(urllib.request.urlopen(url).read())

closes = [float(d[4]) for d in data]
highs = [float(d[2]) for d in data]
lows = [float(d[3]) for d in data]
volumes = [float(d[5]) for d in data]

# RSI
def rsi(prices, period=14):
    deltas = [prices[i]-prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period-1) + gains[i]) / period
        avg_loss = (avg_loss * (period-1) + losses[i]) / period
    rs = avg_gain / avg_loss if avg_loss > 0 else 100
    return 100 - 100/(1+rs)

# EMA
def ema(prices, period):
    k = 2/(period+1)
    result = [prices[0]]
    for p in prices[1:]:
        result.append(p*k + result[-1]*(1-k))
    return result

# Bollinger
def bollinger(prices, period=20):
    sma = sum(prices[-period:]) / period
    std = math.sqrt(sum((x-sma)**2 for x in prices[-period:]) / period)
    return sma, sma+2*std, sma-2*std

# ATR
tr = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1])) for i in range(1, len(closes))]
atr = sum(tr[-14:]) / 14

rsi_val = rsi(closes)
ema9 = ema(closes, 9)[-1]
ema21 = ema(closes, 21)[-1]
ema50 = ema(closes, 50)[-1]
sma20, bb_upper, bb_lower = bollinger(closes)

price = closes[-1]

print('=== DOGEUSDT Анализ ===')
print(f'Цена:      ${price:.6f}')
print(f'RSI(14):   {rsi_val:.1f}')
print(f'EMA9:      ${ema9:.6f}')
print(f'EMA21:     ${ema21:.6f}')
print(f'EMA50:     ${ema50:.6f}')
print(f'BB Upper:  ${bb_upper:.6f}')
print(f'BB Middle: ${sma20:.6f}')
print(f'BB Lower:  ${bb_lower:.6f}')
print(f'ATR(14):   ${atr:.6f} ({atr/price*100:.2f}%)')
print()

# Тренд
if ema9 > ema21 > ema50:
    trend = 'ВОСХОДЯЩИЙ 🟢'
elif ema9 < ema21 < ema50:
    trend = 'НИСХОДЯЩИЙ 🔴'
else:
    trend = 'БОКОВОЙ 🟡'
print(f'Тренд:     {trend}')

# Сигнал
if rsi_val < 30:
    signal = 'ПОКУПКА (RSI перепродан)'
elif rsi_val > 70:
    signal = 'ПРОДАЖА (RSI перекуплен)'
elif price < bb_lower:
    signal = 'ПОКУПКА (ниже BB)'
elif price > bb_upper:
    signal = 'ПРОДАЖА (выше BB)'
elif ema9 > ema21 and price > ema21:
    signal = 'ПОКУПКА (тренд вверх)'
elif ema9 < ema21 and price < ema21:
    signal = 'ПРОДАЖА (тренд вниз)'
else:
    signal = 'НЕЙТРАЛЬНО'
print(f'Сигнал:    {signal}')

# SL/TP
sl_long = price - 2*atr
tp_long = price + 3*atr
sl_short = price + 2*atr
tp_short = price - 3*atr

print()
print('=== Стратегия LONG ===')
print(f'Entry:        ${price:.6f}')
print(f'Stop Loss:    ${sl_long:.6f} (-{2*atr/price*100:.1f}%)')
print(f'Take Profit:  ${tp_long:.6f} (+{3*atr/price*100:.1f}%)')
print(f'R:R =         1.5')

print()
print('=== Стратегия SHORT ===')
print(f'Entry:        ${price:.6f}')
print(f'Stop Loss:    ${sl_short:.6f} (-{2*atr/price*100:.1f}%)')
print(f'Take Profit:  ${tp_short:.6f} (+{3*atr/price*100:.1f}%)')
print(f'R:R =         1.5')
