import RPi.GPIO as GPIO


class Vehicle:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.left = Motor(pin_forward=36, pin_backward=38, pin_pwm=40)
        self.right = Motor(pin_forward=33, pin_backward=35, pin_pwm=37)

    def forward(self, power=100):
        self.left.forward(power)
        self.right.forward(power)

    def reverse(self, power=100):
        self.left.reverse(power)
        self.right.reverse(power)

    def exit(self):
        self.left.exit()
        self.right.exit()
        GPIO.cleanup()
