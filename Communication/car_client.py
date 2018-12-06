import socket
import sys
from Client import *

class CarClient(Client):
    def __init__(self, port):
        super().__init__(port)

a = CarClient(5558)
a.connect()
a.threaded_listen()
