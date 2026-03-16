class EventService:
    def __init__(self):
        self.is_active = False
        self.event_name = "General Event"
        self.participation_reward = 1
        
        # Attendance Logic
        self.attendance_data = {} # {user_id: minutes_present}
        self.total_ticks = 0
        
        # Roast Logic
        self.has_gone = set() # Set of user_ids who finished a match

    def start_tracking(self, name: str = "General Event", reward: int = 1):
        """Resets and starts the clock for a new event."""
        self.is_active = True
        self.event_name = name
        self.participation_reward = reward
        self.attendance_data = {}
        self.total_ticks = 0
        self.has_gone.clear()
        print(f"⏰ Attendance tracking started for: {name}")

    def record_tick(self, member_ids: list):
        """Records 1 minute of presence for a list of users."""
        if not self.is_active:
            return
        
        self.total_ticks += 1
        for uid in member_ids:
            self.attendance_data[uid] = self.attendance_data.get(uid, 0) + 1

    def get_eligible_users(self):
        """Returns list of user_ids who stayed for >= 50% of the duration."""
        if self.total_ticks == 0:
            return []
            
        threshold = self.total_ticks / 2
        eligible = [
            uid for uid, ticks in self.attendance_data.items() 
            if ticks >= threshold
        ]
        return eligible

    def stop_tracking(self):
        """Closes the event state."""
        self.is_active = False