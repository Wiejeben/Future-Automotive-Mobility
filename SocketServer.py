# noinspection PyUnresolvedReferences
from typing import List

import lib.settings
import os
from threading import Thread

from lib.ThreadedSocketServerClient import *


class SocketServer:
    def __init__(self):
        self.clients = []
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

            client = ThreadedSocketServerClient(server, conn, port)
            self.clients.append(client)
            client.start()

    def broadcast_command(self, command: str, *params):
        """Broadcasts command to all clients."""
        pass
        # payload = ' '.join([command] + list(params))
        # self.broadcast(payload)

    def broadcast(self, message: str):
        """Broadcasts to all clients."""
        pass
        # message += SOCKET_EOL
        #
        # for port, client in self.clients.items():
        #     client.sendall(message.encode())


if __name__ == '__main__':
    server = SocketServer()
    server.listen()
