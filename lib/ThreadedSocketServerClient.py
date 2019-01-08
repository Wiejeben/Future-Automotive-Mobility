import socket
import SocketServer
from lib.constants import *
from threading import Thread


class ThreadedSocketServerClient(Thread):
    def __init__(self, server: SocketServer, conn: socket, port: int):
        Thread.__init__(self)
        self.daemon = True

        self.server = server
        self.conn = conn
        self.port = port
        self.identity = None
        self.client = None

    def start(self):
        self.client = self.identify()
        self.conn.sendall(SOCKET_ID_APPROVED.encode())
        print('Connected', self.identity)
        self.listen()
        print('Disconnected', self.identity)

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
        try:
            while True:
                try:
                    data = self.conn.recv(1024)
                except ConnectionResetError:
                    break

                # On disconnect
                if not data:
                    return

                # Due to busy traffic data can be attached to each other
                messages = data.decode().strip(SOCKET_EOL).split(SOCKET_EOL)
                for message in messages:
                    if not self.on_message(message):
                        break
        except Disconnect:
            self.disconnect()

    def on_message(self, message: str):
        """When receiving a message from connected client."""
        attributes = message.split()

        if len(attributes) >= 1:
            command = attributes.pop(0)

            self.client_general(command, attributes)
            self.client(command, attributes)

    def send(self, response):
        # Send response to client
        if type(response) == list and len(response) >= 1:
            self.conn.sendall(str.encode(' '.join(response)))

        return True

    def disconnect(self):
        print('Disconnecting connection with identity', self.name)
        self.conn.close()

    def client_general(self, command, payload):
        if command == SOCKET_DISCONNECT:
            raise Disconnect

    def client_vehicle(self, command, payload):
        print('Vehicle')

    def client_joystick(self, command, payload):
        if command == SOCKET_JOY_BACKWARD:
            self.server.broadcast_command(SOCKET_ID_VEHICLE, SOCKET_JOY_BACKWARD, payload[0] or '0')

        if command == SOCKET_JOY_NEUTRAL:
            self.server.broadcast_command(SOCKET_ID_VEHICLE, SOCKET_JOY_BACKWARD)

        if command == SOCKET_JOY_DIR_LEFT:
            self.server.broadcast_command(SOCKET_ID_VEHICLE, SOCKET_JOY_DIR_LEFT)

        if command == SOCKET_JOY_DIR_RIGHT:
            self.server.broadcast_command(SOCKET_ID_VEHICLE, SOCKET_JOY_DIR_RIGHT)

        if command == SOCKET_JOY_DIR_NEUTRAL:
            self.server.broadcast_command(SOCKET_ID_VEHICLE, SOCKET_JOY_DIR_NEUTRAL)

    def client_recognition(self, command, payload):
        print('Recognition')

    def client_fake(self, command, payload):
        print('Received:', command, payload)

    # def parse_command(self, command: str, params: List[str]):
    #     if command == SOCKET_JOY_FORWARD:
    #         speed = params[0] or '0'
    #
    #         self.broadcast_command(SOCKET_JOY_FORWARD, speed)
    #         return True
    #
    #     if command == SOCKET_JOY_BACKWARD:
    #         speed = params[0] or '0'
    #
    #         self.broadcast_command(SOCKET_JOY_BACKWARD, speed)
    #         return True
    #
    #     if command == SOCKET_JOY_NEUTRAL:
    #         self.broadcast_command(SOCKET_JOY_NEUTRAL)
    #         return True
    #
    #     if command == SOCKET_JOY_DIR_LEFT:
    #         self.broadcast_command(SOCKET_JOY_DIR_LEFT)
    #         return True
    #
    #     if command == SOCKET_JOY_DIR_RIGHT:
    #         self.broadcast_command(SOCKET_JOY_DIR_RIGHT)
    #         return True
    #
    #     if command == SOCKET_JOY_DIR_NEUTRAL:
    #         self.broadcast_command(SOCKET_JOY_DIR_NEUTRAL)
    #         return True
    #
    #     if command == SOCKET_DISCONNECT:
    #         return False
    #
    #     return [SOCKET_ERR_UNKNOWN]


class Disconnect(ValueError):
    pass
