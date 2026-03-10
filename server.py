from flask import Flask, Response, jsonify, render_template
from flask_cors import CORS
from ultralytics import YOLO
import numpy as np
import cv2
import base64
import threading
from routines.curls import CurlTracker
from routines.squat import SquatTracker
from routines.lateral import LateralTracker
from routines.press import PressTracker

app = Flask(__name__)
CORS(app)
model = YOLO('yolov8n-pose.pt')


EXERCISE_MAP = {
    "curl": CurlTracker,
    "squat": SquatTracker,
    "lateral": LateralTracker,
    "press": PressTracker
}

lock = threading.Lock()

state = {
    "mode":     "curl",
    "trackers": {name: cls() for name, cls in EXERCISE_MAP.items()},
    "count":    0,
    "stage":    "READY",
}

@app.route("/")
def index():
    return render_template("index.html")

