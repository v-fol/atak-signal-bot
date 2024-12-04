import pytest
from app.message_processor import SignalMessage, HandleAction  # Adjust the import according to your file structure

@pytest.fixture
def sample_data():
    """Fixture for sample Signal message data."""
    return {
        "account": "test_account",
        "envelope": {
            "timestamp": 1634048765,
            "sourceName": "Test User",
            "sourceNumber": "1234567890",
            "dataMessage": {
                "message": "Test message"
            }
        }
    }

@pytest.fixture
def signal_message(sample_data):
    """Fixture to create a SignalMessage object."""
    return SignalMessage.from_dict(sample_data)

def test_from_dict(signal_message, sample_data):
    """Test the from_dict method."""
    assert signal_message.account == sample_data["account"]
    assert signal_message.message == sample_data["envelope"]["dataMessage"]["message"]
    assert signal_message.source_name == sample_data["envelope"]["sourceName"]
    assert signal_message.source_number == sample_data["envelope"]["sourceNumber"]
    assert signal_message.timestamp == sample_data["envelope"]["timestamp"]
    assert signal_message.message_type == "TEXT_MESSAGE"
    assert signal_message.handle_action == HandleAction.IGNORE

def test_str(signal_message):
    """Test the __str__ method."""
    expected_str = "[TEXT_MESSAGE] Test User (1234567890): Test message"
    assert str(signal_message) == expected_str

def test_route_message_handle_text(signal_message):
    """Test route_message for text message."""
    signal_message.message = "/help"
    signal_message.route_message()  # Will invoke handle_text_message
    assert signal_message.handle_action == HandleAction.IGNORE

def test_route_message_handle_location(signal_message):
    """Test route_message for location message."""
    signal_message.message = "40.7128 74.0060 Test Place"
    signal_message.route_message()  # Will invoke handle_location_message
    assert signal_message.handle_action == HandleAction.SEND_TO_BROKER
    assert signal_message.brocker_message == '{"latitude":"40.7128","longitude":"74.0060","name":"Test Place","source_name":"Test User","source_number":"1234567890"}'

def test_route_message_handle_location_with_minus(signal_message):
    """Test route_message for location message."""
    signal_message.message = "40.7128 -74.0060 Test Place"
    signal_message.route_message()  # Will invoke handle_location_message
    assert signal_message.handle_action == HandleAction.SEND_TO_BROKER
    assert signal_message.brocker_message == '{"latitude":"40.7128","longitude":"-74.0060","name":"Test Place","source_name":"Test User","source_number":"1234567890"}'

def test_route_message_handle_standard_response(signal_message):
    """Test route_message for standard message."""
    signal_message.message = "Hello"
    signal_message.route_message()  # Will invoke send_standard_response
    assert signal_message.handle_action == HandleAction.SEND_MESSAGE
    assert signal_message.response_message == 'To use this bot, send your location in the format "latitude longitude name"'

def test_handle_unknown_message_type(signal_message):
    """Test handling of unknown message types."""
    signal_message.message_type = "UNKNOWN_TYPE"
    signal_message.route_message()
    assert signal_message.handle_action == HandleAction.IGNORE

