from __future__ import print_function
from utils.app_utils import *
from utils.objDet_utils import *
import multiprocessing
from multiprocessing import Queue, Pool
import cv2


class Realtime:
    """
    Read and apply object detection to input real time stream (webcam)
    """

    def __init__(self, args):
        self.args = args
        self.display = args["display"] == 1
        self.queue_input = None
        self.queue_output = None
        self.pool = None
        self.vs = None
        self.fps = None

        self.start_queue(
            args["logger_debug"],
            args["queue_size"],
            args["num_workers"]
        )
        self.start_video(args["input_device"])

    def start_queue(self, debugger, size, workers):
        """
        Starts processing queue.
        """

        if debugger:
            logger = multiprocessing.log_to_stderr()
            logger.setLevel(multiprocessing.SUBDEBUG)

        self.queue_input = Queue(maxsize=size)
        self.queue_output = Queue(maxsize=size)
        self.pool = Pool(workers, worker, (self.queue_input, self.queue_output))

    def start_video(self, device):
        """
        Create a threaded video stream and start the FPS counter.
        """

        self.vs = WebcamVideoStream(src=device).start()
        self.fps = FPS().start()

    def start(self):
        """
        Start processing video feed.
        """

        if self.display:
            print()
            print("=====================================================================")
            print("Starting video acquisition. Press 'q' (on the video windows) to stop.")
            print("=====================================================================")
            print()

        # Start reading and treating the video stream
        running = True
        while running:
            running = self.capture()

        self.destroy()

    def capture(self):
        # Capture frame-by-frame
        ret, frame = self.vs.read()

        if not ret:
            return True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False

        self.queue_input.put(frame)
        output_rgb = cv2.cvtColor(self.queue_output.get(), cv2.COLOR_RGB2BGR)

        # Display the resulting frame
        if self.display:
            cv2.imshow('frame', output_rgb)
            self.fps.update()

        return True

    def destroy(self):
        # When everything done, release the capture
        self.fps.stop()
        self.pool.terminate()
        self.vs.stop()

        cv2.destroyAllWindows()
