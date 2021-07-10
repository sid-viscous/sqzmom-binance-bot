import numpy as np


def f_sma(close_prices, window):
    """Calculates standard moving average SEMA).

    This function takes historical data, and a moving window to calculate SMA.
    As the moving average takes previous closing prices into account, its length will be len(klines) - window

    Args:
        lose_values (list of float): A list containing the closing values.
        window (int): The moving window to take averages over.

    Returns:
        list of float: A list of SMAs
    """

    sma = []


    # calculate SMA
    # Smoothing factor
    smooth = 2.0/(window + 1.0)

    # Calculate first EMA from simple average
    ema.append(sum(close_prices[:window])/window)

    # Calculate remaining EMA values
    i = 0
    for close_price in close_prices[window:]:
        new_ema = close_price*smooth + ema[-1]*(1.0-smooth)
        ema.append(new_ema)
        i += 1

    return ema

def f_ema(close_prices, window):
    """Calculates exponential moving average (EMA).

    This function takes historical data, and a moving window to calculate EMA.
    EMA differs from standard moving average with EMA placing a higher weight on more recent prices.
    As the moving average takes previous closing prices into account, its length will be len(klines) - window

    Args:
        lose_values (list of float): A list containing the closing values.
        window (int): The moving window to take averages over.

    Returns:
        list of float: A list of EMAs
    """

    ema = []


    # calculate EMA
    # Smoothing factor
    smooth = 2.0/(window + 1.0)

    # Calculate first EMA from simple average
    ema.append(sum(close_prices[:window])/window)

    # Calculate remaining EMA values
    i = 0
    for close_price in close_prices[window:]:
        new_ema = close_price*smooth + ema[-1]*(1.0-smooth)
        ema.append(new_ema)
        i += 1

    return ema


def f_macd(close_prices, window_slow, window_fast, window_signal):
    """Calculates moving average convergence divergence (MACD)

    Args:
        close_prices (list of float): A list of close prices for each period.
        window_slow (int): The moving window to take averages over for the slow MACD period.
        window_fast (int): The moving window to take averages over for the fast MACD period.
        window_signal (int): The moving window to take averages over for the signal MACD period.

    Returns:
        list of float: A list of MACDs
    """
    # Size difference between fast and slow windows
    offset = window_slow - window_fast

    # Get slow and fast EMA
    ema_slow = f_ema(close_prices, window_slow)
    ema_fast = f_ema(close_prices, window_fast)

    # Difference between slow and fast EMA
    macd_diff = list(np.array(ema_fast[offset:]) - np.array(ema_slow))

    # MACD signal line
    macd_signal = f_ema(macd_diff, window_signal)

    # MACD history
    offset_2 = len(macd_diff) - len(macd_signal)
    macd_hist = list(np.array(macd_diff[offset_2:]) - np.array(macd_signal))

    return macd_hist


def f_atr(high_prices, low_prices, close_prices, window, multiplier):
    """Calculates average true range (ATR) indicator.

    Args:
        high_prices (list of float): A list of high prices for each period.
        low_prices (list of float): A list of low prices for each period.
        close_prices (list of float): A list of close prices for each period.
        window (int): The window / period to calculate moving averages over.
        multiplier (float): A scalar multipler for the computer ATR list.

    Returns:
        list of float: The scaled ATR list
    """

    # Calculate true range (TR), this will be one element shorter than the price lists
    tr = []
    for i in range(len(high_prices) - 1):
        tr.append(multiplier * max(
            high_prices[i+1] - low_prices[i+1],
            high_prices[i+1] - close_prices[i],
            close_prices[i] - low_prices[i+1]
        ))

    # Calculate the atr
    atr = f_ema(tr, window)

    return atr

def f_ohlc4(open_prices, high_prices, low_prices, close_prices, window):
    """Shortcut function to calculate the average of open, high, low, close prices.

    Args:
        open_prices: (list of float)  A list of open prices for each period.
        high_prices (list of float): A list of high prices for each period.
        low_prices (list of float):  A list of low prices for each period.
        close_prices: (list of float)  A list of close prices for each period.
        window (int): The window / period to calculate moving averages over.

    Returns:
        list of float: Average OHLC values
    """
    ohlc4 = []
    for i in range(window):
        ohlc4.append(np.average([
            open_prices[-window + i],
            high_prices[-window + i],
            low_prices[-window + i],
            close_prices[-window + i]
        ]))

    return ohlc4


def get_kline_values_as_list(klines, key):
    """Extracts all values from single key in a list of klines.

    Args:
        klines (list of dict): Klines (human readable format).
        key (str): Key to extract from the list of Klines.

    Returns:
        list: The extracted value from each of the klines.
    """
    result = []
    for kline in klines:
        result.append(kline[key])

    return result
