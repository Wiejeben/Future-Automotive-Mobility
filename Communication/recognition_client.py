import socket

class RecognitionClient():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def init(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host,self.port))
        print('Connection established.')
    
    def talkToServer(self, action):
        command = action
        print(command)
        self.socket.send(command.encode())

a = RecognitionClient('192.168.43.238', 3000)
a.init()
a.talkToServer('people crossing the street')
# a.talkToServer('person might cross the street')  