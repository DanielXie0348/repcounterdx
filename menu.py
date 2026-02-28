import cv2

def get_user_choice():
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'): return "curl"
    if key == ord('s'): return "squat"
    if key == ord('l'): return "lateral"
    if key == ord('p'): return "press"
    if key == ord('q'): return "quit"
    return None