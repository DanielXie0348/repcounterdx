import cv2
from ultralytics import YOLO
import menu
from routines.curls import CurlTracker
from routines.squat import SquatTracker
from routines.lateral import LateralTracker
from routines.press import PressTracker

# 1. Config
model = YOLO('yolov8n-pose.pt')
cap = cv2.VideoCapture(0)

# Map names to Classes (not objects!)
EXERCISE_MAP = {
    "curl": CurlTracker,
    "squat": SquatTracker,
    "lateral": LateralTracker,
    "press": PressTracker
}

# Start with a default
current_mode = "curl"
trackers = {name: cls() for name, cls in EXERCISE_MAP.items()}

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    choice = menu.get_user_choice()
    if choice == "quit": break
    
    # RESET LOGIC: If user picks a new mode, we create a fresh object
    if choice in EXERCISE_MAP:
        current_mode = choice
        trackers[current_mode] = EXERCISE_MAP[current_mode]() # Resets timer/counter

    results = model(frame, stream=True, verbose=False)

    for r in results:
        frame = r.plot()
        if r.keypoints is not None and len(r.keypoints.xy) > 0:
            kpts = r.keypoints.xy[0].tolist()
            
            # Process the specific tracker
            count, stage = trackers[current_mode].process(kpts)

            # UI Bar
            h, w, _ = frame.shape
            cv2.rectangle(frame, (0, h-80), (w, h), (40, 40, 40), -1)
            
            # Change color if waiting
            txt_color = (0, 0, 255) if "WAIT" in str(stage) else (0, 255, 0)
            
            cv2.putText(frame, f"{current_mode.upper()}: {count}", (20, h-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, txt_color, 2)
            cv2.putText(frame, f"STATUS: {stage}", (w-250, h-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    cv2.imshow("RepCounterDX", frame)

cap.release()
cv2.destroyAllWindows()

# Final Summary
print("\n--- WORKOUT COMPLETE ---")
for name, tracker in trackers.items():
    if tracker.counter > 0:
        print(f"{name.upper()}: {tracker.counter} reps")