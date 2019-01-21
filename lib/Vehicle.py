from threading import Thread

from controllers import Controller
from controllers.FakeController import FakeController
from lib.SocketClient import SocketClient
from lib.constants import *
import time


class Vehicle:
    def __init__(self, controller: Controller):
        self.controller = controller
        self.client = SocketClient(SOCKET_ID_VEHICLE)
        self.last_message = time.time()
        self.blocked = False

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

            # Put vehicle into neutral after 1 second
            if difference > 1:
                self.controller.neutral()

            # Force vehicle into neutral
            if self.blocked:
                self.controller.neutral()

            time.sleep(0.1)

    def on_message(self, message: str):
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

        # Prevent accelerating when blocked
        if not self.blocked:
            if command == SOCKET_JOY_FORWARD:
                self.controller.forward(speed)

            if command == SOCKET_JOY_BACKWARD:
                self.controller.reverse(speed)

        if command == SOCKET_JOY_NEUTRAL:
            self.controller.neutral()

        if command == SOCKET_JOY_DIR_NEUTRAL:
            self.controller.steer_neutral()

        if command == SOCKET_JOY_DIR_LEFT:
            self.controller.steer_left()

        if command == SOCKET_JOY_DIR_RIGHT:
            self.controller.steer_right()

        if command == SOCKET_RECOGNITION_DETECTED:
            print('[INFO] Stopping for detected person')
            self.blocked = True
            self.controller.neutral()

        if command == SOCKET_RECOGNITION_FREE:
            print('[INFO] Continue now that blockade is gone')
            self.blocked = False

        self.last_message = time.time()
