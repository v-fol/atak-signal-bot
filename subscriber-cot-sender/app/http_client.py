import aiohttp


class SignalClient:
    """
    SignalClient class to interact with Signal REST API
    """

    def __init__(self, signal_cli_rest_api_url: str):
        self.signal_cli_rest_api_url = signal_cli_rest_api_url

    async def send_text_message(
        self, bot_phone_number: str, recipients: list[str], message: str
    ) -> dict:
        """
        Send a text message to a list of Signal recipients
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self.signal_cli_rest_api_url}/v2/send",
                json={
                    "message": message,
                    "number": bot_phone_number,
                    "recipients": recipients,
                },
            ) as resp:
                if resp.status == 404:
                    return {"error": "Not Found"}
                if resp.content_type == "application/json":
                    return await resp.json()
                return {"error": "Unexpected response"}
