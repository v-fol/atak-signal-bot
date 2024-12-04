import aiohttp
import orjson

from typing import AsyncGenerator

class SignalClient:
    """
    SignalClient class to interact with Signal REST API
    """
    def __init__(self, signal_cli_rest_api_url: str):
        self.signal_cli_rest_api_url = signal_cli_rest_api_url

    async def listen(self, bot_phone_number: str) -> AsyncGenerator[dict, None]:
        """
        Listen for messages from the Signal REST API WebSocket
        """
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                f"http://{self.signal_cli_rest_api_url}/v1/receive/{bot_phone_number}"
            ) as ws:
                async for msg in ws:
                    yield orjson.loads(msg.data)

    async def send_text_message(self, bot_phone_number: str, recipients: list[str], message: str) -> dict:
        """
        Send a text message to a list of Signal recipients
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self.signal_cli_rest_api_url}/v2/send",
                json={"message": message, "number": bot_phone_number, "recipients": recipients},
            ) as resp:
                if resp.status == 404:
                    return {"error": "Not Found"}
                if resp.content_type == 'application/json':
                    return await resp.json()
                return {"error": "Unexpected response"}