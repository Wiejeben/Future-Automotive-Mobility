from controllers.ServoController import ServoController
from vehicles.Vehicle import Vehicle


class ServoVehicle(Vehicle):
    def __init__(self):
        controller = ServoController()
        super().__init__(controller)


if __name__ == '__main__':
    vehicle = ServoVehicle()
    vehicle.listen()
