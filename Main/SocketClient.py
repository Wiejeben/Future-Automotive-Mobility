import settings
import os
import socket
import select
import time


class SocketClient:
    def __init__(self, on_disconnect=None):
        self.host = str(os.getenv('SOCKET_HOST', '0.0.0.0'))
        self.port = int(os.getenv('SOCKET_PORT'))
        self.connection = None
        self.on_disconnect = on_disconnect

    def connect(self, times_retrying: int = 5) -> bool:
        print('Connecting to remote host', self.host + ':' + str(self.port))

        try:
            self.connection = socket.socket()
            self.connection.connect((self.host, self.port))
        except socket.error as exception:
            print('Failed to connect to server:', exception)

            if times_retrying > 0:
                print('Retrying in 5 seconds (' + str(times_retrying - 1) + ' attempts left)')
                time.sleep(5)
                return self.connect(times_retrying - 1)

            return False

        print('Connection established')
        return True

    def disconnect(self) -> None:
        print('Closing connection')

        if self.on_disconnect:
            self.on_disconnect()

        # 0 = done receiving, 1 = done sending, 2 = both
        self.connection.close()

    def listen(self, callback, reconnect=True) -> None:
        print('Started listening')
        try:
            while True:
                try:
                    # Use select so that as soon as the connection fails, we will be able to reconnect
                    ready_to_read, ready_to_write, in_error = select.select(
                        [self.connection, ], [self.connection, ], [], 5
                    )
                except select.error as exception:
                    print('Connection error:', exception)

                    if not reconnect:
                        break

                    if not self.connect():
                        break

                if len(ready_to_read) > 0:
                    recv = self.connection.recv(1024).decode()

                    if not recv:
                        print('Server left the room')
                        self.disconnect()

                        if not reconnect:
                            break

                        if not self.connect():
                            break

                        continue

                    callback(recv)

                time.sleep(0.1)
        except KeyboardInterrupt:
            self.disconnect()

    def send(self, message: str) -> None:
        self.connection.send(message.encode())


if __name__ == '__main__':
    def on_disconnect() -> None:
        print('SHUTDOWN YOUR ENGINES')


    def on_message(message: str) -> None:
        print('SERVER:', message)


    client = SocketClient(on_disconnect)

    if client.connect():
        client.listen(on_message)
