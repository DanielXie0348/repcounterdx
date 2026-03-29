from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from ultralytics import YOLO
import numpy as np
import cv2
import base64
import threading

from routines import (
    CurlTracker, SquatTracker, LateralRaiseTracker, ShoulderPressTracker,
    PushUpTracker, LungeTracker, TricepExtensionTracker, CalfRaiseTracker,
)

app = Flask(__name__)
print(app.template_folder)
CORS(app)
model = YOLO('yolov8n-pose.pt')

EXERCISE_MAP = {
    "curl":    {"class": CurlTracker,           "name": "Bicep Curl",       "icon": "💪"},
    "squat":   {"class": SquatTracker,           "name": "Squat",            "icon": "🦵"},
    "lateral": {"class": LateralRaiseTracker,    "name": "Lateral Raise",    "icon": "🙌"},
    "press":   {"class": ShoulderPressTracker,   "name": "Shoulder Press",   "icon": "🏋️"},
    "pushup":  {"class": PushUpTracker,          "name": "Push-Up",          "icon": "⬇️"},
    "lunge":   {"class": LungeTracker,           "name": "Lunge",            "icon": "🚶"},
    "tricep":  {"class": TricepExtensionTracker, "name": "Tricep Extension", "icon": "💪"},
    "calf":    {"class": CalfRaiseTracker,       "name": "Calf Raise",       "icon": "🦶"},
}

lock = threading.Lock()
state = {
    "mode":     "curl",
    "trackers": {k: v["class"]() for k, v in EXERCISE_MAP.items()},
    "count":    0,
    "stage":    "READY",
    "history":  [],
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/exercises", methods=["GET"])
def exercises():
    return jsonify({k: {"name": v["name"], "icon": v["icon"]} for k, v in EXERCISE_MAP.items()})


@app.route("/set_exercise", methods=["POST"])
def set_exercise():
    data = request.get_json(force=True)
    mode = data.get("mode", "")
    if mode not in EXERCISE_MAP:
        return jsonify({"error": "Invalid exercise"}), 400
    with lock:
        if state["count"] > 0:
            import time
            state["history"].append({
                "exercise": EXERCISE_MAP[state["mode"]]["name"],
                "reps": state["count"],
                "ts": time.time(),
            })
        state["mode"] = mode
        state["trackers"][mode] = EXERCISE_MAP[mode]["class"]()
        state["count"] = 0
        state["stage"] = "READY"
    return jsonify({"ok": True, "mode": mode})


@app.route("/reset", methods=["POST"])
def reset():
    with lock:
        state["trackers"][state["mode"]] = EXERCISE_MAP[state["mode"]]["class"]()
        state["count"] = 0
        state["stage"] = "READY"
    return jsonify({"ok": True})


@app.route("/history", methods=["GET"])
def history():
    with lock:
        return jsonify({"history": state["history"]})


@app.route("/clear_history", methods=["POST"])
def clear_history():
    with lock:
        state["history"] = []
        state["count"] = 0
        state["stage"] = "READY"
    return jsonify({"ok": True})


@app.route("/process", methods=["POST"])
def process():
    data = request.get_json(force=True)
    img_b64 = data.get("frame", "")

    try:
        img_bytes = base64.b64decode(img_b64)
        np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Empty frame")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    results = model(frame, stream=False, verbose=False)
    count = state["count"]
    stage = state["stage"]
    detected = False

    for r in results:
        frame = r.plot(boxes=False, kpt_radius=4, kpt_line=True, labels=False, probs=False)
        if r.keypoints is not None and len(r.keypoints.xy) > 0:
            detected = True
            points = r.keypoints.xy[0].tolist()
            conf   = r.keypoints.conf[0].tolist()
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

    if not detected:
        stage = "NO POSE"

    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 72])
    annotated_b64 = base64.b64encode(buf).decode("utf-8")

    with lock:
        mode = state["mode"]

    return jsonify({
        "frame":    annotated_b64,
        "mode":     mode,
        "modeName": EXERCISE_MAP[mode]["name"],
        "count":    count,
        "stage":    stage,
        "detected": detected,
    })

@app.route("/save_session", methods=["POST"])
def save_session():
    data = request.get_json(force=True)
    with lock:
        state["history"].append({
            "exercise": data.get("exercise", ""),
            "reps": data.get("reps", 0),
            "ts": data.get("ts", 0),
            "feedback": data.get("feedback", ""),
        })
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)