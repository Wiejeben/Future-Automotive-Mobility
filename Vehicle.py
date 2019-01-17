from lib.Vehicle import Vehicle as BaseVehicle

from controllers.Controller import Controller


class Vehicle(BaseVehicle):
    def __init__(self):
        controller = Controller()
        super().__init__(controller)


if __name__ == '__main__':
    vehicle = Vehicle()
    vehicle.listen()
