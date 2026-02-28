from .base import ExerciseBase
from calcs import calculate_angle

class PressTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 11: return self.counter, "Visible?"
        
        angle = calculate_angle(kpts[6], kpts[8], kpts[10])
        if angle < 60: self.stage = "down"
        if angle > 150 and self.stage == "down":
            self.stage = "up"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"