# noinspection PyUnresolvedReferences
from typing import List
import lib.settings
from lib.ThreadedSocketServerClient import *


class SocketServer:
    def __init__(self):
        self.clients: List[ThreadedSocketServerClient] = []
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

            client = ThreadedSocketServerClient(self, conn)
            self.clients.append(client)
            client.start()

    def broadcast(self, identity, command: str, *params):
        """Broadcasts command to all clients."""
        for client in self.clients:
            if client.identity == identity or identity == SOCKET_BROADCAST_ALL:
                client.send(command, params)

        return True


if __name__ == '__main__':
    server = SocketServer()
    server.listen()
