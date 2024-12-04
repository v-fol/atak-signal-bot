import orjson
import re

from enum import Enum
from dataclasses import dataclass


class HandleAction(Enum):
    SEND_TO_BROKER = "SEND_TO_BROKER"
    SEND_MESSAGE = "SEND_MESSAGE"
    IGNORE = "IGNORE"


@dataclass
class SignalMessage:
    """
    Respreentation of a Signal message
    """

    account: str
    message: str
    timestamp: int
    source_name: str
    source_number: str
    message_type: str
    envelope: dict
    brocker_message: str = ""
    response_message: str = ""
    handle_action: HandleAction = HandleAction.IGNORE

    @classmethod
    def from_dict(cls, data: dict) -> "SignalMessage":
        """
        Create a SignalMessage object from a dictionary
        """
        envelope = data["envelope"]
        message = envelope.get("dataMessage", {}).get("message", "")
        message_type = "TEXT_MESSAGE" if "dataMessage" in envelope else "UNKNOWN_TYPE"
        return cls(
            message=message,
            account=data["account"],
            timestamp=envelope["timestamp"],
            source_name=envelope["sourceName"],
            source_number=envelope["sourceNumber"],
            message_type=message_type,
            envelope=envelope,
        )

    def __str__(self):
        if self.message_type == "TEXT_MESSAGE":
            return f"[{self.message_type}] {self.source_name} ({self.source_number}): {self.message}"
        else:
            return f"[{self.message_type}] {self.source_name} ({self.source_number}): {self.envelope}"

    def route_message(self) -> "SignalMessage":
        if self.message_type == "TEXT_MESSAGE":
            self.handle_text_message()
        else:
            self.handle_unknown_message_type()
        return self

    def handle_text_message(self):
        if self.message.startswith("/"):
            self.route_command()
        elif match := re.match(r"(^\d+\.\d+) (\d+\.\d+)\s*(.+)$", self.message):
            self.handle_location_message(match)
        else:
            self.send_standard_response()

    def route_command(self):
        command = self.message.split(" ")[0][1:]
        command_handlers = {
            "help": self.handle_help_command,
            "ping": self.handle_ping_command,
        }
        handler = command_handlers.get(command, self.handle_unknown_command)
        handler()

    def handle_ping_command(self):
        pass

    def handle_help_command(self):
        pass

    def handle_unknown_command(self):
        pass

    def handle_location_message(self, match) -> None:
        self.brocker_message = orjson.dumps(
            {
                "latitude": match.group(1),
                "longitude": match.group(2),
                "name": match.group(3),
                "source_name": self.source_name,
                "source_number": self.source_number,
            }
        ).decode()
        self.handle_action = HandleAction.SEND_TO_BROKER

    def send_standard_response(self) -> None:
        self.response_message = 'To use this bot, send your location in the format "latitude longitude name"'
        self.handle_action = HandleAction.SEND_MESSAGE

    def handle_unknown_message_type(self):
        self.handle_action = HandleAction.IGNORE
