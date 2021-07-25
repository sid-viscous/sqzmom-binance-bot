from wenmoon.strategies.strategy_utils import f_ema, f_rsi, get_candle_values_as_list

# Parameters
FAST_WINDOW = 6
MID_WINDOW = 12
SLOW_WINDOW = 24
EMA_WINDOW = 9


class Strategy:

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

        # Calculate fast, medium, slow rsi
        rsi_fast = f_rsi(close_prices, FAST_WINDOW)
        rsi_mid = f_rsi(close_prices, MID_WINDOW)
        rsi_slow = f_rsi(close_prices, SLOW_WINDOW)

        # Calculte EMA for each RSI
        ema_rsi_fast = f_ema(rsi_fast, EMA_WINDOW)
        ema_rsi_mid = f_ema(rsi_mid, EMA_WINDOW)
        ema_rsi_slow = f_ema(rsi_slow, EMA_WINDOW)

        # Calculate flags
        flag_a = rsi_slow[-1] > rsi_slow[-2]
        flag_b = rsi_fast[-1] > rsi_mid[-1] and rsi_mid[-1] > rsi_slow[-1]

        # Set the strategy recommended action

        action = "none"

        # Enter long position
        if flag_a:
            action = "buy"

#       Exit strategy goes here
        if not (flag_a or flag_b):
            action = "sell"

        return action
