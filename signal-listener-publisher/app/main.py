import asyncio
import orjson
import os
import logging

from client import SignalClient
from message_processor import SignalMessage, HandleAction
from publisher import KafkaPublisher as Producer
from config import TOPIC, KAFKA_BROKER, SIGNAL_CLI_REST_API_URL, BOT_PHONE_NUMBER

logging.basicConfig(level=logging.DEBUG)
logging.info("Starting signal-listener-publisher")
logging.info(f"Running in mode: {os.getenv('MODE', 'none')}")


class SignalListenerPublisher:
    """Handles listening to Signal messages and publishing to Kafka."""

    def __init__(self, signal_client: SignalClient, producer: Producer):
        self.signal_client = signal_client
        self.producer = producer

    async def process_signal_message(self, message: dict) -> None:
        """
        Processes an incoming Signal message.

        Routes, processes, and decides whether to respond via Signal or broker.
        """
        signal_message = SignalMessage.from_dict(message).route_message()

        if signal_message.handle_action == HandleAction.IGNORE:
            # logging.debug("Message ignored.")
            return

        if signal_message.handle_action == HandleAction.SEND_MESSAGE:
            logging.info("Sending response back to Signal.")
            await self.signal_client.send_text_message(
                signal_message.account,
                [signal_message.envelope["sourceNumber"]],
                signal_message.response_message,
            )
            return

        await self.publish_to_broker(signal_message)

    async def publish_to_broker(self, signal_message: SignalMessage) -> None:
        """
        Publishes a message to Kafka
        """
        if self.producer.error_cb_triggered:
            self.producer = Producer(KAFKA_BROKER, TOPIC)

        self.producer.publish(orjson.dumps(signal_message.brocker_message))
        
        if self.producer.error_cb_triggered:
            logging.error("Broker error during publishing. Sending error message to Signal.")
            await self.signal_client.send_text_message(
                signal_message.account,
                [signal_message.envelope["sourceNumber"]],
                "Server error. Please try again later.",
            )
    
    async def listen(self) -> None:
        """
        Listens for incoming messages from Signal.
        """
        async for message in self.signal_client.listen(BOT_PHONE_NUMBER):
            await self.process_signal_message(message)

    def close(self) -> None:
        """
        Closes the Kafka producer and any other resources.
        """
        if not self.producer.error_cb_triggered:
            self.producer.close()


def main():
    """
    Main entry point for the application.
    """
    signal_client = SignalClient(SIGNAL_CLI_REST_API_URL)
    producer = Producer(KAFKA_BROKER, TOPIC)
    app = SignalListenerPublisher(signal_client, producer)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(app.listen())
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    finally:
        app.close()
        loop.close()


if __name__ == "__main__":
    main()