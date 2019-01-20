# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO

from actuators.Actuator import Actuator


class ServoActuator(Actuator):
    def __init__(self, pin: int, base: int = 6, power_devision: int = 100):
        GPIO.setup(pin, GPIO.OUT)
        self.power = GPIO.PWM(pin, 100)
        self.power.start(base)

        self.base = base
        self.power_division = power_devision

        super().__init__()

    def forward(self, power: int = 100):
        dc = self.base - (power / self.power_division)
        self.power.ChangeDutyCycle(dc)
        super().forward(power)

    def reverse(self, power: int = 100):
        dc = self.base + (power / self.power_division)
        self.power.ChangeDutyCycle(dc)
        super().reverse(power)

    def neutral(self):
        self.power.ChangeDutyCycle(self.base)
        super().neutral()

    def exit(self):
        self.power.stop()
        super().exit()
