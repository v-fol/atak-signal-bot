import pytest
from unittest.mock import MagicMock, patch, ANY
from app.publisher import KafkaPublisher


@pytest.fixture
def kafka_publisher():
    """
    Fixture to create a KafkaPublisher instance for testing.
    """
    bootstrap_servers = "localhost:9092"
    topic = "test-topic"
    with patch("app.publisher.Producer"):
        yield KafkaPublisher(bootstrap_servers, topic)


@patch("app.publisher.Producer")
def test_kafka_publisher_initialization(mock_producer):
    """
    Test that the KafkaPublisher initializes correctly.
    """
    bootstrap_servers = "localhost:9092"
    topic = "test-topic"

    publisher = KafkaPublisher(bootstrap_servers, topic)
    assert publisher.topic == topic
    assert not publisher.error_cb_triggered
    mock_producer.assert_called_once_with(
        {"bootstrap.servers": bootstrap_servers, "error_cb": publisher.error_cb}
    )


def test_publish_message_success(kafka_publisher):
    """
    Test that the publish method successfully sends a message.
    """
    kafka_publisher._producer.produce = MagicMock()

    kafka_publisher.publish("test-message")

    kafka_publisher._producer.produce.assert_called_once_with(
        kafka_publisher.topic, value="test-message", callback=ANY
    )
    kafka_publisher._producer.poll.assert_called_once_with(0)


def test_publish_message_failure(kafka_publisher, caplog):
    """
    Test that the publish method handles message delivery errors.
    """
    def mock_produce(topic, value, callback):
        callback(Exception("Delivery error"), None)

    kafka_publisher._producer.produce = mock_produce

    with caplog.at_level("ERROR"):
        kafka_publisher.publish("test-message")
        assert "Message delivery failed: Delivery error" in caplog.text


def test_error_callback(kafka_publisher):
    """
    Test the error callback behavior.
    """
    error = Exception("Test error")
    result = kafka_publisher.error_cb(error)
    assert result is True
    assert kafka_publisher.error_cb_triggered is True


def test_close_publisher(kafka_publisher):
    """
    Test that the close method flushes the producer.
    """
    kafka_publisher._producer.flush = MagicMock()

    kafka_publisher.close()

    kafka_publisher._producer.flush.assert_called_once()
