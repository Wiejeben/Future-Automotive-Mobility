import settings
import os
import socket
import time
from threading import Thread


class SocketClient:
    def __init__(self):
        self.host = str(os.getenv('SOCKET_HOST', '0.0.0.0'))
        self.port = int(os.getenv('SOCKET_PORT'))
        self.socket = socket.socket()
        self.connected = False

    def connect(self):
        print('Trying to connect...')

        try:
            self.socket.connect((self.host, self.port))
        except socket.error:
            print('Failed to connect')
            return False

        self.connected = True
        print('Successfully connected to', self.host + ':' + str(self.port))

        Thread(target=self.isAlive, daemon=True).start()

        return True

    def isAlive(self):
        while True:
            try: 
                self.socket.send( bytes( "-", "UTF-8" ) )
                time.sleep(1) 
            except socket.error:
                print('Connection error!')
                self.connected = False
                retryConnection: bool = self.connect()
                if(not retryConnection):
                    time.sleep(5)
                    self.connect()
                break


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
