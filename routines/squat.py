from .base import ExerciseBase
from calcs import calculate_angle

class SquatTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 15: return self.counter, "Step Back!"
        
        angle = calculate_angle(kpts[12], kpts[14], kpts[16])
        if angle > 160: self.stage = "up"
        if angle < 90 and self.stage == "up":
            self.stage = "down"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"