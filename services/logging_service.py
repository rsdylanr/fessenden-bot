import discord
from datetime import datetime

class LoggingService:
    def __init__(self, bot, log_channel_id: int=1484629417908109462):
        self.bot = bot
        self.log_channel_id = log_channel_id

    async def _send_log(self, title: str, description: str, color: discord.Color, fields: list = None):
        """Internal helper to send a beautiful embed to the log channel."""
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel:
            # If the bot hasn't cached the channel yet, try fetching it
            try:
                channel = await self.bot.fetch_channel(self.log_channel_id)
            except:
                print(f"❌ Logging Error: Could not find channel ID {self.log_channel_id}")
                return

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for name, value in fields:
                embed.add_field(name=name, value=value, inline=False)

        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"❌ Failed to send log to Discord: {e}")

    async def log_success(self, title: str, message: str, fields: list = None):
        await self._send_log(f"✅ {title}", message, discord.Color.green(), fields)

    async def log_warning(self, title: str, message: str, fields: list = None):
        await self._send_log(f"⚠️ {title}", message, discord.Color.gold(), fields)

    async def log_error(self, title: str, message: str, fields: list = None):
        await self._send_log(f"🚨 {title}", message, discord.Color.red(), fields)

    async def log_info(self, title: str, message: str, fields: list = None):
        await self._send_log(f"ℹ️ {title}", message, discord.Color.blue(), fields)
