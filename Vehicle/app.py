import * from Vehicle
import * from Motor

vehicle = Vehicle()

try:
    while True:
        vehicle.forward()
except KeyboardInterrupt:
    print('Ending program')

vehicle.exit()
