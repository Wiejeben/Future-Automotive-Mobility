import socket
import time
from builtins import zip
from threading import Thread
import numpy as np
from lib.config import load_config
from lib.constants import *


class ThreadedSocketClient(Thread):

    def __init__(self, category_index, threshold):
        Thread.__init__(self)
        self.daemon = True
        self.category_index = category_index
        self.threshold = threshold

        config = load_config()
        self.host = config['remote_host']
        self.port = config['remote_port']

        self.boxes = None
        self.scores = None
        self.classes = None

    def run(self):
        # Create Socket connection
        connection = socket.socket()
        connection.connect((self.host, self.port))
        connection.send((SOCKET_ID_RECOGNITION + SOCKET_EOL).encode())

        while True:
            time.sleep(0.1)
            if self.boxes is None or self.scores is None or self.classes is None:
                time.sleep(1)
                continue

            for box, score, classification in zip(
                    np.squeeze(self.boxes),
                    np.squeeze(self.scores),
                    np.squeeze(self.classes)
            ):
                if score > self.threshold:
                    label = self.category_index[classification]['name']

                    if label == 'person':
                        connection.send((SOCKET_RECOGNITION_DETECTED + SOCKET_EOL).encode())
                        print('> [INFO] Person detected')
                        break
                    # print("==========\nlabel: {}\nscore: {}\nbox: {}".format(label, score, box))
