from .base import ExerciseBase
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from calcs import calculate_angle


class CurlTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 11: return self.counter, "STEP CLOSER"
        angle = calculate_angle(kpts[6], kpts[8], kpts[10])
        if angle > 160: self.stage = "down"
        if angle < 35 and self.stage == "down":
            self.stage = "up"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"


class SquatTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 17: return self.counter, "STEP BACK"
        angle = calculate_angle(kpts[12], kpts[14], kpts[16])
        if angle > 160: self.stage = "up"
        if angle < 90 and self.stage == "up":
            self.stage = "down"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"


class LateralRaiseTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 13: return self.counter, "STEP CLOSER"
        angle = calculate_angle(kpts[12], kpts[6], kpts[8])
        if angle < 30: self.stage = "down"
        if angle > 80 and self.stage == "down":
            self.stage = "up"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"


class ShoulderPressTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 11: return self.counter, "STEP CLOSER"
        angle = calculate_angle(kpts[6], kpts[8], kpts[10])
        if angle < 60: self.stage = "down"
        if angle > 150 and self.stage == "down":
            self.stage = "up"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"


class PushUpTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 11: return self.counter, "STEP BACK"
        angle = calculate_angle(kpts[6], kpts[8], kpts[10])
        if angle > 155: self.stage = "up"
        if angle < 75 and self.stage == "up":
            self.stage = "down"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"


class LungeTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 17: return self.counter, "STEP BACK"
        angle = calculate_angle(kpts[12], kpts[14], kpts[16])
        if angle > 155: self.stage = "up"
        if angle < 95 and self.stage == "up":
            self.stage = "down"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"


class TricepExtensionTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 11: return self.counter, "STEP CLOSER"
        angle = calculate_angle(kpts[6], kpts[8], kpts[10])
        if angle < 50: self.stage = "down"
        if angle > 155 and self.stage == "down":
            self.stage = "up"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"


class CalfRaiseTracker(ExerciseBase):
    def process(self, kpts):
        is_waiting, msg = self.check_delay()
        if is_waiting: return 0, msg
        if len(kpts) < 17: return self.counter, "STEP BACK"
        hip_y = kpts[12][1]
        ankle_y = kpts[16][1]
        ratio = hip_y / (ankle_y + 1)
        if ratio > 0.88: self.stage = "down"
        if ratio < 0.84 and self.stage == "down":
            self.stage = "up"; self.counter += 1
        return self.counter, self.stage if self.stage else "READY"