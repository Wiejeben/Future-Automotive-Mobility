# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO

from actuators.Actuator import Actuator


class ServoActuator(Actuator):
    def __init__(self, pin: int):
        GPIO.setup(pin, GPIO.OUT)
        self.power = GPIO.PWM(pin, 100)
        self.power.start(0)

        super().__init__()

    def forward(self, power: int = 100):
        self.power.ChangeDutyCycle(power)
        super().forward(power)

    def reverse(self, power: int = 100):
        self.power.ChangeDutyCycle(power)
        super().reverse(power)

    def neutral(self):
        self.power.ChangeDutyCycle(0)
        super().neutral()

    def exit(self):
        self.power.stop()
        super().exit()
