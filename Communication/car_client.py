import socket

class CarClient():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def init(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host,self.port))
        print('Connection established.')
    
    def listenToServer(self):
        while True:
            reply = self.socket.recv(1024).decode()
            if reply == 'Terminate':
                break
            print(reply)

a = CarClient('192.168.43.238', 3000)
a.init()
a.listenToServer()        