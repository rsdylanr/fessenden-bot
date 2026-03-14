import time

class EventService:
    def __init__(self):
        self.is_active = False
        self.start_time = 0
        self.has_gone = set()
        self.attendance = {} # {user_id: [total_seconds, last_check]}

    def start_event(self):
        self.is_active = True
        self.start_time = time.time()
        self.has_gone.clear()

    def end_event(self):
        self.is_active = False
        duration = time.time() - self.start_time
        # Logic to return list of users who hit 50% time
        winners = [uid for uid, (secs, _) in self.attendance.items() if secs >= (duration / 2)]
        self.attendance.clear()
        return winners