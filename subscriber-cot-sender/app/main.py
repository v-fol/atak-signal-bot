
import logging
import os
from confluent_kafka import Consumer


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

config = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'python-consumer-group',
    'auto.offset.reset': 'earliest'
}

logger.info("Starting consumer...")
consumer = Consumer(config)
consumer.subscribe(['signal'])


try:
    while True:
        msg = consumer.poll(1.0)  # Poll messages with a 1-second timeout
        # logger.debug("Polling messages...")
        if msg is None:
            continue
        if msg.error():
            logger.info(f"Consumer error: {msg.error()}")
            continue

        logger.info(f"Received message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    logger.info("Stopping consumer...")
finally:
    consumer.close()
