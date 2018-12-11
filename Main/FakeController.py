from Controller import Controller


class FakeController(Controller):
    def __init__(self):
        super().__init__()

    def forward(self, power: int = 100):
        print('Forward')

    def reverse(self, power: int = 100):
        print('Reverse')

    def neutral(self):
        print('Neutral')

    def exit(self):
        print('Exit')
