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
    r = requests.request(method, f'{BASE}{path}', params=params, headers=headers)
    return r.json()

# 1. Отменяем все ордера
print('=== Отменяю все ордера ===')
cancel = signed_request('DELETE', '/api/v3/openOrders', {'symbol': 'DOGEUSDT'})
if isinstance(cancel, list):
    print(f'Отменено ордеров: {len(cancel)}')
else:
    print(cancel)

# 2. Получаем баланс DOGE
account = signed_request('GET', '/api/v3/account')
doge_free = 0
for b in account.get('balances', []):
    if b['asset'] == 'DOGE':
        doge_free = float(b['free'])
        break

print(f'\nБаланс DOGE: {doge_free}')

if doge_free <= 0:
    print('Нет DOGE для продажи')
else:
    # 3. Продаём всё по рынку
    print(f'\nПродаю {doge_free} DOGE по рыночной цене...')
    order = signed_request('POST', '/api/v3/order', {
        'symbol': 'DOGEUSDT',
        'side': 'SELL',
        'type': 'MARKET',
        'quantity': str(doge_free)
    })
    print(json.dumps(order, indent=2))

# 4. Финальный баланс
print('\n=== Финальный баланс ===')
account2 = signed_request('GET', '/api/v3/account')
for b in account2.get('balances', []):
    free = float(b['free'])
    if free > 0 and b['asset'] in ['USDT', 'DOGE', 'BTC', 'ETH']:
        print(f"  {b['asset']}: {free}")
