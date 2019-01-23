from threading import Thread

import pygame
from lib.SocketClient import SocketClient
from lib.constants import *
import numpy as np


class Joystick(object):
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.thread = Thread(target=self.broadcast, daemon=True)

        self.axis_data = {}

        self.button_data = {}
        if len(self.button_data) <= 0:
            for i in range(self.joystick.get_numbuttons()):
                self.button_data[i] = False

        self.hat_data = {0: (0, 0)}
        if len(self.hat_data):
            for i in range(self.joystick.get_numhats()):
                self.hat_data[i] = (0, 0)

        self.client = SocketClient(SOCKET_ID_JOYSTICK)
        self.client.connect()
        # Start listen thread so it will automatically reconnect
        Thread(target=self.client.listen, args=(self.on_message,), daemon=True).start()

        self.clock = pygame.time.Clock()

        # Current controller positions
        self.forward = 0
        self.reverse = 0
        self.left = False
        self.right = False

    def listen(self):
        """Listen for events from the joystick."""
        self.thread.start()

        while True:
            self.clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = round(event.value, 2)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value

                button_l2 = self.button_data[6]
                button_r2 = self.button_data[7]

                # Both buttons pressed
                if button_l2 and button_r2:
                    self.forward = 0
                    self.reverse = 0
                elif button_l2:
                    mapped_l2_value = int(np.interp(self.axis_data[4], (-1, 1), (0, 100)))
                    self.reverse = mapped_l2_value
                elif button_r2:
                    mapped_r2_value = int(np.interp(self.axis_data[5], (-1, 1), (0, 100)))
                    self.forward = mapped_r2_value

                # Neither button pressed
                elif not button_l2 and not button_r2:
                    self.forward = 0
                    self.reverse = 0

                direction = self.hat_data[0][0]
                if direction == 1:
                    self.left = False
                    self.right = True
                elif direction == -1:
                    self.left = True
                    self.right = False
                else:
                    self.left = False
                    self.right = False

    def on_message(self, message):
        print(message)

    def broadcast(self):
        while True:
            self.clock.tick(10)

            if not self.client.connected:
                continue

            # Steering
            if self.left:
                print('STEER: Left')
                self.client.send_command(SOCKET_JOY_DIR_LEFT)
            elif self.right:
                print('STEER: Right')
                self.client.send_command(SOCKET_JOY_DIR_RIGHT)
            else:
                print('STEER: Neutral')
                self.client.send_command(SOCKET_JOY_DIR_NEUTRAL)

            # Speed
            if self.forward > 0:
                print('Forward', self.forward)
                self.client.send_command(SOCKET_JOY_FORWARD, self.forward)
            elif self.reverse > 0:
                print('Reverse', self.reverse)
                self.client.send_command(SOCKET_JOY_BACKWARD, self.reverse)
            else:
                print('Neutral')
                self.client.send_command(SOCKET_JOY_NEUTRAL)


if __name__ == '__main__':
    joystick = Joystick()
    joystick.listen()
