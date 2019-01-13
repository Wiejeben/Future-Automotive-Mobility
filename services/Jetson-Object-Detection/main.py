import numpy as np
import os
import tensorflow as tf
import copy
import yaml
import cv2
import time
from lib import FPS, WebcamVideoStream, SessionWorker

from tensorflow.core.framework import graph_pb2
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

## LOAD CONFIG PARAMS ##
if (os.path.isfile('config.yml')):
    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
else:
    with open("config.sample.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

video_input = cfg['video_input']
visualize = cfg['visualize']
vis_text = cfg['vis_text']
max_frames = cfg['max_frames']
width = cfg['width']
height = cfg['height']
fps_interval = cfg['fps_interval']
allow_memory_growth = cfg['allow_memory_growth']
det_interval = cfg['det_interval']
det_th = cfg['det_th']
model_name = cfg['model_name']
model_path = cfg['model_path']
label_path = cfg['label_path']
num_classes = cfg['num_classes']
split_model = cfg['split_model']
log_device = cfg['log_device']
ssd_shape = cfg['ssd_shape']


class ObjectDetection:
    # helper function for split model
    def __init__(self):
        self.video_stream = None
        self.fps = None
        self.cpu_worker = None
        self.gpu_worker = None
        self.cur_frames = 0

    def start(self):
        graph = self.load_frozenmodel()
        category = self.load_labelmap()
        self.detection(graph, category)

    def load_frozenmodel(self):
        """Load a (frozen) Tensorflow model into memory."""
        print('> Loading frozen model into memory')
        if not split_model:
            detection_graph = tf.Graph()
            with detection_graph.as_default():
                od_graph_def = tf.GraphDef()
                with tf.gfile.GFile(model_path, 'rb') as fid:
                    serialized_graph = fid.read()
                    od_graph_def.ParseFromString(serialized_graph)
                    tf.import_graph_def(od_graph_def, name='')
            return detection_graph

        else:
            # load a frozen Model and split it into GPU and CPU graphs
            # Hardcoded for ssd_mobilenet
            input_graph = tf.Graph()
            with tf.Session(graph=input_graph):
                if ssd_shape == 600:
                    shape = 7326
                else:
                    shape = 1917
                tf.placeholder(tf.float32, shape=(None, shape, num_classes), name="Postprocessor/convert_scores")
                tf.placeholder(tf.float32, shape=(None, shape, 1, 4), name="Postprocessor/ExpandDims_1")
                for node in input_graph.as_graph_def().node:
                    if node.name == "Postprocessor/convert_scores":
                        score_def = node
                    if node.name == "Postprocessor/ExpandDims_1":
                        expand_def = node

            detection_graph = tf.Graph()
            with detection_graph.as_default():
                od_graph_def = tf.GraphDef()
                with tf.gfile.GFile(model_path, 'rb') as fid:
                    serialized_graph = fid.read()
                    od_graph_def.ParseFromString(serialized_graph)
                    dest_nodes = ['Postprocessor/convert_scores', 'Postprocessor/ExpandDims_1']

                    edges = {}
                    name_to_node_map = {}
                    node_seq = {}
                    seq = 0
                    for node in od_graph_def.node:
                        n = self._node_name(node.name)
                        name_to_node_map[n] = node
                        edges[n] = [self._node_name(x) for x in node.input]
                        node_seq[n] = seq
                        seq += 1
                    for d in dest_nodes:
                        assert d in name_to_node_map, "%s is not in graph" % d

                    nodes_to_keep = set()
                    next_to_visit = dest_nodes[:]

                    while next_to_visit:
                        n = next_to_visit[0]
                        del next_to_visit[0]
                        if n in nodes_to_keep: continue
                        nodes_to_keep.add(n)
                        next_to_visit += edges[n]

                    nodes_to_keep_list = sorted(list(nodes_to_keep), key=lambda n: node_seq[n])
                    nodes_to_remove = set()

                    for n in node_seq:
                        if n in nodes_to_keep_list: continue
                        nodes_to_remove.add(n)
                    nodes_to_remove_list = sorted(list(nodes_to_remove), key=lambda n: node_seq[n])

                    keep = graph_pb2.GraphDef()
                    for n in nodes_to_keep_list:
                        keep.node.extend([copy.deepcopy(name_to_node_map[n])])

                    remove = graph_pb2.GraphDef()
                    remove.node.extend([score_def])
                    remove.node.extend([expand_def])
                    for n in nodes_to_remove_list:
                        remove.node.extend([copy.deepcopy(name_to_node_map[n])])

                    with tf.device('/gpu:0'):
                        tf.import_graph_def(keep, name='')
                    with tf.device('/cpu:0'):
                        tf.import_graph_def(remove, name='')

            return detection_graph

    @staticmethod
    def load_labelmap():
        print('> Loading label map')
        label_map = label_map_util.load_labelmap(label_path)
        categories = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=num_classes, use_display_name=True
        )
        category_index = label_map_util.create_category_index(categories)
        return category_index

    def detection(self, detection_graph, category_index):
        print("> Building Graph")
        # Session Config: allow seperate GPU/CPU adressing and limit memory allocation
        config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=log_device)
        config.gpu_options.per_process_gpu_memory_fraction = 0.8
        config.gpu_options.allow_growth = allow_memory_growth

        with detection_graph.as_default():
            with tf.Session(graph=detection_graph, config=config) as sess:
                # Define Input and Ouput tensors
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
                detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                if split_model:
                    score_out = detection_graph.get_tensor_by_name('Postprocessor/convert_scores:0')
                    expand_out = detection_graph.get_tensor_by_name('Postprocessor/ExpandDims_1:0')
                    score_in = detection_graph.get_tensor_by_name('Postprocessor/convert_scores_1:0')
                    expand_in = detection_graph.get_tensor_by_name('Postprocessor/ExpandDims_1_1:0')
                    # Threading
                    self.gpu_worker = SessionWorker("GPU", detection_graph, config)
                    self.cpu_worker = SessionWorker("CPU", detection_graph, config)
                    gpu_opts = [score_out, expand_out]
                    cpu_opts = [detection_boxes, detection_scores, detection_classes, num_detections]
                    gpu_counter = 0
                    cpu_counter = 0
                # Start Video Stream and FPS calculation
                self.fps = FPS(fps_interval).start()
                self.video_stream = WebcamVideoStream(video_input, width, height).start()

                print("> Press 'q' to Exit")
                print('> Starting Detection')
                while self.video_stream.isActive():
                    # actual Detection
                    if split_model:
                        # split model in seperate gpu and cpu session threads
                        if self.gpu_worker.is_sess_empty():
                            # read video frame, expand dimensions and convert to rgb
                            image = self.video_stream.read()
                            image_expanded = np.expand_dims(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), axis=0)
                            # put new queue
                            gpu_feeds = {image_tensor: image_expanded}
                            if visualize:
                                gpu_extras = image  # for visualization frame
                            else:
                                gpu_extras = None
                            self.gpu_worker.put_sess_queue(gpu_opts, gpu_feeds, gpu_extras)

                        g = self.gpu_worker.get_result_queue()
                        if g is None:
                            # gpu thread has no output queue. ok skip, let's check cpu thread.
                            gpu_counter += 1
                        else:
                            # gpu thread has output queue.
                            gpu_counter = 0
                            score, expand, image = g["results"][0], g["results"][1], g["extras"]

                            if self.cpu_worker.is_sess_empty():
                                # When cpu thread has no next queue, put new queue.
                                # else, drop gpu queue.
                                cpu_feeds = {score_in: score, expand_in: expand}
                                cpu_extras = image
                                self.cpu_worker.put_sess_queue(cpu_opts, cpu_feeds, cpu_extras)

                        c = self.cpu_worker.get_result_queue()
                        if c is None:
                            # cpu thread has no output queue. ok, nothing to do. continue
                            cpu_counter += 1
                            time.sleep(0.005)
                            continue  # If CPU RESULT has not been set yet, no fps update
                        else:
                            cpu_counter = 0
                            boxes, scores, classes, num, image = c["results"][0], c["results"][1], c["results"][2], \
                                                                 c["results"][3], c["extras"]
                    else:
                        # default session
                        image = self.video_stream.read()
                        image_expanded = np.expand_dims(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), axis=0)
                        boxes, scores, classes, num = sess.run(
                            [detection_boxes, detection_scores, detection_classes, num_detections],
                            feed_dict={image_tensor: image_expanded})

                    # Visualization of the results of a detection.
                    if visualize:
                        vis_util.visualize_boxes_and_labels_on_image_array(
                            image,
                            np.squeeze(boxes),
                            np.squeeze(classes).astype(np.int32),
                            np.squeeze(scores),
                            category_index,
                            use_normalized_coordinates=True,
                            line_thickness=4)
                        if vis_text:
                            cv2.putText(image, "fps: {}".format(fps.fps_local()), (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (77, 255, 9), 2)
                        cv2.imshow('object_detection', image)
                        # Exit Option
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                    self.cur_frames += 1
                    for box, score, _class in zip(np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes)):
                        if self.cur_frames % det_interval == 0 and score > det_th:
                            label = category_index[_class]['name']
                            print("==========\nlabel: {}\nscore: {}\nbox: {}".format(label, score, box))

                    self.fps.update()

    @staticmethod
    def _node_name(n):
        if n.startswith("^"):
            return n[1:]
        else:
            return n.split(":")[0]

    def exit(self):
        """End everything"""
        if split_model:
            self.gpu_worker.stop()
            self.cpu_worker.stop()
        self.fps.stop()
        self.video_stream.stop()
        cv2.destroyAllWindows()
        print('> [INFO] elapsed time (total): {:.2f}'.format(self.fps.elapsed()))
        print('> [INFO] approx. FPS: {:.2f}'.format(self.fps.fps()))


if __name__ == '__main__':
    object_detection = ObjectDetection()
    object_detection.start()
