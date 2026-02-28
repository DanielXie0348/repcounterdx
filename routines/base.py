import time

class ExerciseBase:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.start_time = time.time()
        self.delay = 3.0

    def check_delay(self):
        elapsed = time.time() - self.start_time
        if elapsed < self.delay:
            return True, f"WAIT {int(self.delay - elapsed) + 1}"
        return False, None