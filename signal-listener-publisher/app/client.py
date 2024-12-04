import aiohttp
import asyncio
import orjson

from typing import AsyncGenerator

class SignalClient:
    def __init__(self, signal_cli_rest_api_domain: str):
        self.signal_cli_rest_api_domain = signal_cli_rest_api_domain

    async def listen(self, bot_phone_number: str) -> AsyncGenerator[dict, None]:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                f"http://{self.signal_cli_rest_api_domain}:8080/v1/receive/{bot_phone_number}"
            ) as ws:
                async for msg in ws:
                    yield orjson.loads(msg.data)

    #         curl -X POST -H "Content-Type: application/json" 'http://localhost:8080/v2/send' \
    #  -d '{"message": "Test", "number": "+380931124245", "recipients": [ "+380967455345" ]}'
    async def send_text_message(self, bot_phone_number: str, recipients: list[str], message: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self.signal_cli_rest_api_domain}:8080/v2/send",
                json={"message": message, "number": bot_phone_number, "recipients": recipients},
            ) as resp:
                if resp.status == 404:
                    return {"error": "Not Found"}
                if resp.content_type == 'application/json':
                    return await resp.json()
                return {"error": "Unexpected response"}