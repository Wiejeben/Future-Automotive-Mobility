import socket
import sys
from Client import *

class RecognitionClient(Client):
    def __init__(self, port):
        super().__init__(port)

a = RecognitionClient(5558)
a.connect()
   
while True:
    time.sleep(.1)
    a.respond(input('->'))
