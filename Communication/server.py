import socket
import traceback
import sys
from threading import Thread

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def showInfo(self):
        print('Host: ', self.host)
        print('Port: ', self.port)
    
    def initialize(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('Socket has been created!')

        try:
            self.socket.bind((self.host, self.port))
        except RuntimeError as error:
            print(error)

        self.socket.listen(5)
        print('Socket now listening')


        # infinite loop- do not reset for every requests
        while True:
            connection, address = self.socket.accept()
            ip, port = str(address[0]), str(address[1])
            print("Connected with " + ip + ":" + port)
            
            try:
                Thread(target=self.client_thread, args=(connection, ip, port)).start()
            except:
                print('Thread did not start')
                traceback.print_exc()
        
        self.socket.close()
            
        # (self.conn, self.addr) = self.socket.accept()
        # print('Connected')
    
    def client_thread(self, connection, ip, port, max_buffer_size = 5120):
        is_active = True

        while is_active:
            client_input = self.receive_input(connection, max_buffer_size)

            if "--QUIT--" in client_input:
                print("Client is requesting to quit")
                connection.close()
                print("Connection " + ip + ":" + port + " closed")
                is_active = False
            else:
                print("Processed result: {}".format(client_input))
                connection.sendall("-".encode("utf8"))
    
    def receive_input(self, connection, max_buffer_size):
        client_input = connection.recv(max_buffer_size)
        client_input_size = sys.getsizeof(client_input)

        if client_input_size > max_buffer_size:
            print("The input size is greater than expected {}".format(client_input_size))

        decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
        result = self.process_input(decoded_input)

        return result

    def process_input(self, input_str):
        print("Processing the input received from client")
        return "Hello " + str(input_str).upper() 

a = Server('192.168.43.238', 3000)
a.initialize()
# a.listenToClients()
# a.closeConnections()