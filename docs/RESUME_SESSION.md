# How to Resume This Session After Reboot

## Quick Start

### 1. Check if bot is running
```powershell
Get-Process python -ErrorAction SilentlyContinue
```

### 2. Start bot (if not running)
```powershell
cd C:\Users\i59400f\Desktop\ai-agent\spread-trading-bot
python spotread_bot.py
```

### 3. Check bot status
```powershell
# Check logs
Get-Content .\spread_bot.log -Tail 20

# Check trade journal
Get-Content .\trade_journal.csv
```

## Files Location

| File | Path |
|------|------|
| Bot code | `C:\Users\i59400f\Desktop\ai-agent\spread-trading-bot\spotread_bot.py` |
| Config | `C:\Users\i59400f\Desktop\ai-agent\spread-trading-bot\config.py` |
| Logs | `C:\Users\i59400f\Desktop\ai-agent\spread-trading-bot\spread_bot.log` |
| Trade journal | `C:\Users\i59400f\Desktop\ai-agent\spread-trading-bot\trade_journal.csv` |
| Bot state | `C:\Users\i59400f\Desktop\ai-agent\spread-trading-bot\bot_state.json` |

## OAuth Credentials

| File | Path |
|------|------|
| Token | `C:\Users\i59400f\AppData\Roaming\bybit\oauth_token.json` |

## Bot Parameters

- Pair: BTCUSDT/ETHUSDT
- Entry Z: 2.0
- Exit Z: 0.5
- Stop Z: 3.0
- Position Size: 5 USDT per leg
- Leverage: 10x
- Trading Hours: 1:00 - 7:00 LOCAL TIME
- Max Daily Loss: 2%
- Max Trades/Day: 10

## Gerchik's Improvements

1. Trade journal (CSV)
2. Daily loss limits
3. Anomaly detection
4. Volatility adaptation
5. Position persistence
6. Local time trading hours

## Stop Bot

```powershell
Get-Process python | Stop-Process -Force
```
