import json
from binance import Client
from wenmoon.bot_utils import format_websocket_result, format_historical_klines, calculate_start_date
from wenmoon.Trader import Trader


class Bot:
    """Main engine for handling market data.

    Stores the candle data and queries the Trader class for the recommended position.

    Attributes:
        config: An instance of the configuration class, which should already be initialised.
        binance_client: An instance of the binance client, used for getting historic data and submitting orders.
        candles (list of dict): The most recent list of closed historic candles.
        strategy (class): The class definition for the chosen strategy.
        newest_kline (dict): The most recent kline from the websocket.
        symbol_info (dict): Information about the symbol being traded; rules, filters etc.
        trader (Trader): Instance of the trader class.
    """

    def __init__(self, config, strategy, binance_client):
        """Initialise the bot.

        This class handles the connections to the binance API, including websockets for live data, and client for
        historic data.

        It also feeds this data to the Trader object, where a decision is made on the current position.

        When the Bot is initialised, it is logged in using the API credentials, and historical candle data is requested.

        Note: Requests made to the normal binance api are subject to limits, websockets are not limited.

        Args:
            config: An instance of the configuration class, which should already be initialised.
            strategy: A class definition for the strategy to be used.
            binance_client: Instance of the Binance client, used for getting historical data and placing orders.

        """
        self.config = config
        self.binance_client = binance_client
        self.candles = None
        self.strategy = strategy
        self.newest_kline = None
        self.symbol_info = None
        self.trader = Trader(config, strategy)
        self.get_historical_klines()

    def get_historical_klines(self):
        """Gets the historic price kline data from the binance api.

        Results are stored in an instance variable.

        The documentation for the returned kline data at this endpoint can be found at the following link:
        https://github.com/binance/binance-public-data/#klines
        """
        print("Getting candle data")
        # Calculate time to query for
        start_time = calculate_start_date(
            self.config.interval_number * self.config.max_candles,
            self.config.interval_unit
        )
        # Get the klines as a generator
        historical_klines = self.binance_client.get_historical_klines_generator(
            symbol=self.config.watch_symbol_pair,
            interval=self.config.interval,
            start_str=str(start_time.timestamp())
        )

        self.candles = format_historical_klines(historical_klines)

    def handle_websocket_message(self, msg):
        """When a websocket message is received, this function is called.

        The websocket returns live price data. When a new epoch is started, the websocket returns a flag for the kline
        being closed. This is used as an indicator in the bot for the start of a new epoch.

        TODO: Check this strategy for detecting new epochs is appropriate, consider a scheduled approach.

        See the following link for the data structure returned from the websocket:
        https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#klinecandlestick-streams

        Args:
            msg (dict): A dictionary containing the kline data

        """

        kline = format_websocket_result(json.loads(msg))

        # Store the recent kline
        self.newest_kline = kline

        if kline["event_type"] == "error":
            # On error, close and restart the websocket
            print("Error: websocket connection issue")
        else:
            # For normal messages
            if kline["is_kline_closed"]:
                # Update historical klines
                self.add_new_kline(kline)

                # Print the candle data if requested in the config
                if self.config.output_websocket:
                    for candle in self.candles:
                        print(candle)
                        # print("To stop candles output, enter 'c'")

                # Give the trader the new candle data and take action if required
                self.trader.set_position(self.candles)


            if self.config.output_websocket:
                print(kline)
                # print("To stop the websocket output, enter 'w'")

    def start(self):
        """This function is called whenever the websocket connection starts.

        A start can happen at the initial running of the bot, or after an error.
        """

        # Delete old candle data (we might be missing a few) and get historical candles
        self.candles = []
        self.get_historical_klines()

        # Ensure we are in the correct position (in the case of a restart we might have missed a buy/sell signal)
        self.trader.set_position(self.candles)

    def add_new_kline(self, kline):
        """Adds the newest kline from the websocket and deletes the oldest one.

        The formats for the historical klines and websocket klines are slightly different, however the OHLC is
        the same for both.

        Args:
            kline (dict): Human readable candle data.
        """
        # Add the new candle
        self.candles.append(kline)

        # Remove the first item
        self.candles.pop(0)
