import sys
import websocket
import threading
import time

from binance import Client

from wenmoon.Config import Config
from wenmoon.Bot import Bot
from wenmoon.strategies.rsi_simple_strategy import Strategy

# Get configurations
config = Config()

# Log into the binance client API using the supplied api key and secret
binance_client = Client(
    config.api_key,
    config.secret_key
)

# Get symbol info
symbol_info = binance_client.get_symbol_info(config.watch_symbol_pair)

# Get the strategy to be used
# strategy = get_strategy(config.strategy)

strategy = Strategy(symbol_info)
# strategy.scout("1", "2")
# print(strategy)

# Initialise bot
bot = Bot(config, strategy, binance_client)

# Set up the url for the required websocket stream (URL is case-sensitive)
socket = f"wss://stream.binance.com:9443/ws/{config.watch_symbol_pair.lower()}@kline_{config.interval}"

# Disable full websocket logging
websocket.enableTrace(False)

def on_message(ws, message):
    """Called when the websocket receives a message.

    This function passes the message on to the Bot instance to handle.

    Args:
        ws: Websocket instance
        message (str): The decoded message received from the websocket
    """
    bot.handle_websocket_message(message)


def on_close(ws, close_status_code, close_msg):
    """Called when the websocket closes.

    This could be due to an error or keyboard interrupt.

    When the websocket connection closes, we attempt to reconnect to it here, and keep trying every 10 seconds.

    Args:
        ws: Websocket instnace
        close_status_code (str):
        close_msg (str):
    """
    print("Websocket closed")
    print(f"Closing with status code {close_status_code}")
    print("Retry : %s" % time.ctime())

    # Retry websocket reconnect every 10s
    time.sleep(10)
    connect_websocket()


def on_error(ws, error):
    """Called when the websocket encounters an error.

    This function simply logs the error.

    After an error, the websocket is automatically closed, and the on_close function is called.

    Args:
        ws: Websocket instnace
        error (str): Error message
    """
    print(f"ERROR: {error}")


def on_open(ws):
    """Called when the websocket is opened.

    This function calls the bot.start function which handles initialisation of candle data and strategy.

    Args:
        ws: Websocket instance
    """
    print("Starting bot")
    bot.start()


def connect_websocket():
    """Handles connection to the websocket.

    The socket url is defined outside this scope from the configuration file.

    This function initialises the websocket and specifies the callback functions for opening and closeing the websocket,
    along with message and error handling.

    The websocket is run on a thread.
    """
    print(f"Watching prices on {socket}")
    ws = websocket.WebSocketApp(
        socket,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    wst = threading.Thread(target=ws.run_forever())
    wst.daemon = True
    wst.start()


# main()
if __name__ == "__main__":
    try:
        connect_websocket()
    except Exception as err:
        print(err)
        print("Connect failed")




