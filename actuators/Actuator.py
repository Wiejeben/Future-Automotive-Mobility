class Actuator:
    def __init__(self):
        # -1 = reverse
        # 0 = neutral
        # 1 = forward
        self.direction = 0

    def forward(self, power: int = 100):
        print('Forward', power)

        if self.direction != 1:
            self.direction = 1

    def reverse(self, power: int = 100):
        print('Reverse', power)

        if self.direction != -1:
            self.direction = -1

    def neutral(self):
        print('Neutral')
        self.direction = 0

    def exit(self):
        print('Exit')

        self.neutral()
