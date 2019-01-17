# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO

from actuators.Actuator import Actuator


class HBridgeActuator(Actuator):
    def __init__(self, pin_forward: int, pin_backward: int, pin_pwm: int):
        super().__init__()
        self.pin_forward = pin_forward
        self.pin_backward = pin_backward
        self.pin_pwm = pin_pwm

        GPIO.setup(pin_pwm, GPIO.OUT)
        GPIO.setup(pin_forward, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_backward, GPIO.OUT, initial=GPIO.LOW)

        self.power = GPIO.PWM(pin_pwm, 100)
        self.power.start(0)

    def forward(self, power: int = 100):
        if self.direction != 1:
            GPIO.output(self.pin_forward, GPIO.HIGH)
            GPIO.output(self.pin_backward, GPIO.LOW)

        self.power.ChangeDutyCycle(power)
        super().forward(power)

    def reverse(self, power: int = 100):
        if self.direction != -1:
            GPIO.output(self.pin_forward, GPIO.LOW)
            GPIO.output(self.pin_backward, GPIO.HIGH)

        self.power.ChangeDutyCycle(power)
        super().reverse(power)

    def neutral(self):
        GPIO.output(self.pin_backward, GPIO.LOW)
        GPIO.output(self.pin_forward, GPIO.LOW)
        self.power.ChangeDutyCycle(0)

        super().neutral()

    def exit(self):
        self.neutral()
        self.power.stop()
        super().exit()
