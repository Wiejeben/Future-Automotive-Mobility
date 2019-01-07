from lib.Controller import Controller


class FakeController(Controller):
    def __init__(self):
        super().__init__()

    def steer_left(self):
        print('Left')

    def steer_right(self):
        print('Right')

    def steer_neutral(self):
        print('No Steering')

    def forward(self, power: int = 100):
        print('Forward', power)

    def reverse(self, power: int = 100):
        print('Reverse', power)

    def neutral(self):
        print('Neutral')

    def exit(self):
        print('Exit')
