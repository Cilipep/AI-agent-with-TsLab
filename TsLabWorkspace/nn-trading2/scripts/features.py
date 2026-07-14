import numpy as np
import pandas as pd


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist


def compute_bollinger(series, period=20, std_dev=2):
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    width = (upper - lower) / middle
    pct_b = (series - lower) / (upper - lower)
    return upper, middle, lower, width, pct_b


def compute_atr(high, low, close, period=14):
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def compute_adx(high, low, close, period=14):
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    atr = compute_atr(high, low, close, period)
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
    adx = dx.rolling(window=period).mean()
    return adx, plus_di, minus_di


def compute_stochastic(high, low, close, k_period=14, d_period=3):
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    d = k.rolling(window=d_period).mean()
    return k, d


def compute_williams_r(high, low, close, period=14):
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    return -100 * (highest_high - close) / (highest_high - lowest_low + 1e-10)


def compute_cci(high, low, close, period=20):
    tp = (high + low + close) / 3
    tp_sma = tp.rolling(window=period).mean()
    tp_mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return (tp - tp_sma) / (0.015 * tp_mad + 1e-10)


def compute_mfi(high, low, close, volume, period=14):
    tp = (high + low + close) / 3
    mf = tp * volume
    positive_mf = mf.where(tp > tp.shift(), 0).rolling(window=period).sum()
    negative_mf = mf.where(tp < tp.shift(), 0).rolling(window=period).sum()
    mfi = 100 - (100 / (1 + positive_mf / (negative_mf + 1e-10)))
    return mfi


def compute_obv(close, volume):
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv


def compute_vwap(high, low, close, volume):
    tp = (high + low + close) / 3
    vwap = (tp * volume).cumsum() / volume.cumsum()
    return vwap


def compute_all_features(df):
    df = df.copy()

    # Price-based
    df['returns'] = df['close'].pct_change()
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    df['high_low_range'] = (df['high'] - df['low']) / df['close']
    df['high_close_range'] = (df['high'] - df['close']) / df['close']
    df['low_close_range'] = (df['close'] - df['low']) / df['close']

    # Moving averages
    for period in [5, 9, 10, 20, 50]:
        df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        df[f'dist_sma_{period}'] = (df['close'] - df[f'sma_{period}']) / df[f'sma_{period}']
        df[f'dist_ema_{period}'] = (df['close'] - df[f'ema_{period}']) / df[f'ema_{period}']

    # RSI
    for period in [7, 14, 21]:
        df[f'rsi_{period}'] = compute_rsi(df['close'], period)

    # MACD
    df['macd'], df['macd_signal'], df['macd_hist'] = compute_macd(df['close'])

    # Bollinger Bands
    df['bb_upper'], df['bb_middle'], df['bb_lower'], df['bb_width'], df['bb_pct_b'] = compute_bollinger(df['close'])

    # ATR
    df['atr_14'] = compute_atr(df['high'], df['low'], df['close'], 14)
    df['atr_7'] = compute_atr(df['high'], df['low'], df['close'], 7)

    # ADX
    df['adx'], df['plus_di'], df['minus_di'] = compute_adx(df['high'], df['low'], df['close'])

    # Stochastic
    df['stoch_k'], df['stoch_d'] = compute_stochastic(df['high'], df['low'], df['close'])

    # Williams %R
    df['williams_r'] = compute_williams_r(df['high'], df['low'], df['close'])

    # CCI
    df['cci'] = compute_cci(df['high'], df['low'], df['close'])

    # MFI
    df['mfi'] = compute_mfi(df['high'], df['low'], df['close'], df['volume'])

    # Volume
    df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / (df['volume_sma_20'] + 1e-10)
    df['obv'] = compute_obv(df['close'], df['volume'])
    df['vwap'] = compute_vwap(df['high'], df['low'], df['close'], df['volume'])

    # Volatility
    df['volatility_20'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
    df['volatility_10'] = df['close'].rolling(window=10).std() / df['close'].rolling(window=10).mean()

    # Momentum
    for period in [5, 10, 20]:
        df[f'momentum_{period}'] = df['close'] / df['close'].shift(period) - 1
        df[f'roc_{period}'] = (df['close'] - df['close'].shift(period)) / (df['close'].shift(period) + 1e-10)

    # Price patterns
    df['doji'] = (np.abs(df['close'] - df['open']) / (df['high'] - df['low'] + 1e-10) < 0.1).astype(int)
    df['hammer'] = ((df['close'] - df['low']) / (df['high'] - df['low'] + 1e-10) > 0.7).astype(int)
    df['shooting_star'] = ((df['high'] - df['close']) / (df['high'] - df['low'] + 1e-10) > 0.7).astype(int)

    return df


def make_label(df, horizon=5, threshold=0.001):
    future_returns = df['close'].shift(-horizon) / df['close'] - 1
    label = (future_returns > threshold).astype(int)
    return label


def auto_select_features(df, label, max_features=40):
    feature_cols = [c for c in df.columns if c not in
                    {'Open', 'High', 'Low', 'Close', 'Volume', 'label', 'timestamp', 'date'}
                    and df[c].dtype in [np.float64, np.float32, np.int64]
                    and not df[c].isna().all()]

    correlations = {}
    for col in feature_cols:
        valid_mask = df[col].notna() & label.notna()
        if valid_mask.sum() > 100:
            corr = abs(df.loc[valid_mask, col].corr(label[valid_mask]))
            if not np.isnan(corr):
                correlations[col] = corr

    sorted_features = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
    selected = [f for f, _ in sorted_features[:max_features]]

    if len(selected) < max_features:
        remaining = [f for f in feature_cols if f not in selected]
        selected.extend(remaining[:max_features - len(selected)])

    return selected[:max_features]
