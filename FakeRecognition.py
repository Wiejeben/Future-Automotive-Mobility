from threading import Thread

from lib.SocketClient import SocketClient
from lib.constants import *


class FakeRecognition:
    def __init__(self):
        self.client = SocketClient(SOCKET_ID_RECOGNITION)

    def connect(self):
        self.client.connect()

    def input(self):
        print('Enter a command: 1 = busy, 0 = free')

        message = input()

        if message == '1':
            self.client.send(SOCKET_RECOGNITION_DETECTED)

        if message == '0':
            self.client.send(SOCKET_RECOGNITION_FREE)


if __name__ == '__main__':
    recognition = FakeRecognition()
    recognition.connect()

    Thread(target=recognition.client.listen, args=(print,), daemon=True).start()

    while True:
        try:
            recognition.input()
        except KeyboardInterrupt:
            break
