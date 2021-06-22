import numpy as np

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

    # Final MACD
    offset_2 = len(macd_diff) - len(macd_signal)
    macd = list(np.array(macd_diff[offset_2:]) - np.array(macd_signal))

    return macd

def get_kline_values_as_list(klines, key):
    result = []
    for kline in klines:
        result.append(kline[key])

    return result
