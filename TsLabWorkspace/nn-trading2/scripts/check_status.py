import hmac, hashlib, time, requests, json
from datetime import datetime

API_KEY = 'DfaoUJoXxNGbMv3I3gCQw1TKWMHQjugkkb36mtDzRYNjtH7zrAwOZdr7DO4kGW1J'
API_SECRET = 'AupwcKFlh7lsYAvd3gPLZoHHwYWcLPkaEbycbF86J6lq67w3D1GDHkheIAU1YFZ3'
BASE = 'https://testnet.binance.vision'

def signed_get(path, params=None):
    if params is None:
        params = {}
    params['timestamp'] = str(int(time.time()*1000))
    params['recvWindow'] = '5000'
    query_str = '&'.join(f'{k}={v}' for k,v in params.items())
    sig = hmac.new(API_SECRET.encode(), query_str.encode(), hashlib.sha256).hexdigest()
    headers = {'X-MBX-APIKEY': API_KEY}
    r = requests.get(f'{BASE}{path}?{query_str}&signature={sig}', headers=headers)
    return r.json()

# 1. Баланс
print('╔══════════════════════════════════════════════════════════════════════╗')
print('║                    ТЕКУЩИЙ СТАТУС                                 ║')
print('╠══════════════════════════════════════════════════════════════════════╣')

account = signed_get('/api/v3/account')
balances = {}
for b in account.get('balances', []):
    free = float(b['free'])
    locked = float(b['locked'])
    if free > 0 or locked > 0:
        balances[b['asset']] = {'free': free, 'locked': locked}

print('║  БАЛАНСЫ:                                                          ║')
print('║  ─────────────────────────────────────────────────────────────────  ║')
for asset, bal in sorted(balances.items()):
    if asset in ['USDT', 'BTC', 'ETH', 'DOGE', 'BNB']:
        print(f'║  {asset:6s}:  {bal["free"]:>15.8f}  (locked: {bal["locked"]:.8f})    ║')
print('╠══════════════════════════════════════════════════════════════════════╣')

# 2. Открытые ордера
print('║  ОТКРЫТЫЕ ОРДЕРА:                                                   ║')
print('║  ─────────────────────────────────────────────────────────────────  ║')

orders = signed_get('/api/v3/openOrders')
if isinstance(orders, list) and len(orders) > 0:
    for o in orders:
        created = datetime.fromtimestamp(o['time']/1000).strftime('%H:%M:%S')
        print(f'║  {o["symbol"]:10s} │ {o["type"]:20s} │ {o["side"]:4s} │ {o["origQty"]:>12s} │ Price: {o["price"]:>12s} │ Stop: {o.get("stopPrice","N/A"):>12s} ║')
else:
    print('║  Нет открытых ордеров                                               ║')

print('╠══════════════════════════════════════════════════════════════════════╣')

# 3. Последние сделки
print('║  ПОСЛЕДНИЕ СДЕЛКИ (BTCUSDT + DOGEUSDT):                             ║')
print('║  ─────────────────────────────────────────────────────────────────  ║')

for symbol in ['BTCUSDT', 'DOGEUSDT']:
    trades = signed_get('/api/v3/myTrades', {'symbol': symbol, 'limit': 5})
    if isinstance(trades, list):
        for t in trades[-3:]:
            side = 'BUY ' if t['isBuyer'] else 'SELL'
            time_str = datetime.fromtimestamp(t['time']/1000).strftime('%m-%d %H:%M')
            print(f'║  {time_str} │ {symbol:10s} │ {side} │ {t["qty"]:>12s} @ {t["price"]:>12s} ║')

print('╚══════════════════════════════════════════════════════════════════════╝')

# Текущая цена DOGE
price_data = requests.get(f'{BASE}/api/v3/ticker/price?symbol=DOGEUSDT').json()
doge_price = float(price_data['price'])
print(f'\nТекущая цена DOGE: ${doge_price:.6f}')
print(f'P&L от покупки:   ${((doge_price - 0.0744) * 20030):+.2f} USDT ({((doge_price/0.0744 - 1)*100):+.2f}%)')
