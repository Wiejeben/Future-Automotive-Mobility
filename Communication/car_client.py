import socket
import sys
from Client import *

class CarClient(Client):
    def __init__(self, port):
        super().__init__(port)
    
    def threaded_listen(self):
        while True:
            data = self.socket.recv(1024).decode()
            # Empty data means disconnect
            if not data:
                break

            print(data)

a = CarClient(5558)
a.connect()
a.threaded_listen()

