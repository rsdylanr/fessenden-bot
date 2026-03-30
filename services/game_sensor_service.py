import time

class GameSensorService:
    def __init__(self, bot):
        self.bot = bot
        # {channel_id: last_active_timestamp}
        self.activity_cache = {} 
        # Default: 10 minutes of silence stops the games
        self.inactivity_threshold = 600 

    def record_activity(self, channel_id: int):
        """Updates the 'Heartbeat' of a channel."""
        self.activity_cache[channel_id] = time.time()

    def is_channel_active(self, channel_id: int) -> bool:
        """Returns True if someone spoke within the threshold."""
        last_active = self.activity_cache.get(channel_id, 0)
        return (time.time() - last_active) < self.inactivity_threshold
