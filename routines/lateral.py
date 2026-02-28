from .base import ExerciseBase
from calcs import calculate_angle

class LateralTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 13: return self.counter, "Visible?"
        
        angle = calculate_angle(kpts[12], kpts[6], kpts[8])
        if angle < 30: self.stage = "down"
        if angle > 80 and self.stage == "down":
            self.stage = "up"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"