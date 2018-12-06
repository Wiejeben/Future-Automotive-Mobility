import RPi.GPIO as GPIO

class Vehicle:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.left = Motor(0, 0, 0)
        self.right = Motor(0, 0, 0)

    def __del__(self):
        GPIO.cleanup()

class Motor:
    def __init__(self, pin_forward, pin_backward, pin_pwm):
        self.pin_forward = pin_forward
        self.pin_backward = pin_backward
        self.pin_pwm = pin_pwm
        self.power = GPIO.PWM(pin_pwm, 50)

        GPIO.setup(pin_forward, GPIO.OUT)
        GPIO.setup(pin_backward, GPIO.OUT)
        GPIO.output(pin_forward, GPIO.LOW)
        GPIO.output(pin_backward, GPIO.LOW)

    def forward(self):
        print('Forward')

        self.power.start(1)
        GPIO.output(self.pin_forward, GPIO.HIGH)
        GPIO.output(self.pin_forward, GPIO.LOW)

    def reverse(self):
        print('Reverse')

        self.power.start(1)

        GPIO.output(self.pin_backward, GPIO.HIGH)
        GPIO.output(self.pin_backward, GPIO.LOW)

    def stop(self):
        print('Stop')

        self.power.stop()

    def __del__(self):
        self.stop()

if __name__ == '__main__':
    vehicle = Vehicle()