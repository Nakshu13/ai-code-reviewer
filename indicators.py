import pandas as pd
import numpy as np

def calculate_sma(data: pd.DataFrame, window: int = 20):
    """
    Simple Moving Average
    """
    sma = data["Close"].rolling(window=window).mean()
    return sma

def calculate_ema(data: pd.DataFrame, window: int = 20):
    """
    Exponential Moving Average
    """
    ema = data["Close"].ewm(span=window, adjust=False).mean()
    return ema

def calculate_rsi(data, window=14):
    delta = data["Close"].diff()

    # Converting to 1D arrays
    delta = delta.values.flatten()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    # Rolling averages
    gain_rolling = pd.Series(gain).rolling(window=window).mean()
    loss_rolling = pd.Series(loss).rolling(window=window).mean()

    rs = gain_rolling / loss_rolling
    rsi = 100 - (100 / (1 + rs))

    return rsi
