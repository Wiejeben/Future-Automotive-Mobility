from controllers.HBridgeController import HBridgeController
from vehicles.Vehicle import Vehicle


class PinkVehicle(Vehicle):
    def __init__(self):
        controller = HBridgeController()
        super().__init__(controller)


if __name__ == '__main__':
    vehicle = PinkVehicle()
    vehicle.listen()
