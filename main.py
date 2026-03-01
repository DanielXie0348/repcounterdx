import cv2
from ultralytics import YOLO
import menu
import graphics
from routines.curls import CurlTracker 
from routines.squat import SquatTracker
from routines.lateral import LateralTracker
from routines.press import PressTracker

# 1. Setup
model = YOLO('yolov8n-pose.pt')
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cv2.namedWindow("RepCounterDX", cv2.WINDOW_NORMAL)
cv2.resizeWindow("RepCounterDX", 1280, 720)

EXERCISE_MAP = {
    "curl": CurlTracker,
    "squat": SquatTracker,
    "lateral": LateralTracker,
    "press": PressTracker
}

current_mode = "curl"
trackers = {name: cls() for name, cls in EXERCISE_MAP.items()}
last_print = ""

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # 2. Input
    choice = menu.get_user_choice()
    if choice == "quit": break
    if choice in EXERCISE_MAP:
        current_mode = choice
        trackers[current_mode] = EXERCISE_MAP[current_mode]()

    # 3. AI Inference
    results = model(frame, stream=True, verbose=False)

    for r in results:
        frame = r.plot(boxes=False, kpt_radius=2, kpt_line=True, labels=False, probs=False)

        if r.keypoints is not None and len(r.keypoints.xy) > 0:
            points = r.keypoints.xy[0].tolist()
            conf = r.keypoints.conf[0].tolist()

            # Side Detection
            right_vis = conf[6] + conf[8] + conf[10]
            left_vis = conf[5] + conf[7] + conf[9]

            active_kpts = points
            if left_vis > right_vis:
                active_kpts[6], active_kpts[8], active_kpts[10] = points[5], points[7], points[9]

            # 4. Logic Processing
            count, stage = trackers[current_mode].process(active_kpts)

            # Only print when something changes
            msg = f"{current_mode.upper()}: {count} | {stage}"
            if msg != last_print:
                print(msg)
                last_print = msg

            # 5. UI
            frame = graphics.draw_ui(frame, current_mode, count, stage)

    frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_LINEAR)
    cv2.imshow("RepCounterDX", frame)

cap.release()
cv2.destroyAllWindows()