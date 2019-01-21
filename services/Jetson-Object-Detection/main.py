from lib.config import load_config

object_detection = ObjectDetection(load_config())
object_detection.start()
