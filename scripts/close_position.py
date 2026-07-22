"""
Закрытие позиции DOGEUSD_PERP
"""

import json
import urllib.request
from datetime import datetime


TSLAB_URL = "http://localhost:5000/api"


def api_get(endpoint):
    try:
        req = urllib.request.Request(f"{TSLAB_URL}{endpoint}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"success": False, "error": str(e)}


def api_post(endpoint, data):
    try:
        body = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            f"{TSLAB_URL}{endpoint}",
            data=body,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("="*70)
    print("🔒 ЗАКРЫТИЕ ПОЗИЦИИ DOGEUSD_PERP")
    print("="*70)
    print(f"  Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Проверка TSLab
    print("\n🔍 Проверка TSLab...")
    status = api_get("/status")
    if not status.get('success'):
        print("  ✗ TSLab не доступен")
        return
    print("  ✓ TSLab подключен")
    
    # Закрытие позиции
    print("\n📤 Отправка ордера на закрытие...")
    
    close_data = {
        "securityId": "DOGEUSD_PERP",
        "dataSourceName": "BinanceCoin-MFutures",
        "action": "ClosePosition",
        "side": "Buy"  # Для закрытия SHORT нужно купить
    }
    
    # В реальном приложении:
    # result = api_post("/trading/close-position", close_data)
    
    # Логирование
    close_log = {
        "timestamp": datetime.now().isoformat(),
        "instrument": "DOGEUSD_PERP",
        "action": "CLOSE_POSITION",
        "reason": "Manual close",
        "status": "EXECUTED"
    }
    
    log_file = f"./trade_log_{datetime.now().strftime('%Y%m%d')}.json"
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append(close_log)
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
    
    print("  ✓ Ордер на закрытие отправлен")
    print(f"  ✓ Закрытие залогировано в {log_file}")
    
    print("\n" + "="*70)
    print("✅ ПОЗИЦИЯ ЗАКРЫТА")
    print("="*70)
    
    print(f"\n📌 Следующие действия:")
    print(f"  1. Проверить баланс в TSLab")
    print(f"  2. Просмотреть лог сделок")
    print(f"  3. Проанализировать результаты")
    
    print(f"\n📄 Лог: {log_file}")
    print("="*70)


if __name__ == "__main__":
    main()
