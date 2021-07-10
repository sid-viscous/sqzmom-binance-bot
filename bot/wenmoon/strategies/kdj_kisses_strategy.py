from wenmoon.strategies.strategy_utils import f_ema, f_macd, f_atr, f_ohlc4, get_kline_values_as_list

# Parameters
DEPTH = 12
DEVIATION = 5
BACKSTEP = 2


class Strategy:

    def __init__(self, symbol_info):
        self.long_stop_prev = None
        self.short_stop_prev = None
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

        # Get minimum ticker size
        min_tick_size = next(r for r in self.symbol_info["filters"] if r["filterType"] == "PRICE_FILTER")["tickSize"]



        # # Useful for dumping data into excel for testing
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




        # print(f"macd_hist = {macd_hist[-1]}")
        # print(f"long_stop_prev = {self.long_stop_prev}")
        # print(f"short_stop_prev = {self.short_stop_prev}")
        # print(f"long_stop = {long_stop}")
        # print(f"short_stop = {short_stop}")
        # print(f"recommended position = {position}")

        # # Set the stop values for next iteration
        # self.long_stop_prev = long_stop
        # self.short_stop_prev = short_stop

        return position
