# noinspection PyUnresolvedReferences
from lib import settings
import os
from lib.Controller import Controller
from lib.Actuator import Actuator

# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO


class GPIOController(Controller):
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.left = Actuator(
            pin_forward=int(os.getenv('PIN_LEFT_FORWARD')),
            pin_backward=int(os.getenv('PIN_LEFT_BACKWARD')),
            pin_pwm=int(os.getenv('PIN_LEFT_PWM'))
        )

        self.right = Actuator(
            pin_forward=int(os.getenv('PIN_RIGHT_FORWARD')),
            pin_backward=int(os.getenv('PIN_RIGHT_BACKWARD')),
            pin_pwm=int(os.getenv('PIN_RIGHT_PWM'))
        )

        self.steering = Actuator(
            pin_forward=int(os.getenv('PIN_STEER_LEFT')),
            pin_backward=int(os.getenv('PIN_STEER_RIGHT')),
            pin_pwm=int(os.getenv('PIN_STEER_PWM'))
        )

    def steer_left(self):
        self.steering.reverse()

    def steer_right(self):
        self.steering.forward()

    def steer_neutral(self):
        self.steering.neutral()

    def forward(self, power: int = 100):
        self.left.forward(power)
        self.right.forward(power)

    def reverse(self, power: int = 100):
        self.left.reverse(power)
        self.right.reverse(power)

    def neutral(self):
        self.left.neutral()
        self.right.neutral()

    def exit(self):
        self.left.exit()
        self.right.exit()
        GPIO.cleanup()
