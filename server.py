from flask import Flask, Response, jsonify, render_template, request
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

@app.route("/set_mode/<mode>")
def set_mode(mode):
    data = request.get_json(force = True)
    if mode in EXERCISE_MAP:
        with lock:
            state["mode"] = mode
            state["trackers"][mode] = EXERCISE_MAP[mode]()
            state["count"] = 0
            state["stage"] = "READY"
        return jsonify({"ok": True, "mode": mode})
    else:
        return jsonify({"status": "error", "message": "Invalid mode"}), 400

@app.route("/reset", methods=["POST"])
def reset():
    with lock:
        state["trackers"][state["mode"]] = EXERCISE_MAP[state["mode"]]()
        state["count"] = 0
        state["stage"] = "READY"
    return jsonify({"ok": True, "message": "State reset"}) 

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json(force=True)
    img_b64 = data.get("frame", "")

    # Decode the base64 frame from the browser
    try:
        img_bytes = base64.b64decode(img_b64)
        np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Empty frame")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Run YOLO
    results = model(frame, stream=False, verbose=False)

    count = state["count"]
    stage = state["stage"]

    for r in results:
        frame = r.plot(boxes=False, kpt_radius=3, kpt_line=True,
                       labels=False, probs=False)

        if r.keypoints is not None and len(r.keypoints.xy) > 0:
            points = r.keypoints.xy[0].tolist() # checks only first person detected, can be extended to multiple people if needed
            conf   = r.keypoints.conf[0].tolist()

            # checks confidence score which side is more visible to determine left vs right side of the body
            right_vis = conf[6] + conf[8] + conf[10]
            left_vis  = conf[5] + conf[7] + conf[9]
            active = list(points)
            if left_vis > right_vis:
                active[6]  = points[5]
                active[8]  = points[7]
                active[10] = points[9]
                active[12] = points[11]
                active[14] = points[13]
                active[16] = points[15]

            with lock:
                mode = state["mode"]
                count, stage = state["trackers"][mode].process(active)
                state["count"] = count
                state["stage"] = stage

    # Encode annotated frame back to base64 to send to browser
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    annotated_b64 = base64.b64encode(buf).decode("utf-8")

    return jsonify({
        "frame": annotated_b64,
        "mode":  state["mode"],
        "count": count,
        "stage": stage,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)