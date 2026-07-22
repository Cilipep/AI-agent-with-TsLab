"""
Spread Trading Bot for Bybit (Gerchik Edition)
Implements Alexander Gerchik's trading principles:
- Strict stop-losses
- Trade journal
- Daily loss limits
- Anomaly detection
- Volatility adaptation
- Position persistence
"""

import time
import json
import hmac
import hashlib
import csv
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import (
    API_KEY, API_SECRET, BASE_URL, PAIR, LOOKBACK,
    ENTRY_Z, EXIT_Z, STOP_Z, POSITION_SIZE_USDT,
    LEVERAGE, KLINE_INTERVAL, KLINE_LIMIT, LOG_FILE,
    JOURNAL_FILE, DAILY_REPORT_FILE, MAX_DRAWDOWN,
    MAX_DAILY_LOSS, MAX_TRADES_PER_DAY, VOLATILITY_LOOKBACK,
    VOLATILITY_SCALE, ANOMALY_THRESHOLD, TRADING_HOURS_START,
    TRADING_HOURS_END, AVOID_FRIDAY_AFTERNOON,
    SERVER_TP_PERCENT, SERVER_SL_PERCENT
)

# State file for position persistence
STATE_FILE = "bot_state.json"


class BybitSpreadBot:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "bybit-skill/1.5.4",
            "X-Referer": "bybit-skill"
        })
        self.position = {
            "long": None,
            "short": None,
            "entry_time": None,
            "entry_z": None
        }
        self.spread_history = []
        self.max_retries = 3
        self.retry_delay = 2
        self.api_timeout = 10
        
        # Gerchik's risk management
        self.initial_balance = 0
        self.daily_pnl = 0
        self.daily_trades = 0
        self.trade_history = []
        self.last_trade_date = None
        
        # Initialize journal
        self.init_journal()

        # Load saved state
        self.load_state()
        
    def init_journal(self):
        """Initialize trade journal CSV"""
        try:
            with open(JOURNAL_FILE, 'x', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'action', 'symbol', 'side', 'qty',
                    'price', 'z_score', 'reason', 'pnl', 'balance'
                ])
        except FileExistsError:
            pass

    def save_state(self):
        """Save bot state to file for persistence"""
        state = {
            "position": self.position,
            "daily_pnl": self.daily_pnl,
            "daily_trades": self.daily_trades,
            "last_trade_date": str(self.last_trade_date) if self.last_trade_date else None,
            "initial_balance": self.initial_balance
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        """Load bot state from file"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.position = state.get("position", self.position)
                self.daily_pnl = state.get("daily_pnl", 0)
                self.daily_trades = state.get("daily_trades", 0)
                if state.get("last_trade_date"):
                    self.last_trade_date = datetime.strptime(state["last_trade_date"], "%Y-%m-%d").date()
                self.initial_balance = state.get("initial_balance", 0)
                self.log("State loaded from file")
            except Exception as e:
                self.log(f"Failed to load state: {e}")
    
    def _sign(self, params: str) -> str:
        """Generate HMAC-SHA256 signature"""
        return hmac.new(
            self.api_secret.encode(),
            params.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, endpoint: str, params: dict = None, body: dict = None) -> dict:
        """Make authenticated API request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                timestamp = str(int(time.time() * 1000))
                recv_window = "5000"
                
                # Build param string
                if method == "GET" and params:
                    query_string = "&".join(f"{k}={v}" for k, v in params.items())
                    param_str = f"{timestamp}{self.api_key}{recv_window}{query_string}"
                    url = f"{self.base_url}{endpoint}?{query_string}"
                else:
                    param_str = f"{timestamp}{self.api_key}{recv_window}{json.dumps(body)}"
                    url = f"{self.base_url}{endpoint}"
                
                # Sign request
                signature = self._sign(param_str)
                
                headers = {
                    "X-BAPI-API-KEY": self.api_key,
                    "X-BAPI-TIMESTAMP": timestamp,
                    "X-BAPI-SIGN": signature,
                    "X-BAPI-RECV-WINDOW": recv_window,
                    "Content-Type": "application/json"
                }
                
                response = self.session.request(
                    method, url, headers=headers,
                    json=body if body else None,
                    timeout=self.api_timeout
                )
                
                result = response.json()
                
                # Check for rate limiting
                if result.get("retCode") == 10006:
                    self.log(f"Rate limited, waiting {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    continue
                
                return result
                
            except requests.exceptions.Timeout:
                self.log(f"API timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
            except requests.exceptions.RequestException as e:
                self.log(f"API error: {e} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                break
        
        raise Exception(f"API request failed after {self.max_retries} attempts")
    
    def get_balance(self) -> float:
        """Get available USDT balance"""
        result = self._request("GET", "/v5/account/wallet-balance", {
            "accountType": "UNIFIED"
        })
        
        if result.get("retCode") != 0:
            raise Exception(f"Failed to fetch balance: {result}")
        
        for coin in result["result"]["list"][0]["coin"]:
            if coin["coin"] == "USDT":
                return float(coin["availableToWithdraw"])
        
        return 0.0
    
    def get_klines(self, symbol: str) -> List[dict]:
        """Fetch hourly klines for a symbol (with volume)"""
        result = self._request("GET", "/v5/market/kline", {
            "category": "linear",
            "symbol": symbol,
            "interval": KLINE_INTERVAL,
            "limit": str(KLINE_LIMIT)
        })
        
        if result.get("retCode") != 0:
            raise Exception(f"Failed to fetch klines: {result}")
        
        # Return klines with volume in chronological order
        return [{
            "close": float(k[4]),
            "volume": float(k[5])
        } for k in reversed(result["result"]["list"])]
    
    def calculate_spread(self, closes1: List[float], closes2: List[float]) -> dict:
        """Calculate spread, mean, std, and z-score"""
        n = min(len(closes1), len(closes2))
        
        # Calculate spread ratios
        spreads = [closes1[i] / closes2[i] for i in range(n)]
        
        # Calculate statistics
        mean = sum(spreads) / n
        std = (sum((s - mean) ** 2 for s in spreads) / n) ** 0.5
        
        current_spread = spreads[-1]
        z_score = (current_spread - mean) / std if std > 0 else 0
        
        return {
            "spread": current_spread,
            "mean": mean,
            "std": std,
            "z_score": z_score,
            "history": spreads
        }
    
    def calculate_volatility(self, closes: List[float]) -> float:
        """Calculate volatility (standard deviation of returns)"""
        if len(closes) < 2:
            return 0
        
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        n = len(returns)
        mean = sum(returns) / n
        variance = sum((r - mean) ** 2 for r in returns) / n
        
        return variance ** 0.5
    
    def detect_anomaly(self, spreads: List[float], volumes1: List[float], volumes2: List[float]) -> dict:
        """Detect anomalies in spread and volume"""
        anomalies = []
        
        # Check spread anomaly
        if len(spreads) >= 20:
            recent_mean = sum(spreads[-20:]) / 20
            recent_std = (sum((s - recent_mean) ** 2 for s in spreads[-20:]) / 20) ** 0.5
            
            if abs(spreads[-1] - recent_mean) > ANOMALY_THRESHOLD * recent_std:
                anomalies.append({
                    "type": "spread_spike",
                    "value": spreads[-1],
                    "mean": recent_mean,
                    "std": recent_std
                })
        
        # Check volume anomaly
        if len(volumes1) >= 20 and len(volumes2) >= 20:
            avg_vol1 = sum(volumes1[-20:]) / 20
            avg_vol2 = sum(volumes2[-20:]) / 20
            
            if volumes1[-1] > 2 * avg_vol1:
                anomalies.append({
                    "type": "volume_spike_long",
                    "value": volumes1[-1],
                    "avg": avg_vol1
                })
            
            if volumes2[-1] > 2 * avg_vol2:
                anomalies.append({
                    "type": "volume_spike_short",
                    "value": volumes2[-1],
                    "avg": avg_vol2
                })
        
        return {
            "has_anomaly": len(anomalies) > 0,
            "anomalies": anomalies
        }
    
    def is_trading_hours(self) -> bool:
        """Check if current time is within trading hours (LOCAL TIME)"""
        now = datetime.now()  # Use local time
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        # Avoid Friday afternoon
        if AVOID_FRIDAY_AFTERNOON and weekday == 4 and hour >= 16:
            return False

        # Check trading hours (handles wrap-around if start > end)
        if TRADING_HOURS_START <= TRADING_HOURS_END:
            # Normal: e.g., 1-7
            in_hours = TRADING_HOURS_START <= hour < TRADING_HOURS_END
        else:
            # Wrap: e.g., 22-6
            in_hours = hour >= TRADING_HOURS_START or hour < TRADING_HOURS_END

        if not in_hours:
            return False

        # Avoid weekends
        if weekday >= 5:
            return False

        return True
    
    def check_daily_limits(self) -> bool:
        """Check daily loss and trade limits"""
        today = datetime.now().date()
        
        # Reset daily counters if new day
        if self.last_trade_date != today:
            self.daily_pnl = 0
            self.daily_trades = 0
            self.last_trade_date = today
        
        # Check daily loss limit
        balance = self.get_balance()
        if balance > 0:
            daily_loss_pct = abs(self.daily_pnl) / balance
            if self.daily_pnl < 0 and daily_loss_pct >= MAX_DAILY_LOSS:
                self.log(f"Daily loss limit reached: {daily_loss_pct:.2%} >= {MAX_DAILY_LOSS:.2%}")
                return False
        
        # Check trade count limit
        if self.daily_trades >= MAX_TRADES_PER_DAY:
            self.log(f"Daily trade limit reached: {self.daily_trades} >= {MAX_TRADES_PER_DAY}")
            return False
        
        return True
    
    def log_trade(self, action: str, symbol: str, side: str, qty: float,
                  price: float, z_score: float, reason: str, pnl: float = 0):
        """Log trade to journal"""
        balance = self.get_balance()
        
        with open(JOURNAL_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                action,
                symbol,
                side,
                qty,
                price,
                f"{z_score:.2f}",
                reason,
                f"{pnl:.2f}",
                f"{balance:.2f}"
            ])
        
        # Update daily PnL
        self.daily_pnl += pnl
        self.daily_trades += 1
    
    def set_leverage(self, symbol: str):
        """Set leverage for a symbol"""
        result = self._request("POST", "/v5/position/set-leverage", body={
            "category": "linear",
            "symbol": symbol,
            "buyLeverage": str(LEVERAGE),
            "sellLeverage": str(LEVERAGE)
        })
        
        # Leverage already set is not an error
        if result.get("retCode") == 110043:
            return result
        
        if result.get("retCode") != 0:
            raise Exception(f"Failed to set leverage: {result}")
        
        return result
    
    def get_position(self, symbol: str) -> Optional[dict]:
        """Get current position for a symbol"""
        result = self._request("GET", "/v5/position/list", {
            "category": "linear",
            "symbol": symbol
        })
        
        if result.get("retCode") != 0:
            return None
        
        positions = result["result"]["list"]
        for pos in positions:
            if pos["size"] and float(pos["size"]) > 0:
                return pos
        
        return None
    
    def get_price(self, symbol: str) -> float:
        """Get current mark price"""
        result = self._request("GET", "/v5/market/tickers", {
            "category": "linear",
            "symbol": symbol
        })
        
        if result.get("retCode") != 0:
            raise Exception(f"Failed to fetch price: {result}")
        
        return float(result["result"]["list"][0]["lastPrice"])
    
    def get_min_qty(self, symbol: str) -> float:
        """Get minimum order quantity for a symbol"""
        result = self._request("GET", "/v5/market/instruments-info", {
            "category": "linear",
            "symbol": symbol
        })
        
        if result.get("retCode") != 0:
            raise Exception(f"Failed to fetch instrument info: {result}")
        
        lot_size = result["result"]["list"][0]["lotSizeFilter"]
        min_qty = lot_size.get("minOrderQty", "0.001")
        
        # Handle empty or None values
        if not min_qty or min_qty == "":
            min_qty = "0.001"
        
        return float(min_qty)

    def place_server_tpsl(self, symbol: str, entry_price: float, qty: float, side: str):
        """Place server-side TP/SL orders (executes even if bot is offline)"""
        try:
            # Calculate TP and SL prices
            if side == "Buy":
                # Long position: TP above, SL below
                tp_price = entry_price * (1 + SERVER_TP_PERCENT / 100)
                sl_price = entry_price * (1 - SERVER_SL_PERCENT / 100)
                close_side = "Sell"
            else:
                # Short position: TP below, SL above
                tp_price = entry_price * (1 - SERVER_TP_PERCENT / 100)
                sl_price = entry_price * (1 + SERVER_SL_PERCENT / 100)
                close_side = "Buy"

            # Place Take Profit order
            result_tp = self._request("POST", "/v5/order/create", body={
                "category": "linear",
                "symbol": symbol,
                "side": close_side,
                "orderType": "Market",
                "qty": str(qty),
                "positionIdx": 0,
                "reduceOnly": True,
                "takeProfit": f"{tp_price:.2f}",
                "tpslMode": "Full"
            })

            if result_tp.get("retCode") == 0:
                self.log(f"[OK] Server TP placed for {symbol}: ${tp_price:.2f} (+{SERVER_TP_PERCENT}%)")
            else:
                self.log(f"[WARN] Failed to place TP for {symbol}: {result_tp}")

            # Place Stop Loss order
            result_sl = self._request("POST", "/v5/order/create", body={
                "category": "linear",
                "symbol": symbol,
                "side": close_side,
                "orderType": "Market",
                "qty": str(qty),
                "positionIdx": 0,
                "reduceOnly": True,
                "stopLoss": f"{sl_price:.2f}",
                "tpslMode": "Full"
            })

            if result_sl.get("retCode") == 0:
                self.log(f"[OK] Server SL placed for {symbol}: ${sl_price:.2f} (-{SERVER_SL_PERCENT}%)")
            else:
                self.log(f"[WARN] Failed to place SL for {symbol}: {result_sl}")

        except Exception as e:
            self.log(f"[WARN] Error placing server TP/SL: {e}")
    
    def calculate_position_size(self, volatility: float) -> float:
        """Calculate position size based on volatility"""
        # Base size
        base_size = POSITION_SIZE_USDT
        
        # Adjust for volatility (lower vol = larger position)
        if volatility > 0:
            # Normalize volatility (typical crypto vol is 0.01-0.05)
            normalized_vol = min(volatility / 0.03, 1.0)
            # Scale position inversely to volatility
            scale = 1.0 + (1.0 - normalized_vol) * (VOLATILITY_SCALE - 1.0)
            adjusted_size = base_size * scale
        else:
            adjusted_size = base_size
        
        # Ensure minimum and maximum
        adjusted_size = max(adjusted_size, base_size * 0.5)
        adjusted_size = min(adjusted_size, base_size * 1.5)
        
        return adjusted_size
    
    def open_spread_position(self, z_score: float, reason: str = "Z-Score signal"):
        """Open spread position: Long one, Short the other"""
        try:
            # Check daily limits
            if not self.check_daily_limits():
                return False
            
            # Check trading hours
            if not self.is_trading_hours():
                self.log("Outside trading hours, skipping entry")
                return False
            
            # Check balance
            balance = self.get_balance()
            required_margin = (POSITION_SIZE_USDT * 2) / LEVERAGE
            
            if balance < required_margin:
                self.log(f"Insufficient balance: {balance:.2f} USDT (need {required_margin:.2f})")
                return False
            
            # Check max drawdown
            if self.initial_balance > 0:
                drawdown = (self.initial_balance - balance) / self.initial_balance
                if drawdown >= MAX_DRAWDOWN:
                    self.log(f"Max drawdown exceeded: {drawdown:.2%} >= {MAX_DRAWDOWN:.2%}")
                    return False
            
            # Get klines for volatility calculation
            closes1 = [k["close"] for k in self.get_klines(PAIR["long"])]
            closes2 = [k["close"] for k in self.get_klines(PAIR["short"])]
            
            # Calculate volatility
            vol1 = self.calculate_volatility(closes1[-VOLATILITY_LOOKBACK:])
            vol2 = self.calculate_volatility(closes2[-VOLATILITY_LOOKBACK:])
            avg_volatility = (vol1 + vol2) / 2
            
            # Calculate position size based on volatility
            position_size = self.calculate_position_size(avg_volatility)
            
            # Set leverage
            self.set_leverage(PAIR["long"])
            self.set_leverage(PAIR["short"])
            
            # Calculate quantities
            price_long = self.get_price(PAIR["long"])
            price_short = self.get_price(PAIR["short"])
            
            qty_long = position_size / price_long
            qty_short = position_size / price_short
            
            # Get minimum quantities
            min_qty_long = self.get_min_qty(PAIR["long"])
            min_qty_short = self.get_min_qty(PAIR["short"])
            
            # Round to proper precision
            qty_long = round(qty_long, 3)
            qty_short = round(qty_short, 2)
            
            # Validate quantities
            if qty_long < min_qty_long:
                self.log(f"Long quantity too small: {qty_long} < {min_qty_long}")
                return False
            
            if qty_short < min_qty_short:
                self.log(f"Short quantity too small: {qty_short} < {min_qty_short}")
                return False
            
            self.log(f"\n{'='*50}")
            self.log(f"[OPENING SPREAD POSITION]")
            self.log(f"Reason: {reason}")
            self.log(f"Z-Score: {z_score:.2f}")
            self.log(f"Volatility: {avg_volatility:.4f}")
            self.log(f"Position Size: {position_size:.2f} USDT")
            self.log(f"Long {PAIR['long']}: {qty_long} @ ${price_long}")
            self.log(f"Short {PAIR['short']}: {qty_short} @ ${price_short}")
            self.log(f"Required margin: {required_margin:.2f} USDT")
            self.log(f"Available balance: {balance:.2f} USDT")
            self.log(f"{'='*50}")
            
            # Open long position
            result_long = self._request("POST", "/v5/order/create", body={
                "category": "linear",
                "symbol": PAIR["long"],
                "side": "Buy",
                "orderType": "Market",
                "qty": str(qty_long),
                "positionIdx": 0
            })
            
            if result_long.get("retCode") != 0:
                raise Exception(f"Failed to open long: {result_long}")
            
            self.log(f"[OK] Long order placed: {result_long['result']['orderId']}")
            
            # Open short position
            result_short = self._request("POST", "/v5/order/create", body={
                "category": "linear",
                "symbol": PAIR["short"],
                "side": "Sell",
                "orderType": "Market",
                "qty": str(qty_short),
                "positionIdx": 0
            })
            
            if result_short.get("retCode") != 0:
                raise Exception(f"Failed to open short: {result_short}")
            
            self.log(f"[OK] Short order placed: {result_short['result']['orderId']}")
            
            # Update position state
            self.position = {
                "long": {"symbol": PAIR["long"], "qty": qty_long, "side": "Buy", "price": price_long},
                "short": {"symbol": PAIR["short"], "qty": qty_short, "side": "Sell", "price": price_short},
                "entry_time": datetime.now().isoformat(),
                "entry_z": z_score,
                "entry_balance": balance
            }

            # Place server-side TP/SL orders (executes even if bot is offline)
            self.place_server_tpsl(PAIR["long"], price_long, qty_long, "Buy")
            self.place_server_tpsl(PAIR["short"], price_short, qty_short, "Sell")
            
            # Log trade
            self.log_trade("OPEN", PAIR["long"], "Buy", qty_long, price_long, z_score, reason)
            self.log_trade("OPEN", PAIR["short"], "Sell", qty_short, price_short, z_score, reason)
            
            self.log(f"[OK] Spread position opened at Z-Score: {z_score:.2f}")

            # Save state
            self.save_state()

            return True
            
        except Exception as e:
            self.log(f"[ERR] Error opening position: {e}")
            return False
    
    def close_spread_position(self, reason: str):
        """Close both legs of the spread position"""
        if not self.position["long"] or not self.position["short"]:
            return False
        
        try:
            self.log(f"\n{'='*50}")
            self.log(f"[CLOSING SPREAD POSITION]")
            self.log(f"Reason: {reason}")
            
            # Get current prices
            price_long = self.get_price(PAIR["long"])
            price_short = self.get_price(PAIR["short"])
            
            # Calculate PnL
            entry_price_long = self.position["long"]["price"]
            entry_price_short = self.position["short"]["price"]
            
            pnl_long = (price_long - entry_price_long) * self.position["long"]["qty"]
            pnl_short = (entry_price_short - price_short) * self.position["short"]["qty"]
            total_pnl = pnl_long + pnl_short
            
            self.log(f"Long PnL: ${pnl_long:.2f}")
            self.log(f"Short PnL: ${pnl_short:.2f}")
            self.log(f"Total PnL: ${total_pnl:.2f}")
            
            # Close long position
            result_long = self._request("POST", "/v5/order/create", body={
                "category": "linear",
                "symbol": self.position["long"]["symbol"],
                "side": "Sell",
                "orderType": "Market",
                "qty": str(self.position["long"]["qty"]),
                "positionIdx": 0,
                "reduceOnly": True
            })
            
            if result_long.get("retCode") != 0:
                self.log(f"Warning: Failed to close long: {result_long}")
            
            # Close short position
            result_short = self._request("POST", "/v5/order/create", body={
                "category": "linear",
                "symbol": self.position["short"]["symbol"],
                "side": "Buy",
                "orderType": "Market",
                "qty": str(self.position["short"]["qty"]),
                "positionIdx": 0,
                "reduceOnly": True
            })
            
            if result_short.get("retCode") != 0:
                self.log(f"Warning: Failed to close short: {result_short}")
            
            # Log trades
            self.log_trade("CLOSE", PAIR["long"], "Sell", self.position["long"]["qty"],
                          price_long, self.position["entry_z"], reason, pnl_long)
            self.log_trade("CLOSE", PAIR["short"], "Buy", self.position["short"]["qty"],
                          price_short, self.position["entry_z"], reason, pnl_short)
            
            # Reset position
            self.position = {"long": None, "short": None, "entry_time": None, "entry_z": None, "entry_balance": None}
            
            self.log(f"[OK] Spread position closed")
            self.log(f"{'='*50}")

            # Save state
            self.save_state()

            return True
            
        except Exception as e:
            self.log(f"[ERR] Error closing position: {e}")
            return False
    
    def generate_daily_report(self):
        """Generate daily trading report"""
        today = datetime.now().date()
        
        with open(DAILY_REPORT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"DAILY REPORT - {today}\n")
            f.write(f"{'='*50}\n")
            f.write(f"Daily PnL: ${self.daily_pnl:.2f}\n")
            f.write(f"Daily Trades: {self.daily_trades}\n")
            f.write(f"Current Balance: ${self.get_balance():.2f}\n")
            
            if self.initial_balance > 0:
                total_return = (self.get_balance() - self.initial_balance) / self.initial_balance
                f.write(f"Total Return: {total_return:.2%}\n")
            
            f.write(f"{'='*50}\n")
    
    def log(self, message: str):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def run(self):
        """Main trading loop"""
        # Record initial balance
        try:
            self.initial_balance = self.get_balance()
        except:
            self.initial_balance = float('inf')

        # Check for existing positions on Bybit
        try:
            pos_long = self.get_position(PAIR["long"])
            pos_short = self.get_position(PAIR["short"])

            if pos_long and pos_short:
                self.log("Existing positions found on Bybit")
                # Restore position state from API
                if not self.position["long"]:
                    self.position = {
                        "long": {"symbol": PAIR["long"], "qty": float(pos_long["size"]),
                                 "side": "Buy", "price": float(pos_long["avgPrice"])},
                        "short": {"symbol": PAIR["short"], "qty": float(pos_short["size"]),
                                  "side": "Sell", "price": float(pos_short["avgPrice"])},
                        "entry_time": datetime.now().isoformat(),
                        "entry_z": 0,
                        "entry_balance": self.initial_balance
                    }
                    self.save_state()
            elif self.position["long"] and not pos_long:
                self.log("Local state has position but Bybit doesn't - resetting")
                self.position = {"long": None, "short": None, "entry_time": None, "entry_z": None, "entry_balance": None}
                self.save_state()
        except Exception as e:
            self.log(f"Warning: Could not check existing positions: {e}")
        
        self.log("=" * 60)
        self.log("Spread Trading Bot Started (GERCHIK EDITION)")
        self.log(f"Pair: {PAIR['long']}/{PAIR['short']}")
        self.log(f"Entry Z: {ENTRY_Z}, Exit Z: {EXIT_Z}, Stop Z: {STOP_Z}")
        self.log(f"Position Size: {POSITION_SIZE_USDT} USDT per leg")
        self.log(f"Leverage: {LEVERAGE}x")
        self.log(f"Initial Balance: {self.initial_balance:.2f} USDT")
        self.log(f"Max Daily Loss: {MAX_DAILY_LOSS:.2%}")
        self.log(f"Max Trades/Day: {MAX_TRADES_PER_DAY}")
        self.log(f"Trading Hours: {TRADING_HOURS_START}:00 - {TRADING_HOURS_END}:00 UTC")
        self.log("=" * 60)
        
        last_report_hour = -1
        
        while True:
            try:
                # Generate hourly report
                current_hour = datetime.now().hour
                if current_hour != last_report_hour and current_hour == 0:
                    self.generate_daily_report()
                    last_report_hour = current_hour
                
                # Check trading hours
                if not self.is_trading_hours():
                    self.log("Outside trading hours, waiting...")
                    time.sleep(300)  # Check every 5 minutes
                    continue
                
                # Fetch klines
                klines1 = self.get_klines(PAIR["long"])
                klines2 = self.get_klines(PAIR["short"])
                
                closes1 = [k["close"] for k in klines1]
                closes2 = [k["close"] for k in klines2]
                volumes1 = [k["volume"] for k in klines1]
                volumes2 = [k["volume"] for k in klines2]
                
                # Calculate spread
                spread_info = self.calculate_spread(closes1, closes2)
                z_score = spread_info["z_score"]
                
                # Detect anomalies
                anomaly_info = self.detect_anomaly(spread_info["history"], volumes1, volumes2)
                
                # Log current status
                status = f"Spread: {spread_info['spread']:.4f} | Z-Score: {z_score:.2f}"
                if anomaly_info["has_anomaly"]:
                    status += f" | ANOMALY: {[a['type'] for a in anomaly_info['anomalies']]}"
                self.log(status)
                
                # Check for signals
                if not self.position["long"]:
                    # No position - check for entry
                    if z_score > ENTRY_Z:
                        self.log(f"Entry signal: Z-Score {z_score:.2f} > {ENTRY_Z}")
                        self.open_spread_position(z_score, "Z-Score above threshold")
                    elif z_score < -ENTRY_Z:
                        self.log(f"Entry signal: Z-Score {z_score:.2f} < -{ENTRY_Z}")
                        self.open_spread_position(z_score, "Z-Score below threshold")
                
                else:
                    # Has position - check for exit
                    entry_z = self.position["entry_z"]
                    
                    # Exit conditions
                    if abs(z_score) < EXIT_Z:
                        self.close_spread_position("Z-Score normalized")
                    elif abs(z_score) > STOP_Z:
                        self.close_spread_position("Stop loss triggered")
                    elif (entry_z > 0 and z_score < -ENTRY_Z) or (entry_z < 0 and z_score > ENTRY_Z):
                        self.close_spread_position("Spread reversed")
                
                # Wait before next iteration
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                self.log("Bot stopped by user")
                self.generate_daily_report()
                break
            except Exception as e:
                self.log(f"Error: {e}")
                time.sleep(60)


if __name__ == "__main__":
    bot = BybitSpreadBot()
    bot.run()
