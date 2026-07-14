import requests
import hmac
import hashlib
import urllib.parse

api_key = 'fV3nR7q3hAevTrJQlGNdPdEi4omXBoL3pYLLwKpWQeAVIWGGujSUFCXvfN7ujLk1'
secret = '7raJ21kLwy7TeF41NHRYskTFP138pThoGdeDudXSb4AKsd4thDPShLkI09SR5cua'

response = requests.get('https://demo.binance.com/api/v3/time')
server_time = response.json()['serverTime']

params = {
    'timestamp': server_time,
    'recvWindow': 10000
}

query_string = urllib.parse.urlencode(params)
signature = hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
params['signature'] = signature

headers = {'X-MBX-APIKEY': api_key}
response = requests.get('https://demo.binance.com/api/v3/account', params=params, headers=headers)
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    for bal in data.get('balances', []):
        free = float(bal['free'])
        locked = float(bal['locked'])
        if free > 0 or locked > 0:
            print(f"{bal['asset']}: free={bal['free']}, locked={bal['locked']}")
else:
    print(f'Error: {response.text[:500]}')
