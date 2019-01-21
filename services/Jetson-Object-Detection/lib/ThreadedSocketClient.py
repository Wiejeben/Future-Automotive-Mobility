import time
from builtins import zip
from threading import Thread
import numpy as np


class ThreadedSocketClient(Thread):

    def __init__(self, category_index, min_score, interval=20):
        Thread.__init__(self)
        self.daemon = True
        self.category_index = category_index
        self.min_score = min_score
        self.interval = interval

        self.boxes = None
        self.scores = None
        self.classes = None

    def run(self):
        current_frames = 0
        while True:
            # Limit to 5 times per second
            time.sleep(0.1)
            if self.boxes is None or self.scores is None or self.classes is None:
                print('> Was none')
                continue

            current_frames += 1
            for box, score, classification in zip(
                    np.squeeze(self.boxes),
                    np.squeeze(self.scores),
                    np.squeeze(self.classes)
            ):
                if current_frames % self.interval == 0 and score > self.min_score:
                    label = self.category_index[classification]['name']
                    print("==========\nlabel: {}\nscore: {}\nbox: {}".format(label, score, box))
