# noinspection PyUnresolvedReferences
import settings
import os
import socket
from threading import Thread


class SocketServer:
    def __init__(self):
        self.clients = {}
        self.port = int(os.getenv('SOCKET_PORT'))

        # Create IPv4 TCP server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port))

    def listen(self):
        """
        Listens for connecting clients and creates a thread for each connection.
        """
        self.socket.listen(5)

        print('Server is available on port', self.port)

        while True:
            conn = None

            try:
                # Awaits incoming connections
                conn, addr = self.socket.accept()
            except KeyboardInterrupt:
                if conn:
                    conn.close()
                break

            print('Connection from', addr[0] + ':' + str(addr[1]))

            Thread(target=self.threaded_client, args=(conn, addr[1]), daemon=True).start()

    def threaded_client(self, conn: socket, port: int):
        """
        Client instants listening for messages.
        """

        self.clients[port] = conn

        while True:
            try:
                data = conn.recv(1024)
            except ConnectionResetError:
                break

            # On disconnect
            if not data:
                break

            # Disconnect when on message returns False
            if not self.on_message(conn, data.decode('utf-8')):
                break

        print('Client (' + str(port) + ') disconnected')
        del self.clients[port]
        conn.close()

    def on_message(self, conn: socket, message: str):
        """
        When receiving a message from connected client.
        """
        print('Received:', message)

        if message == '30% POWER!':
            self.broadcast('30% POWER')
        elif message == '60% POWER!':
            self.broadcast('60% POWER')
        elif message == '100% POWER!':
            self.broadcast('100% POWER')
        elif message == 'backward':
            self.broadcast('backward')
        elif message == 'Neutral':
            self.broadcast('neutral')
        elif message == 'bye':
            return False
        elif message == '-':
            return True
        else:
            conn.sendall(str.encode('Unknown command: ' + message))

        return True

    def broadcast(self, message: str):
        """
        Broadcasts to all clients.
        """

        for port, client in self.clients.items():
            client.sendall(message.encode())


if __name__ == '__main__':
    server = SocketServer()
    server.listen()
