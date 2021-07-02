import numpy as np
from binance import Client, ThreadedWebsocketManager
from wenmoon.bot_utils import format_websocket_result, format_historical_klines, calculate_start_date


class Bot:
    def __init__(self, config, strategy):
        """Initialise the bot.

        This class handles the connections to the binance API, including websockets for live data, and client for
        historic data.

        It also feeds this data to the strategy scout function, where a decision is made on the current position.

        Finally, this class also makes calls to submit orders for buying/selling.

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
            position (str): The current position for the strategy (options: "long", "short").
            coin_balance (float): The balance of coin currently trading.
            fiat_balance (float): The balance of fiat currency currently trading.
            newest_kline (dict): The most recent kline from the websocket.
        """
        self.config = config
        self.websocket = ThreadedWebsocketManager()
        self.websocket_key = None
        self.binance_client = None
        self.candles = None
        self.strategy = strategy
        self.position = config.start_position
        self.coin_balance = None
        self.fiat_balance = None
        self.newest_kline = None
        self.set_initial_balance()

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
                self.get_historical_klines()
                for candle in self.candles:
                    if self.config.output_websocket:
                        print(candle)
                        # print("To stop candles output, enter 'c'")

                # ==============================================================
                # DECISION TIME
                # ==============================================================
                print("-----------------------------------------------------------------------------------------------")
                print(f"Checking strategy for position - current position: {self.position}")
                recommended_position = self.strategy.scout(self.candles, kline)

                # Check if position has changed
                if recommended_position != self.position:
                    if recommended_position == "long":
                        print("Going long")
                        self.position = "long"
                        self.enter_long_position()
                    elif recommended_position == "short":
                        print("Going short")
                        self.position = "short"
                        self.enter_short_position()
                    else:
                        # In the almost impossible scenario where the indicator ends on a neutral position, do nothing
                        print(f"recommended position neutral, stay in current position: {self.position}")

                self.output_balances()

                # ==============================================================

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

    def set_initial_balance(self):
        """Checks the starting coin balance is available in the spot wallet.

        For test mode, no verifications take place on the balance.
        """
        if self.config.test_mode:
            if self.config.start_position == "long":
                self.coin_balance = self.config.start_balance
            else:
                self.fiat_balance = self.config.start_balance
        else:
            pass

    def output_balances(self):
        """Gets the current coin and fiat balances and prints them to the console.

        TODO: Output fiat value of coin balance when in long position.
        """
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(f"Coin balance: {self.coin_balance} {self.config.coin_symbol}")
        print(f"Fiat balance: {self.fiat_balance} {self.config.fiat_symbol}")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    def fake_buy(self):
        """Simulates a buy order.

        Takes into account the current price and modifies the balances on the Bot instance.

        TODO: Take into account trading fees for fake buys and sells

        """
        # Get current price
        price = self.newest_kline["close_price"]

        # Calculate coin buy quantity with current funds
        coin_buy_quantity = self.fiat_balance/price

        # Make the fake purchase
        self.fiat_balance = 0
        self.coin_balance = coin_buy_quantity

        # Output message
        print(f"Bought {coin_buy_quantity} {self.config.coin_symbol} at price of {price} {self.config.fiat_symbol}")

    def fake_sell(self):
        """Simulates a sell order.

        Takes into account the current price and modifies the balances on the Bot instance.

        """
        # Get current price
        price = self.newest_kline["close_price"]

        # Calculate fiat buy quantity with current funds
        fiat_buy_quantity = price*self.coin_balance

        # Make the fake sell
        self.coin_balance = 0
        self.fiat_balance = fiat_buy_quantity

        # Output message
        print(f"Sold {self.config.coin_symbol} at price of {price} {self.config.fiat_symbol} for {fiat_buy_quantity} {self.config.fiat_symbol}")

    def enter_long_position(self):
        """Function triggered when a long position is requested by the strategy

        TODO: Currently operates in test mode only, write real buy code

        """
        if self.config.test_mode:
            self.fake_buy()

    def enter_short_position(self):
        """Function triggered when a short position is requested by the strategy

        TODO: Currently operates in test mode only, write real sell code

        """
        if self.config.test_mode:
            self.fake_sell()




