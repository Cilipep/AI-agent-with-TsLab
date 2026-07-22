# Spread Trading Bot Configuration (Gerchik Edition)

# Bybit API Credentials (from OAuth)
API_KEY = "sIyxpD4YOV0D5dQs5q"
API_SECRET = "6f3fJi5CRjCf5tq1RAIUY4K9oKtbgAKmaiBU"

# Trading Environment
ENV = "mainnet"  # "mainnet" or "testnet"
BASE_URL = "https://api.bybit.com" if ENV == "mainnet" else "https://api-testnet.bybit.com"

# Trading Pair
PAIR = {
    "long": "BTCUSDT",    # Instrument to BUY
    "short": "ETHUSDT",   # Instrument to SELL
}

# Spread Parameters
LOOKBACK = 100           # Period for mean calculation (hours)
ENTRY_Z = 1.2            # Z-score threshold for entry (optimized for 4h)
EXIT_Z = 0.5             # Z-score threshold for exit
STOP_Z = 3.5             # Z-score threshold for stop loss (optimized for 4h)

# Position Size
POSITION_SIZE_USDT = 5   # Size per leg in USDT
LEVERAGE = 10            # Leverage for perpetuals

# Risk Management (Gerchik principles)
MAX_DRAWDOWN = 0.1       # 10% max drawdown
MAX_DAILY_LOSS = 0.02    # 2% max daily loss
MAX_POSITIONS = 1        # Max simultaneous spread positions
MAX_TRADES_PER_DAY = 10  # Max trades per day

# Server-side TP/SL (executes even if bot is offline)
SERVER_TP_PERCENT = 3.0  # Take Profit: +3% from entry
SERVER_SL_PERCENT = 2.0  # Stop Loss: -2% from entry

# Volatility Adaptation
VOLATILITY_LOOKBACK = 20 # Period for volatility calculation
VOLATILITY_SCALE = 1.5   # Scale position size based on volatility

# Anomaly Detection
ANOMALY_THRESHOLD = 3.0  # Std threshold for anomaly detection
VOLUME_SPIKE_RATIO = 2.0 # Volume spike threshold

# Time Filters
TRADING_HOURS_START = 1  # UTC
TRADING_HOURS_END = 7    # UTC
AVOID_FRIDAY_AFTERNOON = False  # Not needed for 1-7 UTC

# Timeframe
KLINE_INTERVAL = "240"   # 4 hour candles (optimized)
KLINE_LIMIT = 100        # Number of candles to fetch

# Logging
LOG_FILE = "spread_bot.log"
JOURNAL_FILE = "trade_journal.csv"
DAILY_REPORT_FILE = "daily_report.txt"
