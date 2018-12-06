import socket
from threading import Thread


class Server:
    def __init__(self, port):
        self.port = port
        self.clients = {}

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
                conn, addr = self.socket.accept()
            except KeyboardInterrupt:
                if conn:
                    conn.close()
                break

            print('Connection from', addr[0], ':', str(addr[1]))

            Thread(target=self.threaded_client, args=(conn, addr[1]), daemon=True).start()

    def threaded_client(self, conn, port):
        """
        Client instants listening for messages.
        """

        self.clients[port] = conn

        conn.send(str.encode('Welcome, type your info\n'))

        while True:
            data = conn.recv(1024)

            # On disconnect
            if not data:
                break

            # Disconnect when on message returns False
            if not self.on_message(conn, data.decode('utf-8')):
                break

        del self.clients[port]
        conn.close()

    def on_message(self, conn, message):
        """
        When receiving a message from connected client.
        """

        if message == 'broadcast':
            for port, client in self.clients.items():
                client.sendall(str.encode('Person detected!'))
        elif message == 'bye':
            return False
        else:
            conn.sendall(str.encode('Unknown command: ' + message))

        return True


if __name__ == '__main__':
    Server(5558).listen()
