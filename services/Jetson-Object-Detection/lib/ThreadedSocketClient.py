import time
from builtins import zip
from threading import Thread

from lib.SocketClient import SocketClient
from lib.constants import *


class ThreadedSocketClient(Thread):

    def __init__(self, category_index, threshold):
        Thread.__init__(self)
        self.daemon = True
        self.category_index = category_index
        self.threshold = threshold

        self.boxes = None
        self.scores = None
        self.classes = None

    def run(self):
        # Create Socket connection
        client = SocketClient(SOCKET_ID_RECOGNITION)
        client.connect(99999)

        # Add listen thread for automatic reconnecting
        Thread(target=client.listen, args=(print,), daemon=True).start()

        while True:
            time.sleep(0.2)
            if self.boxes is None or self.scores is None or self.classes is None:
                time.sleep(1)
                continue

            for box, score, classification in zip(self.boxes, self.scores, self.classes):
                if score > self.threshold:
                    label = self.category_index[classification]['name']

                    if label == 'person':
                        connection.send((SOCKET_RECOGNITION_DETECTED + SOCKET_EOL).encode())
                        print('> [INFO] Person detected')
                        break
                    # print("==========\nlabel: {}\nscore: {}\nbox: {}".format(label, score, box))
