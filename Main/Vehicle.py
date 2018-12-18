from lib.SocketClient import SocketClient
from lib.constants import *

try:
    from lib.GPIOController import GPIOController as Controller
except ModuleNotFoundError:
    print('RPi.GPIO not found, falling back to faker.')
    from lib.FakeController import FakeController as Controller


class Vehicle:
    def __init__(self):
        self.controller = Controller()
        self.client = SocketClient(SOCKET_ID_VEHICLE)

    def listen(self):
        self.client.connect()
        self.client.listen(self.on_message)

    def on_message(self, message: str):
        print('Incoming message:', message)

        if message == '100% POWER':
            self.controller.forward(100)

        if message == '60% POWER':
            self.controller.forward(60)

        if message == '30% POWER':
            self.controller.forward(30)

        if message == 'backward':
            self.controller.reverse(100)

        if message == 'brake' or message == 'stop' or message == 'neutral':
            self.controller.neutral()


if __name__ == '__main__':
    vehicle = Vehicle()
    vehicle.listen()
