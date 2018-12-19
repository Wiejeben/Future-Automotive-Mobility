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
        # print('Incoming message:', message)

        payload = message.split(' ')

        response = True
        if len(payload) >= 1:
            command = payload[0]
            del payload[0]

        if len(payload) >= 1:
            speed = int(payload[0]) or 0

        if command == SOCKET_JOY_FORWARD:
            self.controller.forward(speed)
        elif command == SOCKET_JOY_BACKWARD:
            self.controller.reverse(speed)
        elif command == SOCKET_JOY_NEUTRAL:
            self.controller.neutral()
        elif command == SOCKET_JOY_DIR_LEFT:
            self.controller.steer_left()
        elif command == SOCKET_JOY_DIR_RIGHT:
            self.controller.steer_right()
        elif command == SOCKET_JOY_DIR_NEUTRAL:
            self.controller.steer_neutral()


if __name__ == '__main__':
    vehicle = Vehicle()
    vehicle.listen()
