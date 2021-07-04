class Trader:
    def __init__(self, config, strategy):
        """Initialise the trader.

        This class handles decision making from the strategy, and places buy/sell orders

        Args:
            config (Config): An instance of the configuration class, which should already be initialised.
            strategy (Strategy): An instance of the strategy class for the chosen strategy.
            position (str): The current position for the strategy (options: "long", "short").
            coin_balance (float): The balance of coin currently trading.
            fiat_balance (float): The balance of fiat currency currently trading.
            candles (list of dict): Candle data.
        """
        self.config = config
        self.strategy = strategy
        self.position = config.start_position
        self.coin_balance = 0
        self.fiat_balance = 0
        self.set_initial_balance()
        self.candles = None

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

        Outputs fiat value of coin balance when in long position.
        """

        # Calculate the fiat value of the coin balance
        fiat_value = self.coin_balance*self.candles[-1]["close_price"]

        # Calculate the coin value of the fiat balance
        coin_value = self.fiat_balance/self.candles[-1]["close_price"]

        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(f"Coin balance: {self.coin_balance} {self.config.coin_symbol} ({fiat_value} {self.config.fiat_symbol})")
        print(f"Fiat balance: {self.fiat_balance} {self.config.fiat_symbol} ({coin_value} {self.config.coin_symbol})")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    def fake_buy(self):
        """Simulates a buy order.

        Takes into account the current price and modifies the balances on the Bot instance.

        """
        # Get current price
        price = self.candles[-1]["close_price"]

        # Calculate coin buy quantity with current funds
        coin_buy_quantity = self.fiat_balance/price

        # Subtract trading fee
        coin_buy_quantity *= 1 - self.config.test_fee/100

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
        price = self.candles[-1]["close_price"]

        # Calculate fiat buy quantity with current funds
        fiat_buy_quantity = price*self.coin_balance

        # Subtract trading fee
        fiat_buy_quantity *= 1 - self.config.test_fee / 100

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

    def handle_new_kline(self, candles):
        """Main decision function for signalling.

        This function is called when a new candle comes in from the Bot class.

        It submits the candle data to the chosen strategy

        Args:
            candles (list of dict): The most recent list of closed historic candles.

        """
        # Set the candles as a class variable so other methods can access it
        self.candles = candles

        # Log current position
        print("-----------------------------------------------------------------------------------------------")
        print(f"Checking strategy for position - current position: {self.position}")

        # Query the strategy for the current recommended position
        recommended_position = self.strategy.scout(candles)

        # Check if position has changed
        if recommended_position != self.position:
            if recommended_position == "long":
                # if the strategy position changes to long, handle the move to long position
                print("Going long")
                self.position = "long"
                self.enter_long_position()
            elif recommended_position == "short":
                # if the strategy position changes to short, handle the move to short position
                print("Going short")
                self.position = "short"
                self.enter_short_position()
            else:
                # In the almost impossible scenario where the indicator ends on a neutral position, do nothing
                print(f"recommended position neutral, stay in current position: {self.position}")

        # Log current balances
        self.output_balances()
