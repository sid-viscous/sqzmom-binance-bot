import time
import sys
import signal
import threading
from wenmoon.Config import Config
from wenmoon.Bot import Bot
from wenmoon.strategies import get_strategy




def main():
    # Get configurations
    config = Config()

    # Get the strategy to be used
    strategy = get_strategy(config.strategy)

    # Initialise bot
    bot = Bot(config, strategy)

    # Log in to client with api credentials
    bot.login()

    # Get historical klines
    bot.get_historical_klines()

    # Start the websocket and hence, trading
    bot.start_kline_websocket()





    # Loop forever
    while True:
        #pass
        # The following can be used for some interactivity when running from python, not docker
        selection = input("Your selection? (h for help) ")  # python 3.x, for 2.x use raw_input

        if len(selection) > 1:
            print('Enter one character only.')
        elif selection == 'h':
            print('Choose only one character option from available list:')
            print('\n\t h : help')
            print('\n\t w : start/stop printing websocket output')
            print('\n\t c : start/stop printing candle history output')
            print('\n\t e : exit')
        elif selection == 'e':
            print('Exiting the program and stopping all processes.')
            bot.stop_kline_websocket()
            sys.exit('Finished and exiting.')
        elif selection == 'w':
            if config.output_klines:
                config.output_klines = False
            else:
                config.output_klines = True
        elif selection == 'c':
            if config.output_klines:
                config.output_candles = False
            else:
                config.output_candles = True
        else:
            print('Unknown option.')

