import socket

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def showInfo(self):
        print('Host: ', self.host)
        print('Port: ', self.port)
    
    def initialize(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket has been created!')

        try:
            self.socket.bind((self.host, self.port))
        except RuntimeError as error:
            print(error)

        self.socket.listen(5)
        print('Socket ready to listen to messages')
        (self.conn, self.addr) = self.socket.accept()
        print('Connected')
    
    def listenToClients(self):
        while True:
            data = self.conn.recv(1024).decode()
            print('I sent a message back in response to: ', data)
            reply = ''

            # process your message
            if data == 'Hello':
                reply = 'Hi, back!'
            elif data == 'This is important':
                reply = 'OK, I have done the important thing you have asked me!'

            #and so on and on until...
            elif data == 'quit':
                self.conn.send('Terminate'.encode())
                self.closeConnections()
                break
            else:
                reply = 'Unknown command'

            # Sending reply
            self.conn.send(reply.encode())

    def closeConnections(self):
        self.conn.close()

a = Server('0.0.0.0', 3000)
a.initialize()
a.listenToClients()