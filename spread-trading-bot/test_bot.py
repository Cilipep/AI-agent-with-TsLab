"""
Test script for Spread Trading Bot
Verifies API connection and spread calculation
"""

import sys
import time
import hmac
import hashlib
import json
import requests
from config import API_KEY, API_SECRET, BASE_URL, PAIR, LOOKBACK


def test_connection():
    """Test API connection"""
    print("Testing API connection...")
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    endpoint = "/v5/market/time"
    param_str = f"{timestamp}{API_KEY}{recv_window}"
    
    signature = hmac.new(
        API_SECRET.encode(),
        param_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": recv_window,
        "User-Agent": "bybit-skill/1.5.4"
    }
    
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    result = response.json()
    
    if result.get("retCode") == 0:
        print("✅ API connection successful")
        return True
    else:
        print(f"❌ API connection failed: {result}")
        return False


def test_klines():
    """Test kline fetching"""
    print("\nTesting kline fetching...")
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    endpoint = "/v5/market/kline"
    query = f"category=linear&symbol={PAIR['long']}&interval=60&limit=10"
    param_str = f"{timestamp}{API_KEY}{recv_window}{query}"
    
    signature = hmac.new(
        API_SECRET.encode(),
        param_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": recv_window,
        "User-Agent": "bybit-skill/1.5.4"
    }
    
    response = requests.get(f"{BASE_URL}{endpoint}?{query}", headers=headers)
    result = response.json()
    
    if result.get("retCode") == 0:
        klines = result["result"]["list"]
        print(f"✅ Fetched {len(klines)} klines for {PAIR['long']}")
        print(f"   Latest close: ${float(klines[0][4]):.2f}")
        return True
    else:
        print(f"❌ Failed to fetch klines: {result}")
        return False


def test_spread_calculation():
    """Test spread calculation"""
    print("\nTesting spread calculation...")
    
    def fetch_klines(symbol):
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        query = f"category=linear&symbol={symbol}&interval=60&limit={LOOKBACK}"
        param_str = f"{timestamp}{API_KEY}{recv_window}{query}"
        
        signature = hmac.new(
            API_SECRET.encode(),
            param_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-BAPI-API-KEY": API_KEY,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": recv_window,
            "User-Agent": "bybit-skill/1.5.4"
        }
        
        response = requests.get(f"{BASE_URL}/v5/market/kline?{query}", headers=headers)
        result = response.json()
        
        return [float(k[4]) for k in reversed(result["result"]["list"])]
    
    try:
        closes1 = fetch_klines(PAIR["long"])
        closes2 = fetch_klines(PAIR["short"])
        
        n = min(len(closes1), len(closes2))
        spreads = [closes1[i] / closes2[i] for i in range(n)]
        
        mean = sum(spreads) / n
        std = (sum((s - mean) ** 2 for s in spreads) / n) ** 0.5
        z_score = (spreads[-1] - mean) / std if std > 0 else 0
        
        print(f"✅ Spread calculation successful")
        print(f"   {PAIR['long']}: ${closes1[-1]:.2f}")
        print(f"   {PAIR['short']}: ${closes2[-1]:.2f}")
        print(f"   Spread: {spreads[-1]:.4f}")
        print(f"   Mean: {mean:.4f}")
        print(f"   Std: {std:.4f}")
        print(f"   Z-Score: {z_score:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Spread calculation failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Spread Trading Bot - Test Suite")
    print("=" * 50)
    
    tests = [
        test_connection,
        test_klines,
        test_spread_calculation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  Passed: {sum(results)}/{len(results)}")
    print("=" * 50)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
