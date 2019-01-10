import os
import socket
import sys

import SocketServer
from lib.constants import *
from threading import Thread


class ThreadedSocketServerClient(Thread):
    def __init__(self, server: SocketServer, conn: socket):
        Thread.__init__(self)
        self.daemon = True

        self.server: SocketServer = server
        self.conn: socket = conn
        self.identity: str = None
        self.client = None

    def run(self):
        try:
            self.client = self.identify()
            self.conn.sendall(SOCKET_ID_APPROVED.encode())
            print('Connected', self.identity)
            self.listen()
            print('Disconnected', self.identity)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('EXCEPTION:', e, 'in ' + fname + ' line ' + str(exc_tb.tb_lineno))
            self.disconnect()

    def identify(self):
        """Assigns client based on identification."""
        self.identity = self.conn.recv(1024).decode().strip(SOCKET_EOL)

        if self.identity == SOCKET_ID_RECOGNITION:
            return self.client_recognition

        if self.identity == SOCKET_ID_VEHICLE:
            return self.client_vehicle

        if self.identity == SOCKET_ID_JOYSTICK:
            return self.client_joystick

        if self.identity == SOCKET_ID_FAKE:
            return self.client_fake

        raise Exception('Unknown identification: ' + self.identity)

    def listen(self):
        while True:
            try:
                data = self.conn.recv(1024)
            except ConnectionResetError:
                break
            except Disconnect:
                break

            # On disconnect
            if not data:
                return

            # Due to busy traffic data can be attached to each other
            messages = data.decode().strip(SOCKET_EOL).split(SOCKET_EOL)
            for message in messages:
                self.on_message(message)

    def on_message(self, message: str):
        """When receiving a message from connected client."""
        attributes = message.split()

        if len(attributes) >= 1:
            command = attributes.pop(0)

            self.client_global(command, attributes)
            if not self.client_global(command, attributes) or not self.client(command, attributes):
                self.send(SOCKET_ERR_UNKNOWN_CMD)

    def send(self, command, *params):
        message = (command + ' ' + ' '.join(params[0])).strip() + SOCKET_EOL
        self.conn.sendall(message.encode())

    def disconnect(self):
        print('Disconnecting connection with identity', self.identity)
        self.conn.close()

    def client_global(self, command, payload):
        if command == SOCKET_DISCONNECT:
            raise Disconnect

        return True

    def client_vehicle(self, command: str, payload):
        print('Vehicle')
        return False

    def client_joystick(self, command, payload):
        if command == SOCKET_JOY_FORWARD:
            return self.server.broadcast(SOCKET_ID_VEHICLE, SOCKET_JOY_FORWARD, payload[0] or '0')

        if command == SOCKET_JOY_BACKWARD:
            return self.server.broadcast(SOCKET_ID_VEHICLE, SOCKET_JOY_BACKWARD, payload[0] or '0')

        if command == SOCKET_JOY_NEUTRAL:
            return self.server.broadcast(SOCKET_ID_VEHICLE, SOCKET_JOY_NEUTRAL)

        if command == SOCKET_JOY_DIR_LEFT:
            return self.server.broadcast(SOCKET_ID_VEHICLE, SOCKET_JOY_DIR_LEFT)

        if command == SOCKET_JOY_DIR_RIGHT:
            return self.server.broadcast(SOCKET_ID_VEHICLE, SOCKET_JOY_DIR_RIGHT)

        if command == SOCKET_JOY_DIR_NEUTRAL:
            return self.server.broadcast(SOCKET_ID_VEHICLE, SOCKET_JOY_DIR_NEUTRAL)

        return False

    def client_recognition(self, command, payload):
        print('Recognition')

    def client_fake(self, command, payload):
        print('Received:', command, payload)
        return True


class Disconnect(ValueError):
    pass
