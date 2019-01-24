from threading import Thread

from controllers import Controller
from lib.SocketClient import SocketClient
from lib.constants import *
import time


class Vehicle:
    def __init__(self, controller: Controller):
        self.controller = controller
        self.client = SocketClient(SOCKET_ID_VEHICLE)
        self.last_message = time.time()
        self.blocked = False
        self.blocked_since = None

    def listen(self):
        self.client.connect(999999)

        # Start thread to watch for timeouts
        Thread(target=self.timeout_watcher, daemon=True).start()

        self.client.listen(self.on_message)

    def timeout_watcher(self):
        """Puts vehicle in neutral if no message was received in the last 1 second."""
        while True:
            now = time.time()

            # Put vehicle into neutral after 1 second
            if (now - self.last_message) > 1:
                self.controller.neutral()

            # Force vehicle into neutral
            if self.blocked:
                # Make sure we are blocking at least for 5 seconds after the last person was detected
                if (now - self.blocked_since) > 5:
                    self.unblock()
                    continue

                self.controller.neutral()

            time.sleep(0.5)

    def block(self):
        self.controller.neutral()
        self.blocked_since = time.time()
        self.blocked = True

    def unblock(self):
        self.blocked_since = None
        self.blocked = False

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
            print('Stopping for detected person')
            self.block()

        if command == SOCKET_RECOGNITION_FREE:
            print('Continue now that blockade is gone')
            self.unblock()

        self.last_message = time.time()
