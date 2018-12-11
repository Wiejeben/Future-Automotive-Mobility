import settings
import os
import socket


class SocketClient:
    def __init__(self):
        self.host = str(os.getenv('SOCKET_HOST', '0.0.0.0'))
        self.port = int(os.getenv('SOCKET_PORT'))
        self.socket = socket.socket()

    def connect(self):
        self.socket.connect((self.host, self.port))
        print('Successfully connected to', self.host + ':' + str(self.port))

    def disconnect(self):
        pass

    def listen(self, callback):
        print('Started listening to', self.host + ':' + str(self.port))
        while True:
            message = self.socket.recv(1024).decode()

            # Empty message means disconnect
            if not message:
                print('Server disconnected')
                break

            callback(message)

    def send(self, message: str):
        self.socket.send(message.encode())


if __name__ == '__main__':
    client = SocketClient()
    client.connect()
    client.listen(print)
