import os
import cv2
import time
import argparse
import multiprocessing
import numpy as np
import tensorflow as tf

from app.views.utils.app_utils import FPS, WebcamVideoStream
from multiprocessing import Queue, Pool
from app.views.object_detection.utils import label_map_util
from app.views.object_detection.utils import visualization_utils as vis_util
from app.__init__ import *

import sys

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.');

CWD_PATH = os.getcwd()

# Path to frozen detection graph. This is the actual model that is used for the object detection.
MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
PATH_TO_CKPT = os.path.join(CWD_PATH, 'app', 'views', 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(CWD_PATH, 'app', 'views', 'object_detection', 'data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# fork, knife, banana, bottle
track_objects = {48:0,49:0,52:0,44:0};
state_objects = {48:[0,0],49:[0,0],52:[0,0],44:[0,0]};

class VideoCamera(object):
    def __init__(self):
        #parser = argparse.ArgumentParser()
        #parser.add_argument('-src', '--source', dest='video_source', type=int,
        #                    default=0, help='Device index of the camera.')
        #parser.add_argument('-wd', '--width', dest='width', type=int,
        #                    default=480, help='Width of the frames in the video stream.')
        #parser.add_argument('-ht', '--height', dest='height', type=int,
        #                    default=360, help='Height of the frames in the video stream.')
        #parser.add_argument('-num-w', '--num-workers', dest='num_workers', type=int,
        #                    default=2, help='Number of workers.')
        #parser.add_argument('-q-size', '--queue-size', dest='queue_size', type=int,
        #                    default=5, help='Size of the queue.')
        #args = parser.parse_args()
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(multiprocessing.SUBDEBUG)
        self.input_q = Queue(maxsize=5)
        self.output_q = Queue(maxsize=5)
        pool = Pool(1, worker, (self.input_q, self.output_q))
        self.video_capture = WebcamVideoStream(src=0,
                                          width=800,
                                          height=600).start()
        self.fps = FPS().start()

    def get_frame(self):
        frame = self.video_capture.read()
        self.input_q.put(frame)
        t = time.time()
        output_rgb = cv2.cvtColor(self.output_q.get()[0], cv2.COLOR_RGB2BGR)
        self.fps.update()
        print('[INFO] elapsed time: {:.2f}'.format(time.time() - t));
        ret, jpeg = cv2.imencode('.jpg', output_rgb)
        return jpeg.tobytes()

def detect_objects(image_np, sess, detection_graph):
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    # Each box represents a part of the image where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')    
    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})
    detect_id = classes[0][0];
    detect_box = boxes[0][0];
    if detect_id in track_objects:
        ymin, xmin, ymax, xmax = detect_box;
        # update old location:
        state_objects[detect_id][0] = state_objects[detect_id][1];
        # update new location:
        if ( np.mean([ymax,ymin]) < 0.5 ) : # top
            state_objects[detect_id][1] = 1;
        else: # bottom
            state_objects[detect_id][1] = 0;
        if (state_objects[detect_id][0] == 0) and (state_objects[detect_id][1] == 1):
            track_objects[detect_id] = track_objects[detect_id] + 1;
            print(str(detect_id) + ' is taken. track_objects= ' + str(track_objects[detect_id]) );
            socketio.emit('calculate', {'data':track_objects[detect_id]});
        elif (state_objects[detect_id][0] == 1) and (state_objects[detect_id][1] == 0):
            track_objects[detect_id] = track_objects[detect_id] - 1;
            print(str(detect_id) + ' is returned. track_objects= ' + str(track_objects[detect_id]) );
            socketio.emit('calculate', {'data':track_objects[detect_id]});
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8)
    return [image_np, track_objects]

def worker(input_q, output_q):
    # Load a (frozen) Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        sess = tf.Session(graph=detection_graph)    
    fps = FPS().start()
    while True:
        fps.update()
        frame = input_q.get()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output_q.put(detect_objects(frame_rgb, sess, detection_graph))
    fps.stop()
    sess.close()
