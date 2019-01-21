from lib.config import load_config
from lib.ObjectDetection import ObjectDetection

object_detection = ObjectDetection(load_config())
object_detection.start()
