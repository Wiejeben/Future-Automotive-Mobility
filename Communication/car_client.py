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
            elif reply == 'test1':
                print('Dit was test 1')
            elif reply == 'test2':
                print('Dit was test 2')
            elif reply == 'test3':
                print('Dit was test 3')
            elif reply == 'test4':
                print('Dit was test 4')
            
            # print(reply)

a = CarClient('192.168.43.238', 3000)
a.init()
a.listenToServer()        