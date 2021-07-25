import numpy

from wenmoon.strategies.strategy_utils import f_ema, f_macd, f_atr, f_ohlc4, get_candle_values_as_list

# Strategy from https://kodify.net/tradingview/strategies/sma-crossover/

# Parameters
WINDOW_LEN = 28
V_LEN = 14


class Strategy:

    def __init__(self, symbol_info):
        self.long_stop_prev = None
        self.short_stop_prev = None
        self.symbol_info = symbol_info

    def scout(self, historical_candles):
        """Strategy function should be stored in scout function.
         It should return the string 'long' or 'short'.
         Strings have been used here in case future strategies have more positions.

        Args:
            historical_candles (list of dict): Historical market candles for the selected trading symbol

        Returns:
            string: The position chosen by the strategy (options: "long", "short", "neutral")
        """
        # Get required candles, EMA and MACD require close price, and ATR requires open, high, low, close prices
        close_prices = get_candle_values_as_list(historical_candles, "close_price")
        open_prices = get_candle_values_as_list(historical_candles, "open_price")
        high_prices = get_candle_values_as_list(historical_candles, "high_price")
        low_prices = get_candle_values_as_list(historical_candles, "low_price")
        volumes = get_candle_values_as_list((historical_candles), "volume")

        # Get indicators
        source = close_prices
        hi_low = numpy.subtract(high_prices, low_prices)*100
        open_close = numpy.subtract(close_prices, open_prices)*100


        # macd_hist = f_macd(close_prices, MACD_WINDOW_SLOW, MACD_WINDOW_FAST, MACD_WINDOW_SIGNAL)
        # atr = f_atr(high_prices, low_prices, close_prices, ATR_WINDOW, ATR_MULTIPLIER)
        # ohlc4 = f_ohlc4(open_prices, high_prices, low_prices, close_prices, ATR_WINDOW)
        #
        # # Chandelier exit
        # long_stop = max(ohlc4) - atr[-1]
        # short_stop = min(ohlc4) + atr[-1]
        #
        # # For the first iteration, set the previous long stop
        # if not self.long_stop_prev:
        #     self.long_stop_prev = long_stop
        #
        # if close_prices[-2] > self.long_stop_prev:
        #     long_stop = max(long_stop, self.long_stop_prev)
        #
        # # For the first iteration, set the previous short stop
        # if not self.short_stop_prev:
        #     self.short_stop_prev = short_stop
        #
        # if ohlc4[-2] < self.short_stop_prev:
        #     short_stop = min(short_stop, self.short_stop_prev)
        #
        # if macd_hist[-1] > 0:
        #     position = "long"
        # elif macd_hist[-1] < 0:
        #     position = "short"
        # else:
        #     position = "neutral"



        # Useful for dumping data into excel for testing
        print("+++++++++++++")
        print("Open High Low Close Volume")
        for i in range(len(close_prices)):
            print(f"{open_prices[i]} {high_prices[i]} {low_prices[i]} {close_prices[i]} {volumes[i]}")
        print("--------------")

        # print("MACD_HIST")
        # for p in macd:
        #     print(p)
        #
        # print("ATR")
        # for p in atr:
        #     print(p)
        #
        # print("OHLC4")
        # for p in ohlc4:
        #     print(p)
        #
        # print("long_stop")
        # print(long_stop)
        #
        # print("short_stop")
        # print(short_stop)
        #
        #
        #
        #
        # print(f"macd_hist = {macd_hist[-1]}")
        # print(f"long_stop_prev = {self.long_stop_prev}")
        # print(f"short_stop_prev = {self.short_stop_prev}")
        # print(f"long_stop = {long_stop}")
        # print(f"short_stop = {short_stop}")
        # print(f"recommended position = {position}")
        #
        # # Set the stop values for next iteration
        # self.long_stop_prev = long_stop
        # self.short_stop_prev = short_stopprint("MACD_HIST")
        # for p in macd:
        #     print(p)
        #
        # print("ATR")
        # for p in atr:
        #     print(p)
        #
        # print("OHLC4")
        # for p in ohlc4:
        #     print(p)
        #
        # print("long_stop")
        # print(long_stop)
        #
        # print("short_stop")
        # print(short_stop)
        #
        #
        #
        #
        # print(f"macd_hist = {macd_hist[-1]}")
        # print(f"long_stop_prev = {self.long_stop_prev}")
        # print(f"short_stop_prev = {self.short_stop_prev}")
        # print(f"long_stop = {long_stop}")
        # print(f"short_stop = {short_stop}")
        # print(f"recommended position = {position}")
        #
        # # Set the stop values for next iteration
        # self.long_stop_prev = long_stop
        # self.short_stop_prev = short_stop

        return position
