from utils.app_utils import *
from utils.objDet_utils import *
import multiprocessing
from multiprocessing import Queue, Pool
import cv2


class Realtime:
    """
    Read and apply object detection to input video stream
    """

    def __init__(self, args):
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
        self.start_stream(args["input_device"])

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

    def start_stream(self, device):
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
        """
        Capture and process video frame.
        """

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False

        # Capture frame-by-frame
        ret, frame = self.vs.read()

        # No new frame, try again
        if not ret:
            return True

        # Place frame in queue
        self.queue_input.put(frame)

        # Display the resulting frame
        if self.display:
            cv2.imshow('frame', cv2.cvtColor(self.queue_output.get(), cv2.COLOR_RGB2BGR))
            self.fps.update()

        return True

    def destroy(self):
        """
        Stop threads and hide OpenCV frame.
        """

        # When everything done, release the capture
        self.fps.stop()
        self.pool.terminate()
        self.vs.stop()

        cv2.destroyAllWindows()
