# noinspection PyUnresolvedReferences
from typing import List

from lib import settings
import os
import socket
from threading import Thread
from lib.constants import *


class SocketServer:
    def __init__(self):
        self.clients = {}
        self.port = int(os.getenv('SOCKET_PORT'))

        # Create IPv4 TCP server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port))

    def listen(self):
        """Listens for connecting clients and creates a thread for each connection."""
        self.socket.listen(5)

        print('Server is available on port', self.port)

        while True:
            conn = None

            try:
                # Awaits incoming connections
                conn, (ip, port) = self.socket.accept()
            except KeyboardInterrupt:
                if conn:
                    conn.close()
                break

            print('Connection from', ip + ':' + str(port))

            Thread(target=self.threaded_client, args=(conn, port), daemon=True).start()

    def threaded_client(self, conn: socket, port: int):
        """Client instants listening for messages."""

        self.clients[port] = conn

        while True:
            try:
                data = conn.recv(1024)
            except ConnectionResetError:
                break

            # On disconnect
            if not data:
                break

            messages = data.decode().split(SOCKET_EOL)
            messages.pop()
            for message in messages:
                if not self.on_message(conn, message):
                    break

        print('Client (' + str(port) + ') disconnected')
        del self.clients[port]
        conn.close()

    def on_message(self, conn: socket, message: str):
        """When receiving a message from connected client."""
        print('Received from:', message)
        payload = message.split()

        response = True
        if len(payload) >= 1:
            command = payload[0]
            del payload[0]

            response = self.parse_command(command, payload)

        if type(response) == bool:
            return response

        if type(response) == list and len(response) >= 1:
            conn.sendall(str.encode(' '.join(response)))

        return True

        # if message == '30% POWER!':
        #     self.broadcast('30% POWER')
        # elif message == '60% POWER!':
        #     self.broadcast('60% POWER')
        # elif message == '100% POWER!':
        #     self.broadcast('100% POWER')
        # elif message == 'backward':
        #     self.broadcast('backward')
        # elif message == 'Neutral':
        #     self.broadcast('neutral')
        # elif message == 'bye':
        #     return False
        # elif message == '-':
        #     return True
        # else:
        #     conn.sendall(str.encode('Unknown command: ' + message))
        #
        # return True

    def parse_command(self, command: str, params: List[str]):
        if command == SOCKET_ID_RECOGNITION:
            return [SOCKET_ID_APPROVED]

        if command == SOCKET_ID_VEHICLE:
            return [SOCKET_ID_APPROVED]

        if command == SOCKET_ID_JOYSTICK:
            return [SOCKET_ID_APPROVED]

        if command == SOCKET_ID_FAKE:
            return [SOCKET_ID_APPROVED]

        if command == SOCKET_JOY_FORWARD:
            speed = params[0] or '0'

            self.broadcast_command(SOCKET_JOY_FORWARD, speed)
            return True

        if command == SOCKET_JOY_BACKWARD:
            speed = params[0] or '0'

            self.broadcast_command(SOCKET_JOY_BACKWARD, speed)
            return True

        if command == SOCKET_JOY_NEUTRAL:
            self.broadcast_command(SOCKET_JOY_NEUTRAL)
            return True

        if command == SOCKET_DISCONNECT:
            return False

        return [SOCKET_ERR_UNKNOWN]

    def broadcast_command(self, command: str, *params):
        """Broadcasts command to all clients."""
        payload = ' '.join([command] + list(params)).encode()

        for port, client in self.clients.items():
            client.sendall(payload)

    def broadcast(self, message: str):
        """Broadcasts to all clients."""

        for port, client in self.clients.items():
            client.sendall(message.encode())


if __name__ == '__main__':
    server = SocketServer()
    server.listen()
