from flask import Flask, render_template, jsonify, Response, request
from app.views.camera import VideoCamera
# from flask import Flask, render_template, jsonify, Response
# from app.views.object_detection_app import VideoCamera

from app import app
import random
import requests
from bs4 import BeautifulSoup
from threading import Thread
# from flask_socketio import SocketIO, emit         

class MyThread(Thread):
    def __init__(self, frame):
        ''' Constructor. '''
 
        Thread.__init__(self)
        self.frame = frame
 
 
    def run(self):
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/stream')
def stream():
    return render_template('stream.html', title='Smart Stream')

@app.route('/camera')
def camera():
    return render_template('camera.html', title='Camera')

def gen(camera):
    # myThreadOb1 = MyThread(frame)
    # myThreadOb1.start();
    # myThreadOb1.join();
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')