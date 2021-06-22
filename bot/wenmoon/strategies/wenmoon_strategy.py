from wenmoon.strategies.strategy_utils import f_ema, f_macd, get_kline_values_as_list

# Parameters
EMA_WINDOW = 10
MACD_WINDOW_SLOW = 26
MACD_WINDOW_FAST = 12
MACD_WINDOW_SIGNAL = 9

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

        # Useful for dumping data into excel for testing
        # print("+++++++++++++")
        # print("Open High Low Close")
        # for i in range(len(close_prices)):
        #     print(f"{open_prices[i]} {high_prices[i]} {low_prices[i]} {close_prices[i]}")
        # print("--------------")
        # Get indicators
        ema = f_ema(close_prices, EMA_WINDOW)
        macd = f_macd(close_prices, MACD_WINDOW_SLOW, MACD_WINDOW_FAST, MACD_WINDOW_SIGNAL)

        position = "long"

        return position
