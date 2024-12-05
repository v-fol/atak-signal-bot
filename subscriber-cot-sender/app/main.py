import logging
import orjson
import asyncio

from broker_subscriber import BrokerSubscriber
from xml_transformer import XMLTransformer
from tcp_client import TCPClient
from http_client import SignalClient

from config import (
    KAFKA_BROKER,
    TOPIC,
    TCP_HOST,
    TCP_PORT,
    SIGNAL_CLI_REST_API_DOMAIN,
    SIGNAL_CLI_REST_API_PORT,
    BOT_PHONE_NUMBER,
    GROUP_ID,
    AUTO_OFFSET_RESET
)

logging.basicConfig(level=logging.DEBUG)


async def main():
    """
    Main function to run the subscriber.
    """
    subscriber = BrokerSubscriber(KAFKA_BROKER, TOPIC, GROUP_ID, AUTO_OFFSET_RESET)
    signal_client = SignalClient(
        f"{SIGNAL_CLI_REST_API_DOMAIN}:{SIGNAL_CLI_REST_API_PORT}"
    )

    for message in subscriber.listen():
        tcp_client = TCPClient(TCP_HOST, TCP_PORT)
        loaded_message = orjson.loads(message)

        xml_cot_message = XMLTransformer(loaded_message).generate_cot()
        try:
            tcp_client.send(xml_cot_message)
        finally:
            tcp_client.close()
        await signal_client.send_text_message(
            BOT_PHONE_NUMBER,
            [loaded_message["source_number"]],
            "CoT message sent successfully.",
        )
        logging.info("CoT message sent successfully.")


def run():
    """
    Run the subscriber.
    """
    try:
        asyncio.run(main())
    finally:
        logging.info("Shutting down...")


if __name__ == "__main__":
    run()
