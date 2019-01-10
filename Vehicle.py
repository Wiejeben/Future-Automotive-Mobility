from threading import Thread

from lib.SocketClient import SocketClient
from lib.constants import *
import time

try:
    from lib.GPIOController import GPIOController as Controller
except ModuleNotFoundError:
    print('RPi.GPIO not found, falling back to faker.')
    from lib.FakeController import FakeController as Controller


class Vehicle:
    def __init__(self):
        self.controller = Controller()
        self.client = SocketClient(SOCKET_ID_VEHICLE)
        self.last_message = time.time()

    def listen(self):
        self.client.connect()

        # Start thread to watch for timeouts
        Thread(target=self.timeout_watcher, daemon=True).start()

        self.client.listen(self.on_message)

    def timeout_watcher(self):
        """Puts vehicle in neutral if no message was received in the last 1 second."""
        while True:
            now = time.time()
            difference = now - self.last_message
            if difference > 1:
                self.controller.neutral()

            time.sleep(0.1)

    def on_message(self, message: str):
        print('Incoming message:', message)

        payload = message.split(' ')

        # Get command
        command = message
        if len(payload) >= 1:
            command = payload[0]
            del payload[0]

        # Get speed parameter
        speed = 0
        if len(payload) >= 1:
            speed = int(payload[0])

        if command == SOCKET_JOY_FORWARD:
            self.controller.forward(speed)

        if command == SOCKET_JOY_BACKWARD:
            self.controller.reverse(speed)

        if command == SOCKET_JOY_NEUTRAL:
            self.controller.neutral()

        if command == SOCKET_JOY_DIR_LEFT:
            self.controller.steer_left()

        if command == SOCKET_JOY_DIR_RIGHT:
            self.controller.steer_right()

        if command == SOCKET_JOY_DIR_NEUTRAL:
            self.controller.steer_neutral()

        self.last_message = time.time()


if __name__ == '__main__':
    vehicle = Vehicle()
    vehicle.listen()
