from calcs import calculate_angle

class WorkoutCoach:
    def __init__(self):
        self.counter = 0
        self.stage = None # Tracks if you are 'up' or 'down'
        self.mode = "None"

    def set_mode(self, new_mode):
        if self.mode != new_mode:
            self.mode = new_mode
            self.counter = 0 # Reset count when switching exercises
            self.stage = None

    def process_workout(self, kpts):
        """The Master Switch that main.py calls."""
        if self.mode == "curl":
            return self._do_curl(kpts)
        elif self.mode == "squat":
            return self._do_squat(kpts)
        return 0, "Select Exercise"

    def _do_curl(self, kpts):
        # IDs: Shoulder(6), Elbow(8), Wrist(10)
        angle = calculate_angle(kpts[6], kpts[8], kpts[10])
        
        if angle > 160:
            self.stage = "down"
        if angle < 30 and self.stage == "down":
            self.stage = "up"
            self.counter += 1
        return self.counter, self.stage

    def _do_squat(self, kpts):
        # IDs: Hip(12), Knee(14), Ankle(16)
        angle = calculate_angle(kpts[12], kpts[14], kpts[16])
        
        if angle > 160:
            self.stage = "up"
        if angle < 90 and self.stage == "up":
            self.stage = "down"
            self.counter += 1
        return self.counter, self.stage