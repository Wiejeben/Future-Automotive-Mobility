import datetime


class FPS:
    def __init__(self, interval):
        self._glob_start = None
        self._glob_end = None
        self._glob_numFrames = 0
        self._local_start = None
        self._local_numFrames = 0
        self._interval = interval
        self.curr_local_elapsed = None
        self.first = False

    def start(self):
        self._glob_start = datetime.datetime.now()
        self._local_start = self._glob_start
        return self

    def stop(self):
        self._glob_end = datetime.datetime.now()

    def update(self):
        self.first = True
        curr_time = datetime.datetime.now()
        self.curr_local_elapsed = (curr_time - self._local_start).total_seconds()
        self._glob_numFrames += 1
        self._local_numFrames += 1
        if self.curr_local_elapsed > self._interval:
            print("> FPS: {}".format(self.fps_local()))
            self._local_numFrames = 0
            self._local_start = curr_time

    def elapsed(self):
        return (self._glob_end - self._glob_start).total_seconds()

    def fps(self):
        return self._glob_numFrames / self.elapsed()

    def fps_local(self):
        if self.first:
            return round(self._local_numFrames / self.curr_local_elapsed, 1)
        else:
            return 0.0
