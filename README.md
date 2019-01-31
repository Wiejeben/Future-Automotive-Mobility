# Smarterdam
Repository for Smarterdam - Minor Future Automotive Mobility - University of Applied Sciences Rotterdam.

# Applications
This repository contains the following applications:
* `SocketServer.py`: Run this on your computer. This application takes care of connectivity between the other applications.
* `Joystick.py`: Run this on the computer that connects the PlayStation 4 controller.
* `PinkVehicle.py`: Run this in Virtualenv on the Raspberry Pi connected to the h-bridges in the pink vehicle.
* `DemoVehicle.py`: INCOMPLETE. This is a demo environment with a virtual vehicle.
* `ServoVehicle.py`: Run this in Virtualenv on the Raspberry Pi (with Python 3.6.5) connected to the servo actuator.

* `FakeVehicle.py`: To test your vehicles implementation.
* `FakeRecognition.py`: To simulate person detection.

* `services/Jetson-Object-Detection`: Execute `main.py` on the Nvidia Jetson. Use `config.yml` to set your environmental variables.
* `services/LIDAR`: Run this in Ubuntu with the RPLIDAR-A1.
* `services/Object-Detection`: Run this in Ubuntu in Docker with a USB camera attached. 

# Environmental variables
Environmental variables can be configured in the `.env` file (Note: During installation you must make a copy of `.env.example` to `.env` before starting the Python application).

# Virtualenv
It is recommended that you install the main application in Virtualenv. To set this up, execute `virtualenv -p python3.6 venv`.

In order to activate Virtualenv, execute `source venv/bin/activate`.

# Installation
To install dependencies, run `pip install -r requirements.txt`.
Make sure your environmental variables are up-to-date by comparing it to the `.env.example`.

# Pre-commit
To commit newly added dependencies, run `pip freeze > requirements.txt`.
