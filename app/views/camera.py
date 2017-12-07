# camera.py

import cv2

class VideoCamera(object):
    def __init__(self):
        # webcam
        self.video = cv2.VideoCapture(0)
        # self.video = cv2.VideoCapture('video.mp4');
        # camera = cv2.VideoCapture(0)
        # if not camera.isOpened():
        #     raise RuntimeError('Could not start camera.')
        # styles = Styles() # this loads lots of stuff in GPU memory
        # current_style = 'la_muse'

        # while True:
        #     # read current frame
        #     _, frame = camera.read()
        #      # this does some (heavy) GPU computation
        #     frame = styles.convert_to_style(frame[:, :, ::-1], current_style)[:, :, ::-1]
        #     frame = cv2.resize(frame, (640, 480))
        #     frame = cv2.imencode('.jpg', frame)[1].tobytes()
        #     # encode as a jpeg image and return it
        #     yield frame
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()