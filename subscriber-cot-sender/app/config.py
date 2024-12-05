import os


SCRIPT_TO_RUN = os.getenv("SCRIPT_TO_RUN", "app/main.py")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = os.getenv("TOPIC", "signal")
TCP_HOST = os.getenv("TCP_HOST", "tak-server")
TCP_PORT = os.getenv("TCP_PORT", 8087)
SIGNAL_CLI_REST_API_DOMAIN = os.getenv("SIGNAL_CLI_REST_API_DOMAIN", "localhost")
SIGNAL_CLI_REST_API_PORT = os.getenv("SIGNAL_CLI_REST_API_PORT", 8080)
BOT_PHONE_NUMBER = os.getenv("BOT_PHONE_NUMBER", "")
GROUP_ID = os.getenv("GROUP_ID", "python")
AUTO_OFFSET_RESET = os.getenv("AUTO_OFFSET_RESET", "earliest")