from controllers.FakeController import FakeController
from lib.Vehicle import Vehicle


class FakeVehicle(Vehicle):
    def __init__(self):
        controller = FakeController()
        super().__init__(controller)


if __name__ == '__main__':
    vehicle = FakeVehicle()
    vehicle.listen()
