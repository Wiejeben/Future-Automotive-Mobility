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
        self.display = not ((not args["display"]) & (args["num_frames"] < 0))
        self.queue_input = None
        self.queue_output = None
        self.pool = None
        self.vs = None
        self.fps = None
        self.output = None

        self.start_queue(args["logger_debug"], args["queue_size"], args["num_workers"])
        self.start_video(args["input_device"])
        self.start_output(args["output"])

    def start_queue(self, debugger, size, workers):
        """
        Set the multiprocessing logger to debug if required.
        """

        if debugger:
            logger = multiprocessing.log_to_stderr()
            logger.setLevel(multiprocessing.SUBDEBUG)

        # Multiprocessing: Init input and output Queue and pool of workers
        self.queue_input = Queue(maxsize=size)
        self.queue_output = Queue(maxsize=size)
        self.pool = Pool(workers, worker, (self.queue_input, self.queue_output))

    def start_video(self, device):
        # created a threaded video stream and start the FPS counter
        self.vs = WebcamVideoStream(src=device).start()
        self.fps = FPS().start()

    def start_output(self, enabled):
        if enabled:
            self.output = cv2.VideoWriter(
                'outputs/{}.avi'.format(args["output_name"]),
                cv2.VideoWriter_fourcc(*'XVID'),
                self.vs.getFPS() / args["num_workers"],
                (self.vs.getWidth(), self.vs.getHeight())
            )

    def start(self):
        if self.display:
            print()
            print("=====================================================================")
            print("Starting video acquisition. Press 'q' (on the video windows) to stop.")
            print("=====================================================================")
            print()

        # Start reading and treating the video stream
        countFrame = 0
        while True:
            # Capture frame-by-frame
            ret, frame = self.vs.read()
            countFrame = countFrame + 1
            if ret:
                self.queue_input.put(frame)
                output_rgb = cv2.cvtColor(self.queue_output.get(), cv2.COLOR_RGB2BGR)

                # write the frame
                if self.output:
                    self.output.write(output_rgb)

                # Display the resulting frame
                if self.display:
                    cv2.imshow('frame', output_rgb)
                    self.fps.update()
                elif countFrame >= args["num_frames"]:
                    break

            else:
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        self.fps.stop()
        self.pool.terminate()
        self.vs.stop()
        if self.output:
            self.output.release()

        cv2.destroyAllWindows()

def realtime(args):
    app = Realtime(args)
    app.start()
