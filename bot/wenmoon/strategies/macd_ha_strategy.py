from wenmoon.strategies.strategy_utils import f_ema, f_macd, f_atr, f_ohlc4, get_kline_values_as_list, \
    get_heikin_ashi_candles

# Parameters
MACD_WINDOW_SLOW = 37
MACD_WINDOW_FAST = 17
MACD_WINDOW_SIGNAL = 9


class Strategy:

    def __init__(self, symbol_info):
        self.symbol_info = symbol_info

    def scout(self, historical_klines):
        """Strategy function should be stored in scout function.
         It should return the string 'long' or 'short'.
         Strings have been used here in case future strategies have more positions.

        Args:
            historical_klines (list of dict): Historical market klines (candles) for the selected trading symbol

        Returns:
            string: The position chosen by the strategy (options: "long", "short", "neutral")
        """
        # Get required candles, EMA and MACD require close price, and ATR requires open, high, low, close prices
        close_prices = get_kline_values_as_list(historical_klines, "close_price")
        open_prices = get_kline_values_as_list(historical_klines, "open_price")
        high_prices = get_kline_values_as_list(historical_klines, "high_price")
        low_prices = get_kline_values_as_list(historical_klines, "low_price")

        # Get Heikin Ashi candles
        open_ha, high_ha, low_ha, close_ha = get_heikin_ashi_candles(open_prices, high_prices, low_prices, close_prices)

        # Get indicators
        macd_hist = f_macd(close_ha, MACD_WINDOW_SLOW, MACD_WINDOW_FAST, MACD_WINDOW_SIGNAL)

        if macd_hist[-1] > 0:
            position = "long"
        elif macd_hist[-1] < 0:
            position = "short"
        else:
            position = "neutral"



        # Useful for dumping data into excel for testing
        # print("+++++++++++++")
        # print("Open High Low Close")
        # for i in range(len(close_prices)):
        #     print(f"{open_prices[i]} {high_prices[i]} {low_prices[i]} {close_prices[i]}")
        # print("--------------")
        #
        # print("MACD_HIST")
        # for p in macd_hist:
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




        print(f"macd_hist = {macd_hist[-1]}")
        print(f"recommended position = {position}")

        return position
