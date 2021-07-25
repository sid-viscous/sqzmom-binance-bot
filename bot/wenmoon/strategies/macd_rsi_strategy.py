from wenmoon.strategies.strategy_utils import f_macd, f_rsi, get_candle_values_as_list

# Parameters
RSI_WINDOW = 14
FAST_WINDOW = 17
SLOW_WINDOW = 37
SIGNAL_WINDOW = 9
RSI_CUTOFF = 35


class Strategy:
    """Strategy based on MACD and RSI.

    Buys on MACD upward crossover but only if the RSI is below the threshold.

    Sells on MACD downward crossover.

    Status:
        Back-tested on TV.
        Initial testing in bot.
        Deploying on server.

    """

    def __init__(self, symbol_info, candles_type="normal"):
        self.long_stop_prev = None
        self.short_stop_prev = None
        self.symbol_info = symbol_info
        self.candles_type = candles_type

    def scout(self, historical_candles):
        """Strategy function should be stored in scout function.
         It should return the string 'long' or 'short'.
         Strings have been used here in case future strategies have more positions.

        Args:
            historical_candles (list of dict): Historical market candles for the selected trading symbol

        Returns:
            string: The position chosen by the strategy (options: "none", "buy", "sell")
        """
        # Get required candles, EMA and MACD require close price, and ATR requires open, high, low, close prices
        close_prices = get_candle_values_as_list(historical_candles, "close_price")
        open_prices = get_candle_values_as_list(historical_candles, "open_price")
        high_prices = get_candle_values_as_list(historical_candles, "high_price")
        low_prices = get_candle_values_as_list(historical_candles, "low_price")
        volumes = get_candle_values_as_list(historical_candles, "volume")

        # Calculate rsi
        rsi = f_rsi(close_prices, RSI_WINDOW)

        # Calculte MACD indicator
        macd_line, macd_signal, macd_histogram = f_macd(close_prices, SLOW_WINDOW, FAST_WINDOW, SIGNAL_WINDOW)

        # Set up conditions - Buy
        # Check MACD histogram has just changed from negative to positive
        buy_condition_1 = macd_histogram[-2] < 0 and macd_histogram[-1] > 0

        # Check rsi is below the cutoff
        buy_condition_2 = rsi[-1] <= RSI_CUTOFF

        # Check MACD line is below zero
        buy_condition_3 = macd_line[-1] < 0

        # Set up conditions - Sell
        # Check MACD histogram has just changed from positive to negative
        sell_condition_1 = macd_histogram[-2] > 0 and macd_histogram[-1] < 0

        # Check MACD line is above zero
        sell_condition_2 = macd_line[-1] > 0

        # Set the strategy recommended action (by default, do nothing)
        action = "none"

        # Check buy conditions and set buy flag if met
        if buy_condition_1 and buy_condition_2 and buy_condition_3:
            action = "buy"

        # Check sell conditions and set sell flag if met
        if sell_condition_1 and sell_condition_2:
            action = "sell"

        # Print strategy data
        print("MACD RSI strategy data")
        print("Buy condition 1: macd_histogram[-2] < 0 and macd_histogram[-1] > 0")
        print(f"  macd_histogram[-2] = {macd_histogram[-2]}")
        print(f"  macd_histogram[-1] = {macd_histogram[-1]}")
        print(f"  Condition 1 met?: {buy_condition_1}")
        print(f"Buy condition 2: rsi[-1] <= {RSI_CUTOFF}")
        print(f"  rsi[-1] = {rsi[-1]}")
        print(f"  Buy condition 2 met?: {buy_condition_2}")
        print("Buy condition 3: macd_line[-1] < 0")
        print(f"  macd_line[-1] = {macd_line[-1]}")
        print(f"  Buy condition 3 met?: {buy_condition_3}")
        print("Sell condition 1: macd_histogram[-2] > 0 and macd_histogram[-1] < 0")
        print(f"  macd_histogram[-2] = {macd_histogram[-2]}")
        print(f"  macd_histogram[-1] = {macd_histogram[-1]}")
        print(f"  Sell condition 1 met?: {sell_condition_1}")
        print("Sell condition 2: macd_line[-1] > 0")
        print(f"  macd_line[-1] = {macd_line[-1]}")
        print(f"  Sell condition 2 met?: {sell_condition_2}")

        return action
