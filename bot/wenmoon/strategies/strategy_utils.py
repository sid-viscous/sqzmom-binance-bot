import numpy as np


def get_candle_values_as_list(candles, key):
    """Extracts all values from single key in a list of candles.

    Args:
        candles (list of dict): Candles (human readable format).
        key (str): Key to extract from the list of Klines.

    Returns:
        list: The extracted value from each of the candles.
    """
    result = []
    for candle in candles:
        result.append(candle[key])

    return result

def get_heikin_ashi_candles(open_prices, high_prices, low_prices, close_prices):
    """Converts regular candles to Heikin Ashi candles.

    Args:
        open_prices:
        high_prices:
        low_prices:
        close_prices:

    Returns:

    """
    open_ha = []
    low_ha = []
    high_ha = []
    close_ha = []

    for i in range(len(open_prices)):
        close_ha.append(np.mean([open_prices[i], close_prices[i], low_prices[i], high_prices[i]]))
        if i == 0:
            open_ha.append(open_prices[i])
        else:
            open_ha.append(np.mean([open_ha[i-1], close_ha[i-1]]))
        high_ha.append(max([high_prices[i], open_ha[i], close_ha[i]]))
        low_ha.append(min([low_prices[i], open_ha[i], close_ha[i]]))

    return open_ha, high_ha, low_ha, close_ha


def k(candles, window):
    """Gets the most recent candles.

    Args:
        candles (list of dict): Candle data
        window (int): number of candles to extract

    Returns:
        list of dict: Recent candle data
    """
    return candles[-window:]

def l(list_1, window):
    """Gets the most recent items in the list.

    Args:
        list_1 (list): Source list
        window (int): Window to include

    Returns:
        list: List containing most recent items
    """
    return list_1[-window:]


def subtract(list_1, list_2):
    """Subtracts list_2 from list_1 even if they are different lengths.

    Length of the returned list will be the length of the shortest list supplied.

    Index 0 is treated as the oldest, and the older list items are truncated.

    Args:
        list_1 (list of float): List to be subtracted from
        list_2 (list of float): List to subtract

    Returns:
        list of float: result of list_1 - list_2
    """
    offset = len(list_1) - len(list_2)
    return list(np.array(list_1[offset:]) - np.array(list_2))


def f_sma(close_prices, window):
    """Calculates standard moving average SMA).

    This function takes historical data, and a moving window to calculate SMA.
    As the moving average takes previous closing prices into account, its length will be len(candles) - window

    Args:
        close_prices (list of float): A list of close prices for each period.
        window (int): The moving window to take averages over.

    Returns:
        list of float: A list of SMAs
    """
    sma = []
    i = 0
    n = len(close_prices) - window + 1

    for i in range(n):
        sma.append(sum(close_prices[i:i+window])/window)
        i += 1

    return sma


def f_ema(close_prices, window):
    """Calculates exponential moving average (EMA).

    This function takes historical data, and a moving window to calculate EMA.
    EMA differs from standard moving average with EMA placing a higher weight on more recent prices.
    As the moving average takes previous closing prices into account, its length will be len(candles) - window

    Args:
        close_prices (list of float): A list of close prices for each period.
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
        list of float: A list of MACD signals (< 0 if downtrend, > 0 if uptrend).
        list of float:
    """
    # Get slow and fast EMA
    ema_slow = f_ema(close_prices, window_slow)
    ema_fast = f_ema(close_prices, window_fast)

    # Difference between slow and fast EMA
    macd_line = subtract(ema_fast, ema_slow)

    # MACD signal line
    macd_signal = f_ema(macd_line, window_signal)

    # MACD histogram
    macd_histogram = subtract(macd_line, macd_signal)

    return macd_line, macd_signal, macd_histogram


def f_atr(high_prices, low_prices, close_prices, window):
    """Calculates average true range (ATR) indicator.

    Args:
        high_prices (list of float): A list of high prices for each period.
        low_prices (list of float): A list of low prices for each period.
        close_prices (list of float): A list of close prices for each period.
        window (int): The window / period to calculate moving averages over.

    Returns:
        list of float: The scaled ATR list
    """
    # Ensure window is positive
    window = max(window, 1)

    # Calculate true range (TR), this will be one element shorter than the price lists
    tr = []
    for i in range(len(high_prices) - 1):
        tr.append(max(
            high_prices[i+1] - low_prices[i+1],
            abs(high_prices[i+1] - close_prices[i]),
            abs(close_prices[i] - low_prices[i+1])
        ))

    # Calculate the ATR from EMA
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

def f_highest(high_prices, window):
    """Gets the highest high price within the window.

    Args:
        high_prices (list of float): A list of high prices for each period
        window (int): The window to compare prices within.

    Returns:
        float: The highest price within the window
    """
    return max(l(high_prices, window))

def f_lowest(low_prices, window):
    """Gets the highest high price within the window.

    Args:
        low (list of float): A list of low prices for each period.
        window (int): The window to compare prices within.

    Returns:
        float: The highest price within the window
    """
    return min(l(low_prices, window))


def f_highestbars(high_prices, window):
    """Returns the number of bars since the highest high price within the window.

    Args:
        high_prices (list of float): A list of high prices for each period.
        window (int): The window / period to compare prices over.

    Returns:
        int: Number of bars since the highest high
    """
    # Get the highest high
    highest = f_highest(high_prices, window)

    # Get the index of the highest high
    idx = high_prices.index(highest)

    # Return the number of bars since this index
    return len(high_prices) - idx


def f_lowestbars(low_prices, window):
    """Returns the number of bars since the lowest low price within the window.

    Args:
        low_prices (list of float):  A list of low prices for each period.
        window (int): The window / period to compare prices over.

    Returns:
        int: Number of bars since the lowest low
    """
    # Get the lowest low
    lowest = f_lowest(low_prices, window)

    # Get the index of the lowest low
    idx = low_prices.index(lowest)

    # Return the number of bars since this index
    return len(low_prices) - idx


def f_change(prices):
    """Calculates the change in prices.

    Args:
        prices (list of float): Price list to calculate change.

    Returns:
        list of float: Difference in current to previous price (length is 1 smaller than prices).
    """
    changes = []
    for i in range(len(prices) - 1):
        changes.append(prices[i+1] - prices[i])

    return changes


def f_rsi(close_prices, window, mode="sma"):
    """Calculates relative strength index.

    Args:
        close_prices (list of float): A list of close prices for each period.
        window (int): The window / period to use in moving averages.

    Returns:
        list of float: RSI curve data.
    """
    # Moving change in close price
    changes = f_change(close_prices)

    # Upward and downward movements
    up_move = []
    down_move = []

    for change in changes:
        if change > 0:
            up_move.append(change)
            down_move.append(0)
        else:
            up_move.append(0)
            down_move.append(abs(change))

    # Get average upward and downward movements
    if mode == "ema":
        # Exponential moving average
        avg_up = f_ema(up_move, window)
        avg_down = f_ema(down_move, window)

    else:
        # Standard moving average
        avg_up = f_sma(up_move, window)
        avg_down = f_sma(down_move, window)

    rsi = []
    for i in range(len(avg_up)):
        # Relative strength
        rs = avg_up[i]/avg_down[i]

        # RSI
        rsi.append(100 - (100/(rs+1)))

    return rsi



