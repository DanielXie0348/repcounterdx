import cv2
from ultralytics import YOLO
from exercises import WorkoutCoach
import menu

# Initialize
model = YOLO('yolov8n-pose.pt')
cap = cv2.VideoCapture(0)
coach = WorkoutCoach()

print("Ready! Press 'c' for Curls, 's' for Squats, 'q' to Quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # 1. Check Menu for input
    choice = menu.get_user_choice()
    if choice == "quit": break
    if choice == "reset": coach.counter = 0
    if choice in ["curl", "squat"]:
        coach.set_mode(choice)

    # 2. Run AI Inference
    results = model(frame, stream=True, verbose=False)

    for r in results:
        # Standard YOLO skeleton drawing
        frame = r.plot()

        if r.keypoints is not None and len(r.keypoints.xy) > 0:
            # Extract [x, y] coordinates
            kpts = r.keypoints.xy[0].tolist()
            
            # 3. Ask Coach to process the workout
            count, stage = coach.process_workout(kpts)

            # 4. Display the HUD
            cv2.rectangle(frame, (0,0), (250,100), (0,0,0), -1) # Background box
            cv2.putText(frame, f"MODE: {coach.mode.upper()}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"REPS: {count}", (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("RepCounterDX", frame)

cap.release()
cv2.destroyAllWindows()