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

# 1. Отменяем все открытые ордера
print('=== Отменяю все ордера DOGEUSDT ===')
cancel = signed_request('DELETE', '/api/v3/openOrders', {'symbol': 'DOGEUSDT'})
print(f'Результат отмены: {cancel}')
print()

# Проверяем баланс
account = signed_request('GET', '/api/v3/account')
for b in account.get('balances', []):
    if b['asset'] == 'DOGE':
        print(f'Баланс DOGE: {b["free"]} (locked: {b["locked"]})')
    if b['asset'] == 'USDT':
        print(f'Баланс USDT: {b["free"]}')
print()

# 2. Ставим OCO ордер (SL + TP)
SL_PRICE = 0.07334      # -1.5%
TP_PRICE = 0.07611      # +2.2%
QTY = 20030

print('=== Ставлю OCO ордер (SL + TP) ===')
print(f'Stop Loss:  ${SL_PRICE:.6f} (-1.5%)')
print(f'Take Profit:${TP_PRICE:.6f} (+2.2%)')
print(f'Quantity:   {QTY} DOGE')
print()

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

# 3. Проверяем открытые ордера
print('=== Открытые ордера ===')
open_orders = signed_request('GET', '/api/v3/openOrders', {'symbol': 'DOGEUSDT'})
if isinstance(open_orders, list):
    for o in open_orders:
        print(f"  {o['type']} {o['side']} {o['origQty']} @ {o['price']} (stop: {o.get('stopPrice', 'N/A')})")
    print(f'\nВсего: {len(open_orders)} ордеров')
else:
    print(open_orders)
