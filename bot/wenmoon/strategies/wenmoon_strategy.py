from wenmoon.strategies.strategy_utils import f_ema, f_macd, f_atr, f_ohlc4, get_kline_values_as_list

# Parameters
EMA_WINDOW = 10
MACD_WINDOW_SLOW = 27
MACD_WINDOW_FAST = 12
MACD_WINDOW_SIGNAL = 7
ATR_WINDOW = 20
ATR_MULTIPLIER = 2.0


class Strategy:

    @staticmethod
    def scout(historical_klines, current_kline):
        """Strategy function should be stored in scout function.
         It should return the string 'long' or 'short'.
         Strings have been used here in case future strategies have multiple positions.

        Args:
            historical_klines (list of dict): Historical market klines (candles) for the selected trading symbol
            current_kline (dict): The most up to date kline from the websocket (may not be closed)

        Returns:
            string: The position chosen by the strategy (options: "long" or "short")
        """
        # Get required candles, EMA and MACD require close price, and ATR requires open, high, low, close prices
        close_prices = get_kline_values_as_list(historical_klines, "close_price")
        open_prices = get_kline_values_as_list(historical_klines, "open_price")
        high_prices = get_kline_values_as_list(historical_klines, "high_price")
        low_prices = get_kline_values_as_list(historical_klines, "low_price")



        # Get indicators
        macd = f_macd(close_prices, MACD_WINDOW_SLOW, MACD_WINDOW_FAST, MACD_WINDOW_SIGNAL)
        atr = f_atr(high_prices, low_prices, close_prices, ATR_WINDOW, ATR_MULTIPLIER)
        ohlc4 = f_ohlc4(open_prices, high_prices, low_prices, close_prices, ATR_WINDOW)

        # Chandelier exit
        long_stop = max(ohlc4) - atr[-1]
        short_stop = min(ohlc4) + atr[-1]

        # Useful for dumping data into excel for testing
        # print("+++++++++++++")
        # print("Open High Low Close")
        # for i in range(len(close_prices)):
        #     print(f"{open_prices[i]} {high_prices[i]} {low_prices[i]} {close_prices[i]}")
        # print("--------------")
        #
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




        # TODO: Replace this with actual strategy
        position = "long"

        return position
