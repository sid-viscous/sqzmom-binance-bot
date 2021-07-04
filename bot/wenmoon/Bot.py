import numpy as np
from binance import Client, ThreadedWebsocketManager
from wenmoon.bot_utils import format_websocket_result, format_historical_klines, calculate_start_date
from wenmoon.Trader import Trader


class Bot:
    def __init__(self, config, strategy):
        """Initialise the bot.

        This class handles the connections to the binance API, including websockets for live data, and client for
        historic data.

        It also feeds this data to the Trader object, where a decision is made on the current position.

        Note: Requests made to the normal binance api are subject to limits, websockets are not limited.

        Args:
            config: An instance of the configuration class, which should already be initialised.
            strategy: A class definition for the strategy to be used.

        Attributes:
            config: An instance of the configuration class, which should already be initialised.
            websocket: An instance of the threaded websocket connection manager.
            websocket_key: The key for the websocket thread.
            binance_client: An instance of the binance client, used for getting historic data and submitting orders.
            candles (list of dict): The most recent list of closed historic candles.
            strategy (class): The class definition for the chosen strategy.
            newest_kline (dict): The most recent kline from the websocket.
            trader (Trader): Instance of the trader class.
        """
        self.config = config
        self.websocket = ThreadedWebsocketManager()
        self.websocket_key = None
        self.binance_client = None
        self.candles = None
        self.strategy = strategy
        self.newest_kline = None
        self.trader = Trader(config, strategy)

    def login(self):
        """Logs into the binance client API using the supplied api key and secret."""
        self.binance_client = Client(
            self.config.api_key,
            self.config.secret_key
        )

    def get_historical_klines(self):
        """Gets the historic price kline data from the binance api.

        Results are stored in an instance variable.

        The documentation for the returned kline data at this endpoint can be found at the following link:
        https://github.com/binance/binance-public-data/#klines
        """
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
        kline = format_websocket_result(msg)

        # Store the recent kline
        self.newest_kline = kline

        if kline["event_type"] == "error":
            # On error, close and restart the websocket
            print("Error: websocket connection issue")
            self.stop_kline_websocket()
            self.start_kline_websocket()
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
                self.trader.handle_new_kline(self.candles)


            if self.config.output_websocket:
                print(kline)
                # print("To stop the websocket output, enter 'w'")

    def start_kline_websocket(self):
        """Starts the websocket connection.

        The instance of the websocket manager, and the key to its thread are stored as instance variables.

        The callback function for when a websocket message is received is also specified here.
        """
        print(f"Starting websocket connection, watching symbol {self.config.watch_symbol_pair}")
        try:
            self.websocket.start()
            self.websocket_key = self.websocket.start_kline_socket(
                callback=self.handle_websocket_message,
                symbol=self.config.watch_symbol_pair
            )
        except:
            print("Error: cannot connect to websocket")

    def stop_kline_websocket(self):
        """Ends the connection to the websocket."""
        try:
            self.websocket.stop()
        except:
            print("Error: cannot stop connection to websocket")

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
