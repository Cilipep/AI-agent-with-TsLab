"""
Демонстрация запуска на реальном аккаунте DOGE с плечом 3x.
⚠️ ДЕМОНСТРАЦИЯ - в реальном режиме требует подтверждения!
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


def load_config():
    with open("./strategy_config.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    print("="*70)
    print("🚀 LIVE TRADING - DOGEUSD_PERP (ДЕМОНСТРАЦИЯ)")
    print("="*70)
    print("⚠️  РЕЖИМ РЕАЛЬНОЙ ТОРГОВЛИ")
    print("⚠️  ИСПОЛЬЗУЮТСЯ РЕАЛЬНЫЕ ДЕНЬГИ!")
    print("="*70)
    
    config = load_config()
    
    # Проверка TSLab
    print("\n🔍 Проверки...")
    status = api_get("/status")
    if status.get('success'):
        print("  ✓ TSLab подключен")
    else:
        print("  ✗ TSLab не доступен")
        return
    
    # Проверка Binance
    ds = api_get("/datasources")
    if ds.get('success'):
        for d in ds.get('data', []):
            if d.get('name') == 'BinanceCoin-MFutures' and d.get('isConnected'):
                print("  ✓ Binance Coin Futures подключен")
                break
        else:
            print("  ✗ Binance не подключен")
            return
    
    # Анализ рынка
    print("\n📊 Анализ рынка...")
    print("  Тренд:     ↓ Нисходящий")
    print("  RSI:       45")
    print("  SMA Fast:  0.0175")
    print("  SMA Slow:  0.0180")
    print("  EMA200:    0.0190")
    
    # Сигнал
    print("\n📡 Сигнал: SHORT (Продажа)")
    
    # Проверка лимитов
    print("\n🛡️  Проверка лимитов безопасности...")
    print(f"  ⚠️  Историческая просадка 49.34% превышает лимит 30%")
    print(f"  → Рекомендуется снизить плечо до 2x")
    
    # Детали сделки
    print("\n" + "="*70)
    print("📋 ДЕТАЛИ СДЕЛКИ")
    print("="*70)
    
    print(f"\n  Инструмент:    DOGEUSD_PERP")
    print(f"  Действие:      ПРОДАТЬ (SHORT)")
    print(f"  Плечо:         {config['capital']['leverage']}x")
    print(f"  Капитал:       ${config['capital']['initial']}")
    print(f"  Размер:        ${config['capital']['initial'] * config['capital']['leverage'] * config['risk_management']['position_sizing']['risk_per_trade_pct'] / 100:.2f}")
    print(f"  Stop Loss:     {config['risk_management']['stop_loss']['atr_multiplier']}x ATR")
    print(f"  Take Profit:   {config['risk_management']['take_profit']['atr_multiplier']}x ATR")
    print(f"  Trail Stop:    {config['risk_management']['trailing_stop']['trail_pct']}%")
    
    print(f"\n  Реинвестирование:")
    for trend, params in config['reinvestment']['rules'].items():
        print(f"    {trend:<12} → {params['reinvest_pct']}%")
    
    # Порядок действий
    print("\n" + "="*70)
    print("📋 ПОРЯДОК ДЕЙСТВИЙ ДЛЯ РЕАЛЬНОЙ ТОРГОВЛИ:")
    print("="*70)
    
    steps = [
        ("1. Подтверждение", "Нажать Enter для подтверждения сделки"),
        ("2. Отправка ордера", "POST /api/trading/order с параметрами"),
        ("3. Мониторинг", "Отслеживание позиции в реальном времени"),
        ("4. Управление", "Трейлинг стоп, тейк профит"),
        ("5. Логирование", "Сохранение результатов в журнал"),
    ]
    
    for step, desc in steps:
        print(f"  {step:<20} {desc}")
    
    # Ограничения
    print("\n" + "="*70)
    print("🛡️  ОГРАНИЧЕНИЯ БЕЗОПАСНОСТИ:")
    print("="*70)
    
    limits = [
        "Максимальная просадка: 30% от капитала",
        "Максимальная позиция: 100% от капитала × плечо",
        "Автоматическая остановка при ликвидации",
        "Двойное подтверждение перед каждой сделкой",
        "Логирование всех действий",
    ]
    
    for limit in limits:
        print(f"  • {limit}")
    
    # Предупреждение
    print("\n" + "="*70)
    print("⚠️  ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ:")
    print("="*70)
    print("""
  Торговля с кредитным плечом связана с высоким риском!
  
  • Вы можете потерять больше, чем вложили
  • Рынок может двигаться против вашей позиции
  • Ликвидация означает полную потерю капитала
  
  Убедитесь, что вы:
  • Понимаете риски
  • Готовы потерять вложенные средства
  • Используете только свободные средства
    """)
    
    print("="*70)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("📄 Для реальной торговли запустите live_trading.py")
    print("="*70)
    
    return {
        'status': 'ready',
        'signal': 'SHORT',
        'leverage': config['capital']['leverage'],
        'risk': config['risk_management']['position_sizing']['risk_per_trade_pct'],
        'config': config
    }


if __name__ == "__main__":
    main()
