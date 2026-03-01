import cv2

def draw_ui(frame, mode, count, stage):
    h, w, _ = frame.shape

    bar_top = h - 40

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, bar_top), (w, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    cv2.line(frame, (0, bar_top), (w, bar_top), (0, 200, 100), 1)

    y = bar_top + 26

    if "WAIT" in str(stage) or "FAST" in str(stage):
        txt_color = (0, 0, 255)
    elif stage in ("up", "down"):
        txt_color = (0, 165, 255)
    else:
        txt_color = (0, 220, 100)

    cv2.putText(frame, mode.upper(), (10, y), cv2.FONT_HERSHEY_DUPLEX, 0.6, txt_color, 1)
    cv2.putText(frame, f"REPS: {count}", (80, y), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    return frame