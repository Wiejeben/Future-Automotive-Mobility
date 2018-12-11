import RPi.GPIO as GPIO


class Actuator:
    def __init__(self, pin_forward, pin_backward, pin_pwm):
        self.pin_forward = pin_forward
        self.pin_backward = pin_backward
        self.pin_pwm = pin_pwm

        GPIO.setup(pin_pwm, GPIO.OUT)
        GPIO.setup(pin_forward, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_backward, GPIO.OUT, initial=GPIO.LOW)

        self.power = GPIO.PWM(pin_pwm, 100)
        self.power.start(0)

        # -1 = reverse
        # 0 = neutral
        # 1 = forward
        self.direction = 0

    def forward(self, power=100):
        print('Forward')

        if self.direction != 1:
            GPIO.output(self.pin_forward, GPIO.HIGH)
            GPIO.output(self.pin_backward, GPIO.LOW)
            self.direction = 1

        self.power.ChangeDutyCycle(power)

    def reverse(self, power=100):
        print('Reverse')

        if self.direction != -1:
            GPIO.output(self.pin_forward, GPIO.LOW)
            GPIO.output(self.pin_backward, GPIO.HIGH)
            self.direction = -1

        self.power.ChangeDutyCycle(power)

    def neutral(self):
        GPIO.output(self.pin_backward, GPIO.LOW)
        GPIO.output(self.pin_forward, GPIO.LOW)
        self.power.ChangeDutyCycle(0)
        self.direction = 0

    def exit(self):
        self.neutral()
        self.power.stop()
