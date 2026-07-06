"""
Конфигурация API ключей для SkSred Trading Bot

Получите ключи из TSLab:
1. Откройте TSLab
2. Навигация → Данные → Поставщики → BinanceCoin-MFutures → Настройки
3. Скопируйте Key и Secret
"""

# API ключи Binance
# Замените значения ниже на ваши ключи из TSLab
API_KEY = "Q9yAz91QrW3Oz7ekr2xEagBLSYyFxULXOoayVx2vZIJW5WeAhR5mAmTN2RsR64fw"
API_SECRET = "w2fI94itvgKavrueconurkxg3XdeerIuTkXssM7T9VW6M4yKSGfvxsaAtFOdqKR3"

# Режим работы
# True = Testnet (тестовая сеть, без реальных денег)
# False = Mainnet (реальная торговля)
USE_TESTNET = False

# Параметры торговли
LEVERAGE = 5
TIMEFRAME = '4h'

# Инструменты и распределение капитала
INSTRUMENTS = {
    'XTZ/USDT:USDT': {'sma_s': 3, 'sma_l': 15, 'alloc': 20},
    'SUI/USDT:USDT': {'sma_s': 3, 'sma_l': 15, 'alloc': 20},
    'TRX/USDT:USDT': {'sma_s': 7, 'sma_l': 15, 'alloc': 20},
}

# Параметры стратегии
EMA_TREND = 200
ATR_PERIOD = 14
ATR_SL_MULT = 1.5
ATR_TP_MULT = 3.0
TRAIL_ACTIVATE = 0.02
TRAIL_DIST = 0.015
COMMISSION = 0.0005

# Интервал проверки (секунды)
CHECK_INTERVAL = 300

# ============================================================
# УВЕДОМЛЕНИЯ TELEGRAM
# ============================================================
TELEGRAM_BOT_TOKEN = "8773240911:AAGm7uMifidrE2GMfO-_S0x3qzKO6XtEctc"
TELEGRAM_CHAT_ID = "1002581728198"

# Прокси для Telegram (если нужен)
# Формат: "socks5://host:port" или "http://host:port"
TELEGRAM_PROXY = None  # Замените на ваш прокси если нужен
