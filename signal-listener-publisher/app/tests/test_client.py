import pytest
from aioresponses import aioresponses
from app.client import SignalClient


@pytest.fixture
def mock_signal_client():
    """Fixture to create an instance of SignalClient."""
    return SignalClient(signal_cli_rest_api_url="mock-signal-api")


@pytest.mark.asyncio
async def test_send_text_message_success(mock_signal_client):
    """Test sending a text message successfully."""
    with aioresponses() as m:
        # Mock the Signal API response
        m.post("http://mock-signal-api/v2/send", payload={"status": "sent"})

        response = await mock_signal_client.send_text_message(
            bot_phone_number="123456789",
            recipients=["987654321"],
            message="Hello, Signal!",
        )

        assert response == {"status": "sent"}


@pytest.mark.asyncio
async def test_send_text_message_not_found(mock_signal_client):
    """Test sending a text message with 404 response."""
    with aioresponses() as m:
        # Mock the Signal API 404 response
        m.post("http://mock-signal-api/v2/send", status=404)

        response = await mock_signal_client.send_text_message(
            bot_phone_number="123456789",
            recipients=["987654321"],
            message="Hello, Signal!",
        )

        assert response == {"error": "Not Found"}
