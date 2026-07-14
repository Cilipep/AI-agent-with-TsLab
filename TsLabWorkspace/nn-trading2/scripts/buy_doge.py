import hmac, hashlib, time, requests, json

API_KEY = 'DfaoUJoXxNGbMv3I3gCQw1TKWMHQjugkkb36mtDzRYNjtH7zrAwOZdr7DO4kGW1J'
API_SECRET = 'AupwcKFlh7lsYAvd3gPLZoHHwYWcLPkaEbycbF86J6lq67w3D1GDHkheIAU1YFZ3'
BASE = 'https://testnet.binance.vision'

def signed_request(method, path, params=None):
    if params is None:
        params = {}
    params['timestamp'] = str(int(time.time()*1000))
    params['recvWindow'] = '5000'
    query_str = '&'.join(f'{k}={v}' for k,v in params.items())
    sig = hmac.new(API_SECRET.encode(), query_str.encode(), hashlib.sha256).hexdigest()
    params['signature'] = sig
    headers = {'X-MBX-APIKEY': API_KEY}
    if method == 'POST':
        r = requests.post(f'{BASE}{path}', params=params, headers=headers)
    else:
        r = requests.get(f'{BASE}{path}?{query_str}&signature={sig}', headers=headers)
    return r.json()

# Получаем баланс USDT
account = signed_request('GET', '/api/v3/account')
usdt_free = 0
doge_free = 0
for b in account.get('balances', []):
    if b['asset'] == 'USDT':
        usdt_free = float(b['free'])
    if b['asset'] == 'DOGE':
        doge_free = float(b['free'])

print(f'Баланс USDT: {usdt_free}')
print(f'Баланс DOGE: {doge_free}')

# Получаем текущую цену
price_data = requests.get(f'{BASE}/api/v3/ticker/price?symbol=DOGEUSDT').json()
current_price = float(price_data['price'])
print(f'Цена DOGE: ${current_price:.6f}')

# Рассчитываем количество (2% депозита)
position_usdt = usdt_free * 0.02
qty = position_usdt / current_price

# Округляем до 1 DOGE (минимальный шаг)
qty = int(qty)

print(f'Покупаем: {qty} DOGE за ~${qty * current_price:.2f} USDT')

# Исполняем BUY ордер
order = signed_request('POST', '/api/v3/order', {
    'symbol': 'DOGEUSDT',
    'side': 'BUY',
    'type': 'MARKET',
    'quantity': str(qty)
})

print()
print('=== Результат ===')
print(json.dumps(order, indent=2))

# Баланс после
account2 = signed_request('GET', '/api/v3/account')
print()
print('=== Баланс после покупки ===')
for b in account2.get('balances', []):
    free = float(b['free'])
    if free > 0 and b['asset'] in ['USDT', 'DOGE', 'BTC', 'ETH']:
        print(f"  {b['asset']}: {free}")
