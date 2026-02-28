import cv2

def get_user_choice():
    """Listens for key presses and returns the mode string."""
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('c'):
        return "curl"
    elif key == ord('s'):
        return "squat"
    elif key == ord('r'):
        return "reset"
    elif key == ord('q'):
        return "quit"
    return None