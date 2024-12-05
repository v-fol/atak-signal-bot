import logging
from abc import ABC, abstractmethod
import orjson

from confluent_kafka import Producer

logging.basicConfig(level=logging.DEBUG)


class Publisher(ABC):
    """
    Abstract base class for a message publisher.
    """
    @abstractmethod
    def publish(self, message: str) -> None:
        """
        Publish a message 
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the publisher to release resources.
        """
        pass


class KafkaPublisher(Publisher):
    """
    Kafka-specific implementation of the Publisher.
    """
    def __init__(self, bootstrap_servers: str, topic: str):
        self.error_cb_triggered = False
        self._producer = Producer({"bootstrap.servers": bootstrap_servers, "error_cb": self.error_cb})
        self.topic = topic
        logging.info("KafkaPublisher initialized with bootstrap servers: %s", bootstrap_servers)

    def error_cb(self, err) -> bool:
        """
        Error callback for the Kafka producer.
        """
        logging.error("Kafka error: %s", err)
        self.error_cb_triggered = True
        return True


    def publish(self, message: bytes) -> None:
        """
        Publish a message to a Kafka topic.
        """

        def delivery_report(err, msg):
            if err:
                logging.error("Message delivery failed: %s", err)
            else:
                logging.info("Message delivered to %s [%s]", msg.topic(), msg.partition())

        logging.debug("Publishing message to kafka")
        self._producer.produce(self.topic, value=message, callback=delivery_report)
        self._producer.poll(0)

    def close(self) -> None:
        """
        Flush any remaining messages and close the producer.
        """
        logging.info("Closing KafkaPublisher...")
        self._producer.flush()
