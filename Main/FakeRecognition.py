from SocketClient import SocketClient


class FakeRecognition:
    def __init__(self):
        self.client = SocketClient()

    def connect(self):
        self.client.connect()

    def input(self):
        print('Enter a command: 1 = busy, 0 = free')

        message = input()

        if message != '1' and message != '0':
            return

        self.client.send(message)


if __name__ == '__main__':
    recognition = FakeRecognition()
    recognition.connect()

    while True:
        recognition.input()
