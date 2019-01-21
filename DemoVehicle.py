import os
import time
from threading import Thread

import pygame
from math import tan, radians, degrees, copysign
from pygame.math import Vector2

from lib.SocketClient import SocketClient
from lib.constants import *


class Car:
    def __init__(self, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=5.0):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 20
        self.brake_deceleration = 10
        self.free_deceleration = 2

        self.acceleration = 0.0
        self.steering = 0.0

    def update(self, dt):
        self.acceleration = max(-self.max_acceleration, min(self.acceleration, self.max_acceleration))
        self.steering = max(-self.max_steering, min(self.steering, self.max_steering))
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / tan(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

    def forward(self, dt):
        if self.velocity.x < 0:
            self.acceleration = self.brake_deceleration
        else:
            self.acceleration += 1 * dt

    def reverse(self, dt):
        if self.velocity.x > 0:
            self.acceleration = -self.brake_deceleration
        else:
            self.acceleration -= 1 * dt

    def brake(self, dt):
        if abs(self.velocity.x) > dt * self.brake_deceleration:
            self.acceleration = -copysign(self.brake_deceleration, self.velocity.x)
        else:
            self.acceleration = -self.velocity.x / dt

    def neutral(self, dt):
        if abs(self.velocity.x) > dt * self.free_deceleration:
            self.acceleration = -copysign(self.free_deceleration, self.velocity.x)
        else:
            if dt != 0:
                self.acceleration = -self.velocity.x / dt

    def steer_right(self, dt):
        self.steering -= 30 * dt

    def steer_left(self, dt):
        self.steering += 30 * dt

    def steer_neutral(self, dt):
        self.steering = 0


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Car tutorial')
        width = 1280
        height = 720
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.car = Car(0, 0)
        self.exit = False
        self.dt = 0

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, 'assets/car.png')
        car_image = pygame.image.load(image_path)
        ppu = 32

        client = SocketClient(SOCKET_ID_VEHICLE)
        client.connect()
        Thread(target=client.listen, args=(self.socket_event,), daemon=True).start()

        while not self.exit:
            self.dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            self.user_event(pygame.key.get_pressed())

            # Logic
            self.car.update(self.dt)

            # Drawing
            self.screen.fill((0, 0, 0))
            rotated = pygame.transform.rotate(car_image, self.car.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, self.car.position * ppu - (rect.width / 2, rect.height / 2))
            pygame.display.flip()

            self.clock.tick(self.ticks)

        pygame.quit()

    def user_event(self, pressed):
        if pressed[pygame.K_UP]:
            self.car.forward(self.dt)
        elif pressed[pygame.K_DOWN]:
            self.car.reverse(self.dt)
        elif pressed[pygame.K_SPACE]:
            self.car.brake(self.dt)
        else:
            self.car.neutral(self.dt)

        if pressed[pygame.K_RIGHT]:
            self.car.steer_right(self.dt)
        elif pressed[pygame.K_LEFT]:
            self.car.steer_left(self.dt)
        else:
            self.car.steer_neutral(self.dt)

    def socket_event(self, message):
        payload = message.split()

        if len(payload) <= 0:
            return

        command = payload[0]
        del payload[0]

        if command == SOCKET_JOY_FORWARD:
            # speed = 50
            # if len(payload) >= 0:
            #     speed = int(payload[0])
            self.car.forward(self.dt)
        elif command == SOCKET_JOY_BACKWARD:
            self.car.reverse(self.dt)
        elif command == SOCKET_JOY_NEUTRAL:
            self.car.brake(self.dt)

        if command == SOCKET_JOY_DIR_RIGHT:
            self.car.steer_right(self.dt)
        elif command == SOCKET_JOY_DIR_LEFT:
            self.car.steer_left(self.dt)
        elif command == SOCKET_JOY_DIR_NEUTRAL:
            self.car.steer_neutral(self.dt)


if __name__ == '__main__':
    game = Game()
    game.run()
