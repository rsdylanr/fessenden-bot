import time
import discord

class GameSensorService:
    def __init__(self, bot):
        self.bot = bot
        self.activity_cache = {} # {channel_id: last_active_timestamp}
        self.inactivity_threshold = 600 # 10 minutes in seconds

    def record_activity(self, channel_id: int):
        """Called by the dispatcher every time a human speaks."""
        self.activity_cache[channel_id] = time.time()

    def is_channel_active(self, channel_id: int) -> bool:
        """Checks if the channel has had a message within the threshold."""
        last_active = self.activity_cache.get(channel_id, 0)
        return (time.time() - last_active) < self.inactivity_threshold

    def set_threshold(self, minutes: int):
        self.inactivity_threshold = minutes * 60
