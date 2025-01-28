import ccxt
import pandas as pd
from datetime import datetime
import time
import pandas_ta as ta
import numpy as np

def get_data(
    symbol: str,
    timeframe: str = "1h",
    start_date: str = "2024-01-01T00:00:00Z",
    end_date: str = None,
    exchange_name: str = "binance",
    delay: float = 0.1,
) -> None:
    """
    Fetch OHLCV data for a given symbol and timeframe using CCXT.
    """
    # Initialize the exchange
    exchange = getattr(ccxt, exchange_name)()

    # Set end_date to current UTC time if not provided
    if end_date is None:
        end_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Convert start and end dates to timestamps
    since = exchange.parse8601(start_date)
    until = exchange.parse8601(end_date)

    # List to store all OHLCV data
    all_ohlcv = []

    # Fetch OHLCV data in batches (max 500 rows per request)
    while since < until:
        # Fetch OHLCV data (max 500 rows per request)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=500)

        # If no data is returned, break the loop
        if not ohlcv:
            break

        # Append the data to the list
        all_ohlcv += ohlcv

        # Update the `since` parameter to the timestamp of the last candle + 1ms
        since = ohlcv[-1][0] + 1

        # Sleep to avoid hitting rate limits
        time.sleep(delay)

    # Convert to a pandas DataFrame
    df = pd.DataFrame(all_ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")  # Convert timestamp to datetime
    df.set_index("timestamp", inplace=True)  # Set timestamp as the index

    # Print the DataFrame
    return df

#### Indicators function ####

def add_indicators(
    df: pd.DataFrame,
    length: int = 14,  # Default length for all indicators
    sma_length: int = 50,  # Specific length for SMA
    ema_length: int = 20,  # Specific length for EMA
    atr_length: int = 14,  # Specific length for ATR
    adx_length: int = 14,  # Specific length for ADX
    cci_length: int = 20,  # Specific length for CCI
    roc_length: int = 14,  # Specific length for ROC
    willr_length: int = 14,  # Specific length for Williams %R
    cmf_length: int = 20,  # Specific length for CMF
    vwma_length: int = 20,  # Specific length for VWMA
) -> pd.DataFrame:
    """
    Add technical indicators to the DataFrame.
    """
    # Calculate EMA (Exponential Moving Average)
    df[f'EMA_{ema_length}_period'] = df['close'].ewm(span=ema_length, adjust=False).mean()

    # Calculate SMA (Simple Moving Average)
    df[f'SMA_{sma_length}_period'] = df['close'].rolling(window=sma_length).mean()

    # Calculate RSI (Relative Strength Index)
    df[f'RSI_{length}_period'] = ta.rsi(df['close'], length=length)

    # Calculate ATR (Average True Range)
    df[f'ATR_{atr_length}_period'] = ta.atr(df['high'], df['low'], df['close'], length=atr_length)

    # Calculate VWAP (Volume Weighted Average Price)
    df['VWAP'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])

    # Calculate ADX (Average Directional Index)
    df[f'ADX_{adx_length}_period'] = ta.adx(df['high'], df['low'], df['close'], length=adx_length)['ADX_14']

    # Calculate CCI (Commodity Channel Index)
    df[f'CCI_{cci_length}_period'] = ta.cci(df['high'], df['low'], df['close'], length=cci_length)

    # Calculate OBV (On-Balance Volume)
    df['OBV'] = ta.obv(df['close'], df['volume']).astype('float64')

    # Calculate ROC (Rate of Change)
    df[f'ROC_{roc_length}_period'] = ta.roc(df['close'], length=roc_length)

    # Calculate Williams %R
    df[f'Williams_%R_{willr_length}_period'] = ta.willr(df['high'], df['low'], df['close'], length=willr_length).astype('float64')

    # Calculate CMF (Chaikin Money Flow)
    df[f'CMF_{cmf_length}_period'] = ta.cmf(df['high'], df['low'], df['close'], df['volume'], length=cmf_length)

    # Calculate VWMA (Volume Weighted Moving Average)
    df[f'VWMA_{vwma_length}_period'] = ta.vwma(df['close'], df['volume'], length=vwma_length)

    return df

#### Hawkes process function ####

def varu_hawkes(data: pd.Series, kappa: float):
    assert(kappa > 0.0)
    alpha = np.exp(-kappa)
    arr = data.to_numpy()
    output = np.zeros(len(data))
    output[:] = np.nan
    for i in range(1, len(data)):
        if np.isnan(output[i - 1]):
            output[i] = arr[i]
        else:
            output[i] = output[i - 1] * alpha + arr[i]
    return pd.Series(output, index=data.index) * kappa
