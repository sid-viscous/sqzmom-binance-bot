import os
import re
import configparser
from datetime import datetime

CONFIG_FILE = "wenmoon/settings.cfg"
CONFIG_SECTION = "binance_user_config"

class Config:
    def __init__(self):
        # Initialise config parser
        config = configparser.ConfigParser()

        # Set default configuration
        config["DEFAULT"] = {
            "coin_symbol": "BTC",
            "fiat_symbol": "USDT",
            "watch_pair_symbol": "BTCUSDT",
            "interval": "1h",
            "start_position": "fiat",
            "max_candles": 50,
            "test_mode": "yes",
            "strategy": "wenmoon"
        }

        # Open configuration file
        if not os.path.exists(CONFIG_FILE):
            print("Configuration file not found, should be in wenmoon/settings.cfg")
            raise FileNotFoundError
        else:
            config.read(CONFIG_FILE)

        # Set configuration attributes
        self.api_key = config.get(CONFIG_SECTION, "api_key")
        self.secret_key = config.get(CONFIG_SECTION, "secret_key")
        self.coin_symbol = config.get(CONFIG_SECTION, "coin_symbol")
        self.fiat_symbol = config.get(CONFIG_SECTION, "fiat_symbol")
        self.watch_symbol_pair = config.get(CONFIG_SECTION, "watch_pair_symbol")
        self.interval = self._validate_interval(config.get(CONFIG_SECTION, "interval"))
        self.interval_number = int(re.search(r"\d+", self.interval)[0])
        self.interval_unit = re.search(r"\D+", self.interval)[0]
        self.start_position = config.get(CONFIG_SECTION, "start_position")
        self.start_balance = config.getfloat(CONFIG_SECTION, "start_balance")
        self.max_candles = config.getint(CONFIG_SECTION, "max_candles")
        self.test_mode = config.getboolean(CONFIG_SECTION, "test_mode")
        self.strategy = config.get(CONFIG_SECTION, "strategy")
        self.output_klines = False
        self.output_websocket = False

    @staticmethod
    def _validate_interval(interval):
        valid_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h"]
        if interval in valid_intervals:
            return interval
        else:
            raise ValueError(f"Supplied interval is invalid, required one of {valid_intervals}")


