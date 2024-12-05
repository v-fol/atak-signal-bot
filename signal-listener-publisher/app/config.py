import os

TOPIC = os.getenv("TOPIC", "signal")
KAFKA_BROKER = f"{os.getenv('KAFKA_BROKER_DOMAIN', 'kafka')}:{os.getenv('KAFKA_BROKER_PORT', '9092')}"
SIGNAL_CLI_REST_API_URL = f"{os.getenv('SIGNAL_CLI_REST_API_DOMAIN', 'localhost')}:{os.getenv('SIGNAL_CLI_REST_API_PORT', '8080')}"
BOT_PHONE_NUMBER = os.getenv("BOT_PHONE_NUMBER", "")
SCRIPT_TO_RUN = os.getenv("SCRIPT_TO_RUN", "app/main.py")