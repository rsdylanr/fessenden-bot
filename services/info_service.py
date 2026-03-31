import discord
from datetime import datetime

class InfoService:
    def __init__(self, bot):
        self.bot = bot

    def get_timestamp(self):
        """Standardized Fessenden Timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def format_bytes(self, size):
        """Converts raw bytes to human-readable format (KB, MB, GB)."""
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{round(size, 2)} {power_labels[n]}B"

    async def get_member_data(self, guild, user_id):
        """Safely retrieves a member from a guild without crashing."""
        member = guild.get_member(user_id)
        if not member:
            try:
                member = await guild.fetch_member(user_id)
            except:
                return None
        return member
