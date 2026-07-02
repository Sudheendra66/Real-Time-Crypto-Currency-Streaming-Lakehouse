import sys
from pathlib import Path
import json
import websocket

# Add producer/src and producer/ to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # producer/src
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # producer

from schemas.market_event import MarketEvent
from eventhub.producer import EventHubPublisher
from config.settings import (
    EVENT_HUB_CONNECTION_STRING,
    EVENT_HUB_NAME
)


# Create Event Hub publisher
publisher = EventHubPublisher(
    EVENT_HUB_CONNECTION_STRING,
    EVENT_HUB_NAME
)


def on_message(ws, message):
    try:
        # Parse Binance event
        raw_event = json.loads(message)

        # Convert to enterprise schema
        market_event = MarketEvent.from_binance(raw_event)

        # Convert object to dictionary
        event = market_event.to_dict()

        # Send to Event Hub
        publisher.publish(event)

        # Print for monitoring
        print(
            f"{event['symbol']} | "
            f"Price: {event['trade_price']} | "
            f"Qty: {event['trade_quantity']}"
        )

    except Exception as e:
        print(f"ERROR: {e}")


def on_error(ws, error):
    print(f"WebSocket Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("Connection closed")


def on_open(ws):
    print("Connected to Binance")


socket = (
    "wss://stream.binance.com:9443/stream?"
    "streams="
    "btcusdt@trade/"
    "ethusdt@trade/"
    "solusdt@trade/"
    "bnbusdt@trade/"
    "xrpusdt@trade"
)


ws = websocket.WebSocketApp(
    socket,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)


ws.run_forever()