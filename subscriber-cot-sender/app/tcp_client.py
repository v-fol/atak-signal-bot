import socket
import logging

logging.basicConfig(level=logging.DEBUG)


class TCPClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def send(self, message: str) -> str:
        """
        Send a message to the TCP server.
        """
        self.socket.sendall(message)
        return self.socket.recv(1024).decode()

    def close(self):
        """
        Close the TCP connection.
        """
        self.socket.close()
