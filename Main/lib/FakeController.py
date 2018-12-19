from lib.Controller import Controller


class FakeController(Controller):
    def __init__(self):
        super().__init__()

    def steer_left(self):
        print('Left')

    def steer_right(self):
        print('Right')

    def forward(self, power: int = 100):
        print('Forward')

    def reverse(self, power: int = 100):
        print('Reverse')

    def neutral(self):
        print('Neutral')

    def exit(self):
        print('Exit')
