import datetime
import uuid
from xml.etree import ElementTree as ET
from typing import Union, Dict

W3C_XML_DATETIME = "%Y-%m-%dT%H:%M:%S.%fZ"  # W3C XML Schema dateTime format
MARKER_TYPE = "a-h-A-M-A"  # Type of marker
TIME_BEFORE_STALE = 60  # Time (in seconds) before the event becomes stale
DEFAULT_HAE = "0"
DEFAULT_CE = "10"
DEFAULT_LE = "10"


class XMLTransformer:
    def __init__(self, broker_message: Dict[str, Union[str, float]]):
        self.broker_message = broker_message

    def generate_cot(self) -> bytes:
        """
        Generate a Cursor on Target (CoT) Event in XML format.

        Returns:
            bytes: The CoT event as an XML byte string.
        """
        # Create the root element
        root = ET.Element(
            "event",
            attrib={
                "version": "2.0",
                "type": MARKER_TYPE,
                "uid": uuid.uuid4().hex,
                "how": "m-g",
                "time": self.cot_time(),
                "start": self.cot_time(),
                "stale": self.cot_time(TIME_BEFORE_STALE),
            },
        )

        detail = ET.SubElement(root, "detail")
        ET.SubElement(
            detail,
            "contact",
            attrib={"callsign": self.broker_message.get("name", "Unknown")},
        )

        ET.SubElement(root, "point", attrib=self._get_point_attributes())

        return ET.tostring(root)

    def cot_time(self, offset_seconds: Union[int, None] = None) -> str:
        """
        Get the current UTC datetime as a W3C XML Schema dateTime string.

        Args:
            offset_seconds (int, optional): Number of seconds to offset the current time. Defaults to None.

        Returns:
            str: The datetime string in W3C XML format.
        """
        time = datetime.datetime.now(datetime.timezone.utc)
        if offset_seconds:
            time += datetime.timedelta(seconds=offset_seconds)
        return time.strftime(W3C_XML_DATETIME)

    def _get_point_attributes(self) -> Dict[str, str]:
        """
        Create attributes for the <point> element.

        Returns:
            dict: Attributes for the <point> element.
        """
        return {
            "lat": self.broker_message["latitude"],
            "lon": self.broker_message["longitude"],
            "hae": DEFAULT_HAE,
            "ce": DEFAULT_CE,
            "le": DEFAULT_LE,
        }
