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
    r = requests.post(f'{BASE}{path}', params=params, headers=headers)
    return r.json()

# Сначала отменяем существующий SL ордер
print('Отменяю старый SL ордер...')
cancel = signed_request('POST', '/api/v3/order', {
    'symbol': 'DOGEUSDT',
    'orderId': '1799374'
})
print(f'Отмена: {cancel}')
print()

# Параметры
SL_PRICE = 0.07334      # -1.5%
TP_PRICE = 0.07611      # +2.2%
QTY = 20030

print('=== Ставлю OCO ордер (SL + TP) ===')
print(f'Stop Loss:  ${SL_PRICE:.6f}')
print(f'Take Profit:${TP_PRICE:.6f}')
print(f'Quantity:   {QTY} DOGE')
print()

# OCO ордер
oco = signed_request('POST', '/api/v3/orderList/oco', {
    'symbol': 'DOGEUSDT',
    'side': 'SELL',
    'quantity': str(QTY),
    'aboveType': 'TAKE_PROFIT_LIMIT',
    'abovePrice': str(TP_PRICE),
    'aboveStopPrice': str(TP_PRICE),
    'aboveTimeInForce': 'GTC',
    'belowType': 'STOP_LOSS_LIMIT',
    'belowPrice': str(SL_PRICE),
    'belowStopPrice': str(SL_PRICE),
    'belowTimeInForce': 'GTC'
})

print(json.dumps(oco, indent=2))
print()

# Проверяем
print('=== Открытые ордера ===')
orders = signed_request('POST', '/api/v3/openOrders', {'symbol': 'DOGEUSDT'}) if False else None

# Используем GET
import hmac as h2
ts2 = int(time.time()*1000)
qs2 = f'symbol=DOGEUSDT&timestamp={ts2}&recvWindow=5000'
sig2 = h2.new(API_SECRET.encode(), qs2.encode(), hashlib.sha256).hexdigest()
r2 = requests.get(f'{BASE}/api/v3/openOrders?{qs2}&signature={sig2}', headers={'X-MBX-APIKEY': API_KEY})
open_orders = r2.json()

if isinstance(open_orders, list):
    for o in open_orders:
        print(f"  {o['type']} {o['side']} {o['origQty']} @ {o['price']} (stop: {o.get('stopPrice', 'N/A')})")
    print(f'\nВсего открытых ордеров: {len(open_orders)}')
else:
    print(open_orders)
