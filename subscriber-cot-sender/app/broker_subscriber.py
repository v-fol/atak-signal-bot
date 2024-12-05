import logging

from confluent_kafka import Consumer


logging.basicConfig(level=logging.INFO)


class BrokerSubscriber:
    """
    Handles subscribing to Kafka messages.
    """

    def __init__(self, broker: str, topic: str, group_id: str, auto_offset_reset: str):
        self.consumer = Consumer(
            {
                "bootstrap.servers": broker,
                "group.id": group_id,
                "auto.offset.reset": auto_offset_reset,
            }
        )
        self.topic = topic
        self.consumer.subscribe([topic])

    def listen(self):
        """
        Listens for incoming messages from Kafka and yields message values.
        """
        try:
            while True:
                messages = self.consumer.consume(num_messages=10, timeout=1.0)
                for msg in messages:
                    if msg.error():
                        logging.error(f"Error: {msg.error()}")
                    else:
                        yield msg.value().decode()
        finally:
            self.consumer.close()
