import asyncio
import json
import os
import logging

from confluent_kafka import Producer

from client import SignalClient
from message_processor import SignalMessage, HandleAction

# Configuration
TOPIC = "signal"
SIGNAL_CLI_REST_API_DOMAIN = os.getenv("SIGNAL_CLI_REST_API_DOMAIN", "localhost")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

signal_client = SignalClient(SIGNAL_CLI_REST_API_DOMAIN)

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Starting signal-listener-publisher")
logger.info(f"Connecting to {os.getenv('MODE', 'none')}")

# Kafka producer setup
kafka_config = {'bootstrap.servers': KAFKA_BROKER}
producer = Producer(kafka_config)

def delivery_report(err, msg):
    """Callback for Kafka delivery reports."""
    if err:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

async def connect():
    """Connect to SignalClient and listen for messages."""
    async for message in signal_client.listen("+380931124245"):
        logger.debug(f"Received message: {message}")
        # await signal_client.send(message["account"], [message["envelope"]["source"], ],  "Message received")
        signal_message = SignalMessage.from_dict(message).route_message()

        if signal_message.handle_action == HandleAction.IGNORE:
            continue

        if signal_message.handle_action == HandleAction.SEND_MESSAGE:
            await signal_client.send_text_message(
                signal_message.account,
                [signal_message.envelope["sourceNumber"]],
                signal_message.response_message
            )
            continue

        try:
            producer.produce(
                TOPIC,
                value=signal_message.brocker_message.encode("utf-8"),
                callback=delivery_report
            )
            # Trigger Kafka delivery callbacks
            producer.poll(1)
            producer.flush()
            logger.info("Message sent to Kafka")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(connect())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        producer.flush()
