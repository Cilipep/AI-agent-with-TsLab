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

# Параметры стратегии
ENTRY_PRICE = 0.0744
SL_PRICE = 0.07334      # -1.5%
TP_PRICE = 0.07611      # +2.2%
QTY = 20030             # Весь DOGE

print('=== Установка SL/TP для DOGEUSDT ===')
print(f'Entry:      ${ENTRY_PRICE:.6f}')
print(f'Stop Loss:  ${SL_PRICE:.6f}')
print(f'Take Profit:${TP_PRICE:.6f}')
print(f'Quantity:   {QTY} DOGE')
print()

# 1. Stop Loss ордер (SELL если цена упадёт до SL)
print('Ставлю Stop Loss...')
sl_order = signed_request('POST', '/api/v3/order', {
    'symbol': 'DOGEUSDT',
    'side': 'SELL',
    'type': 'STOP_LOSS_LIMIT',
    'timeInForce': 'GTC',
    'quantity': str(QTY),
    'price': str(SL_PRICE),
    'stopPrice': str(SL_PRICE)
})
print(f'SL Order: {sl_order.get("orderId", sl_order.get("msg", "error"))}')
print(json.dumps(sl_order, indent=2))
print()

# 2. Take Profit ордер (SELL если цена вырастет до TP)
print('Ставлю Take Profit...')
tp_order = signed_request('POST', '/api/v3/order', {
    'symbol': 'DOGEUSDT',
    'side': 'SELL',
    'type': 'TAKE_PROFIT_LIMIT',
    'timeInForce': 'GTC',
    'quantity': str(QTY),
    'price': str(TP_PRICE),
    'stopPrice': str(TP_PRICE)
})
print(f'TP Order: {tp_order.get("orderId", tp_order.get("msg", "error"))}')
print(json.dumps(tp_order, indent=2))
print()

# Проверяем открытые ордера
print('=== Открытые ордера ===')
orders = signed_request('GET', '/api/v3/openOrders', {'symbol': 'DOGEUSDT'})
if isinstance(orders, list):
    for o in orders:
        print(f"  {o['type']} {o['side']} {o['origQty']} @ {o['price']} (stop: {o['stopPrice']})")
else:
    print(orders)
