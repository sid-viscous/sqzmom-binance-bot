import os
import csv

CSV_PATH = "trades.csv"

class Trader:
    """This class handles decision making from the strategy, and places buy/sell orders.

    Attributes:
        config (Config): Instance of the Config class - holds settings for the bot.
        strategy (Strategy): An instance of the strategy class for the chosen strategy.
        position (str): The current position for the strategy (options: "long", "short").
        coin_balance (float): The balance of coin currently trading.
        fiat_balance (float): The balance of fiat currency currently trading.
        candles (list of dict): Candle data (candles[0] is the oldest, candles[-1] is the newest).
        newest_buy_price (float): The buy price from the most recent buy.
        current_trade_profit (float): The profit from the most recent buy (expressed as a percentage).
        buy_count (int): Running count of the number of buy trades made.
        sell_count (int): Running count of the number of sell trades made.
    """
    def __init__(self, config, strategy):
        """Initialise the trader.

        Args:
            config (Config): Instance of the Config class - holds settings for the bot.
            strategy (Strategy): An instance of the strategy class for the chosen strategy.
        """
        self.config = config
        self.strategy = strategy
        self.position = config.start_position
        self.coin_balance = 0
        self.fiat_balance = 0
        self.set_initial_balance()
        self.candles = None
        self.newest_buy_price = 0.0
        self.current_trade_profit = 0.0
        self.buy_count = 0
        self.sell_count = 0

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

    @staticmethod
    def write_csv_row(row):
        file_exists = os.path.isfile(CSV_PATH)

        with open(CSV_PATH, 'a') as csvfile:
            headers = row.keys()
            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)

            if not file_exists:
                writer.writeheader()  # file doesn't exist yet, write a header

            writer.writerow(row)

    def output_status(self):
        """Outputs details about the current status of the bot.

        Includes information such as current position and profit from most recent buy.
        """

        # Get newest candle data
        open_price = self.candles[-1]["open_price"]
        high_price = self.candles[-1]["high_price"]
        low_price = self.candles[-1]["low_price"]
        close_price = self.candles[-1]["close_price"]
        volume = self.candles[-1]["volume"]

        # Calculate the fiat value of the coin balance
        fiat_value = self.coin_balance * close_price

        # Calculate the coin value of the fiat balance
        coin_value = self.fiat_balance / close_price

        # Prepare strings for balance output
        balance_string_coin = f"{self.coin_balance:,.4e} {self.config.coin_symbol} ({fiat_value:,.4e} {self.config.fiat_symbol})"
        balance_string_fiat = f"{self.fiat_balance:,.4e} {self.config.fiat_symbol} ({coin_value:,.4e} {self.config.coin_symbol})"

        print("#"*72)
        print(" BOT STATUS ".center(72))
        print(" Newest candle ".center(72, "-"))
        print(" {:<17} {:<17} {:<17} {:<17}".format("Open", "High", "Low", "Close"))
        print(" {:<17} {:<17} {:<17} {:<17}".format(open_price, high_price, low_price, close_price))
        print(" {:<17}".format("Volume"))
        print(" {:<17}".format(volume))
        print(" Current position ".center(72, "-"))
        print(" {:<35} {:<35}".format("Coin balance", "Fiat balance"))
        print(" {:<35} {:<35}".format(balance_string_coin, balance_string_fiat))
        print(" History ".center(72, "-"))
        print(" {:<35} {:<35}".format("Buy count", "Sell count"))
        print(" {:<35} {:<35}".format(self.buy_count, self.sell_count))
        print("#"*72)

        # JSONify results
        status_json = {
            "time": self.candles[-1]["candle_close_time"],
            "fiat_balance": self.fiat_balance,
            "coin_balance": self.coin_balance,
            "fiat_value": fiat_value,
            "coin_value": coin_value
        }

        # Print results to csv
        self.write_csv_row(status_json)

    def fake_buy(self):
        """Simulates a buy order.

        Takes into account the current price and modifies the balances on the Bot instance.

        """
        # Get current price
        price = self.candles[-1]["close_price"]

        # Calculate coin buy quantity with current funds
        coin_buy_quantity = self.fiat_balance / price

        # Subtract trading fee
        coin_buy_quantity *= 1 - self.config.test_fee / 100

        # Make the fake purchase
        self.fiat_balance = 0
        self.coin_balance = coin_buy_quantity
        self.buy_count += 1

        # Output message
        print(f"Bought {coin_buy_quantity} {self.config.coin_symbol} at price of {price} {self.config.fiat_symbol}")

        # Store the most recent buy price
        self.newest_buy_price = price

    def fake_sell(self):
        """Simulates a sell order.

        Takes into account the current price and modifies the balances on the Bot instance.

        """
        # Get current price
        price = self.candles[-1]["close_price"]

        # Calculate fiat buy quantity with current funds
        fiat_buy_quantity = price * self.coin_balance

        # Subtract trading fee
        fiat_buy_quantity *= 1 - self.config.test_fee / 100

        # Make the fake sell
        self.coin_balance = 0
        self.fiat_balance = fiat_buy_quantity
        self.sell_count += 1

        # Output message
        print(f"Sold {self.config.coin_symbol} at price of {price} {self.config.fiat_symbol} for {fiat_buy_quantity}"
              f" {self.config.fiat_symbol}")

    def buy(self):
        """Function triggered when a long position is requested by the strategy

        TODO: Currently operates in test mode only, write real buy code

        """
        if self.config.test_mode:
            self.fake_buy()
        else:
            pass

    def sell(self):
        """Function triggered when a short position is requested by the strategy

        TODO: Currently operates in test mode only, write real sell code

        """
        if self.config.test_mode:
            self.fake_sell()
        else:
            pass

    def set_position(self, candles):
        """Main decision function for signalling.

        This function is called when a new candle comes in from the Bot class.

        It submits the candle data to the chosen strategy

        Args:
            candles (list of dict): The most recent list of closed historic candles.

        """
        # Set the candles as a class variable so other methods can access it
        self.candles = candles

        # Log the newest candle prices
        nc = candles[-1]
        newest_price = nc["close_price"]

        # If long, set the current profit from this trade
        if self.position == "long":
            self.current_trade_profit = 100 * (1 - self.config.test_fee) * (newest_price - self.newest_buy_price)\
                                        / self.newest_buy_price
        else:
            self.current_trade_profit = 0.0

        # Query the strategy for the current recommended position
        print("Scouting for trades")
        recommended_action = self.strategy.scout(candles)
        print(f"Recommended action: {recommended_action}")

        # Check for exits
        if self.position == "long":
            if recommended_action == "sell":
                # If strategy recommends an exit then sell
                print("Strategy sell indicator triggered - selling")
                self.position = "short"
                self.sell()
            elif self.config.profit_target and self.current_trade_profit >= self.config.profit_target:
                # If a profit target has been set and has been exceeded then sell
                print("Profit target reached - selling")
                recommended_action = "sell"
                self.position = "short"
                self.sell()
            elif self.config.stop_loss and self.current_trade_profit <= self.config.stop_loss:
                # If a stop los has been set and has been exceeded then sell
                print("Stop loss reached - selling")
                recommended_action = "sell"
                self.position = "short"
                self.sell()

        # Check for entries
        if self.position == "short":
            if recommended_action == "buy":
                # if the strategy position changes to long, handle the move to long position
                print("Going long")
                self.position = "long"
                self.buy()

        # Log current balances
        self.output_status()
