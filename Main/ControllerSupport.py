
# This file presents an interface for interacting with the Playstation 4 Controller
# in Python. Simply plug your PS4 controller into your computer using USB and run this
# script!
#
# NOTE: I assume in this script that the only joystick plugged in is the PS4 controller.
#       if this is not the case, you will need to change the class accordingly.
#
# Copyright © 2015 Clay L. McLeod <clay.l.mcleod@gmail.com>
#
# Distributed under terms of the MIT license.

import os
import pprint
import pygame
from SocketClient import SocketClient
import numpy as np
import time

class PS4Controller(object):
    """Class representing the PS4 controller."""

    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def __init__(self):
        """Initialize the joystick components"""
        
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        """Initialze Communication Client"""
        self.client = SocketClient()
        self.connect()

    def connect(self):
        """Connect with server"""
        self.client.connect()

    def sendInput(self, message: str):
        """Send controller output to server"""
        self.client.send(message)

    def listen(self):
        """Listen for events to happen"""
        
        if not self.axis_data:
            self.axis_data = {}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = round(event.value,2)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value

                # Insert your code on what you would like to happen for each event here!
                # In the current setup, I have the state simply printing out to the screen.
                
                # os.system('clear')
                # print(self.button_data)
                # print(self.axis_data)
                # print(self.hat_data)

                # 0 = []
                # 1 = x
                # 2 = O
                # 3 = /\
                # 4 = L1
                # 5 = R1
                # 6 = L2
                # 7 = R2
                # 8 = share
                # 9 = options
                # 10= L3
                # 11= R3
                # 12 = PSbutton
                # 13 = touchpad


                if(self.button_data[6]):
                    time.sleep(0.1)
                    print('L2 is Pressed. Telling the car to go backwards')
                    self.sendInput('backward')

                if(self.button_data[7]):
                    time.sleep(0.1)

                    mappedR2Value = np.interp(self.axis_data[5], (-1,1), (0,100))
                    
                    print('R2 is Pressed. Telling the car to go forwards with specific speed')
                    print(mappedR2Value)

                    if(mappedR2Value < 33):
                        print('30% POWERR!')
                        self.sendInput('30% POWER!')
                    elif(mappedR2Value < 66):
                        print('60% POWERR!')
                        self.sendInput('60% POWER!')
                    elif(mappedR2Value <= 100):
                        print('100% POWERR!')
                        self.sendInput('100% POWER!')
                        
                elif(not self.button_data[6] and not self.button_data[7]):
                    time.sleep(0.1)
                    self.sendInput('Neutral')
                
                

                


if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.listen()