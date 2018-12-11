from SocketClient import SocketClient

try:
    from GPIOController import GPIOController as Controller
except ModuleNotFoundError:
    from FakeController import FakeController as Controller


class Vehicle:
    def __init__(self):
        self.controller = Controller()
        self.client = SocketClient()

    def listen(self):
        self.client.connect()
        self.client.listen(self.on_message)

    def on_message(self, message: str):
        print('Incoming message:', message)

        if message == 'forward':
            self.controller.forward(100)

        if message == 'reverse':
            self.controller.reverse(100)

        if message == 'brake' or message == 'stop' or message == 'neutral':
            self.controller.neutral()


if __name__ == '__main__':
    vehicle = Vehicle()
    vehicle.listen()
