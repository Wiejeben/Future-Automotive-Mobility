import socket
from threading import Thread
import time


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket()

    def connect(self):
        self.socket.connect((self.host, self.port))
        print('Successfully connected to', self.host + ':' + str(self.port))

    def threaded_listen(self, callback):
        while True:
            data = self.socket.recv(1024).decode()

            # Empty data means disconnect
            if not data:
                break

            calback(data)

    def send(self, message):
        self.socket.send(message.encode())


if __name__ == '__main__':
    client = Client('0.0.0.0', 5558)
    client.connect()

    def something(data):
        print(data)

    Thread(target=client.threaded_listen, args=s, daemon=True).start()

    time.sleep(.1)
    while True:
        client.send(input('->'))
