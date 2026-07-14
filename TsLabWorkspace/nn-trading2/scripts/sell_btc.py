import hmac, hashlib, time, requests, json

API_KEY = 'DfaoUJoXxNGbMv3I3gCQw1TKWMHQjugkkb36mtDzRYNjtH7zrAwOZdr7DO4kGW1J'
API_SECRET = 'AupwcKFlh7lsYAvd3gPLZoHHwYWcLPkaEbycbF86J6lq67w3D1GDHkheIAU1YFZ3'
BASE = 'https://testnet.binance.vision'

# Получаем баланс BTC
ts = int(time.time()*1000)
qs = f'timestamp={ts}&recvWindow=5000'
sig = hmac.new(API_SECRET.encode(), qs.encode(), hashlib.sha256).hexdigest()
r = requests.get(f'{BASE}/api/v3/account?{qs}&signature={sig}', headers={'X-MBX-APIKEY': API_KEY})
account = r.json()
btc_free = 0
for b in account.get('balances', []):
    if b['asset'] == 'BTC':
        btc_free = float(b['free'])
        break

print(f'Баланс BTC: {btc_free}')

if btc_free <= 0:
    print('Нет BTC для продажи')
    exit()

# Продаём весь BTC рыночным ордером
qty = f'{btc_free:.6f}'
ts2 = int(time.time()*1000)
params = {
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'type': 'MARKET',
    'quantity': qty,
    'timestamp': str(ts2),
    'recvWindow': '5000'
}
query_str = '&'.join(f'{k}={v}' for k,v in params.items())
sig2 = hmac.new(API_SECRET.encode(), query_str.encode(), hashlib.sha256).hexdigest()
params['signature'] = sig2

r2 = requests.post(f'{BASE}/api/v3/order', params=params, headers={'X-MBX-APIKEY': API_KEY})
result = r2.json()
print(json.dumps(result, indent=2))

# Получаем баланс после продажи
ts3 = int(time.time()*1000)
qs3 = f'timestamp={ts3}&recvWindow=5000'
sig3 = hmac.new(API_SECRET.encode(), qs3.encode(), hashlib.sha256).hexdigest()
r3 = requests.get(f'{BASE}/api/v3/account?{qs3}&signature={sig3}', headers={'X-MBX-APIKEY': API_KEY})
acc = r3.json()
print()
print('=== Баланс после продажи ===')
for b in acc.get('balances', []):
    free = float(b['free'])
    if free > 0:
        print(f"  {b['asset']}: {free}")
