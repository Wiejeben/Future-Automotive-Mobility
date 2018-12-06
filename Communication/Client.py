import socket
from threading import Thread
import time


class Client:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket()
        self.host = '0.0.0.0'

    def connect(self):
        self.socket.connect((self.host, self.port))
        print('Successfully connected to', self.host + ':' + str(self.port))

    def respond(self, message):
        self.socket.send(message.encode())


# if __name__ == '__main__':
#     client = Client(5558)
#     client.connect()

#     while True:
#         time.sleep(.1)
#         client.respond(input('->'))