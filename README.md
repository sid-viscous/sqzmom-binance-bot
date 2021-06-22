# SQZMOM Bot (wenmoon)

A crypto trading bot based on Lazybear's squeeze momentum (SQZMOM) strategy.

It trades on the Binance exchange.

## Configuration

Make a copy of `settings.cfg.example` and call it `settings.cfg`. 

Go to binance and get your API key and secret key and put them into `settings.cfg` under `api_key` and `secret_key`.

## Running this bot

### In Python

In a terminal, navigate to the `bot` folder and run the command.

```shell
python -m wenmoon
```

Sometimes killing the bot is difficult, so closing the terminal session may be necessary. You can try using CTRL+C

### In Docker

In a terminal, navigate to the same directory level as `docker-compose.yml` and run the command:

```shell
docker-compose up --build
```

To stop the bot use CTRL+C in the terminal  where the bot is running, or the following command in another terminal:

```shell
docker stop sqzmom-bot_bot_1
```
