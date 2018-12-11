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
            data = conn.recv(1024)
            # On disconnect
            if not data:
                break

            # Disconnect when on message returns False
            if not self.on_message(conn, data.decode('utf-8')):
                break

        print('Client disconnected')
        del self.clients[port]
        conn.close()

    def on_message(self, conn: socket, message: str):
        """
        When receiving a message from connected client.
        """

        if message == '1':
            self.broadcast('neutral')
        elif message == '0':
            self.broadcast('forward')
        elif message == 'bye':
            return False
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
