# noinspection PyUnresolvedReferences
from actuators.ServoActuator import ServoActuator as Actuator
import os
from controllers.Controller import Controller

# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO


class ServoController(Controller):
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.servo = Actuator(int(os.getenv('PIN_SERVO_PWM')))
        self.base = 6
        self.power_division = 200

    def steer_neutral(self):
        self.servo.neutral()

    def forward(self, power: int = 100):
        power = self.base - (power / 200)
        self.servo.forward(power)

    def reverse(self, power: int = 100):
        power = self.base + (power / 200)
        self.servo.reverse(power)

    def neutral(self):
        self.servo.neutral()

    def exit(self):
        self.servo.exit()
        GPIO.cleanup()
