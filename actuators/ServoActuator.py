# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO

from actuators.Actuator import Actuator


class ServoActuator(Actuator):
    def __init__(self, pin: int):
        GPIO.setup(pin, GPIO.OUT)
        self.power = GPIO.PWM(pin, 100)
        self.power.start(0)

        self.base = 6
        self.power_division = 100

        super().__init__()

    def forward(self, power: int = 100):
        dc = self.base - (power / self.power_division)
        print(dc)
        self.power.ChangeDutyCycle(dc)
        super().forward(power)

    def reverse(self, power: int = 100):
        dc = self.base + (power / self.power_division)
        print(dc)
        self.power.ChangeDutyCycle(dc)
        super().reverse(power)

    def neutral(self):
        print(self.base)
        self.power.ChangeDutyCycle(self.base)
        super().neutral()

    def exit(self):
        self.power.stop()
        super().exit()
