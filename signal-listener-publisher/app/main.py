import asyncio
import json
import websockets
import os
import logging

from pprint import pprint as pp


SIGNAL_CLI_REST_API_DOMAIN = os.getenv("SIGNAL_CLI_REST_API_DOMAIN", "localhost")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("ping from signal-listener-publisher")


async def connect():
    async with websockets.connect(
        f"ws://{SIGNAL_CLI_REST_API_DOMAIN}:8080/v1/receive/+380931124245",
        ping_interval=None,
    ) as websocket:
        print("Connected to WebSocket. Listening for messages...")
        async for message in websocket:
            pp(json.loads(message))

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect())
    loop.run_forever()
