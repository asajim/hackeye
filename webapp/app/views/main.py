from flask import Flask, render_template, jsonify, Response
from app.views.camera import VideoCamera
from app import app
import random


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


@app.route('/monitor')
def monitor():
    return render_template('monitor.html', title='Patient Monitor')


@app.route('/knowledge')
def knowledge():
    return render_template('knowledge.html', title='Knowledge Base')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
