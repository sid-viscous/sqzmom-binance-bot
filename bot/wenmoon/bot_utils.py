from datetime import datetime, timezone, timedelta


def format_websocket_result(msg):
    """Rewrites the message from the websocket into a more readable format.

    See the following link for the data structure returned from the websocket:
    https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#klinecandlestick-streams

    Args:
        msg (dict): The raw message from the websocket.

    Returns:
        dict: Human readable dictionary for the kline data.

    """
    return {
        "event_type": msg["e"],
        "event_time_ms": msg["E"],
        "event_time": str(datetime.fromtimestamp(msg["E"]/1000, tz=timezone.utc)),
        "symbol": msg["s"],
        "candle_start_time": msg["k"]["t"],
        "candle_close_time": msg["k"]["T"],
        "interval": msg["k"]["i"],
        "first_trade_id": msg["k"]["f"],
        "last_trade_id": msg["k"]["L"],
        "open_price": float(msg["k"]["o"]),
        "close_price": float(msg["k"]["c"]),
        "high_price": float(msg["k"]["h"]),
        "low_price": float(msg["k"]["l"]),
        "volume": msg["k"]["v"],
        "number_of_trades": int(msg["k"]["n"]),
        "is_candle_closed": msg["k"]["x"],
        "quote_asset_volume": float(msg["k"]["q"]),
        "taker_buy_base_asset_volume": float(msg["k"]["V"]),
        "taker_buy_quote_asset_volume": float(msg["k"]["Q"])
    }


def format_historical_candle(candle):
    """Rewrites a candle into a more readable format.

    The documentation for the returned kline data at this endpoint (/api/v3/klines) can be found at the following link:
    https://github.com/binance/binance-public-data/#klines

    Args:
        kline (list of str): Raw kline data.

    Returns:
        dict: Human readable kline data.
    """
    return {
        "candle_start_time_ms": int(candle[0]),
        "candle_start_time": str(datetime.fromtimestamp(int(candle[0])/1000, tz=timezone.utc)),
        "open_price": float(candle[1]),
        "high_price": float(candle[2]),
        "low_price": float(candle[3]),
        "close_price": float(candle[4]),
        "volume": float(candle[5]),
        "candle_close_time_ms": int(candle[6]),
        "candle_close_time": str(datetime.fromtimestamp(int(candle[6])/1000, tz=timezone.utc)),
        "quote_asset_volume": float(candle[7]),
        "number_of_trades": int(candle[8]),
        "taker_buy_base_asset_volume": float(candle[9]),
        "taker_buy_quote_asset_volume": float(candle[10])
    }


def format_historical_candles(msg):
    """Rewrites a list of klines into a more readable format.

    Args:
        msg (list of list of str):  Historical klines for the required period.

    Returns:
        list of dict: Historical klines for the required period, with more verbose keys.
    """
    result = []
    for candle in msg:
        # By default, the binance api returns candles that are still in progress, even if calling 1ms after next epoch
        # Check close time is not in the future
        formatted_candle = format_historical_candle(candle)
        close = datetime.fromtimestamp(formatted_candle["candle_close_time_ms"]/1000, tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        if close < now:
            result.append(formatted_candle)
    return result


def calculate_start_date(time_span, time_unit):
    """Calculates the start time in ms from now minus an interval.

    Args:
        time_span (int): The number of time units to go back.
        time_unit (str): Unit of time in minutes or hours (options: "m", "h").

    Returns:
        datetime: Start time to retrieve candle data for.
    """
    if time_unit == "m":
        return datetime.utcnow() - timedelta(minutes=time_span)
    elif time_unit == "h":
        return datetime.utcnow() - timedelta(hours=time_span)
