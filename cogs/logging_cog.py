import discord
from discord.ext import commands
from datetime import datetime
import traceback

# 🔒 HARDCODED LOG CHANNEL ID HERE
# Replace this number with your actual channel ID (Right-click the channel -> Copy ID)
LOG_CHANNEL_ID = 1484163103905284187  

# ==========================================
# ⚙️ LOGGING SERVICE (Internal Helper)
# ==========================================
class LoggingService:
    def __init__(self, bot):
        self.bot = bot

    async def _send_log(self, title: str, description: str, color: discord.Color, fields: list = None):
        """Internal helper to send the embed to the hardcoded channel."""
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        
        if not channel:
            try:
                channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
            except:
                print(f"❌ Logging Error: Could not find channel ID {LOG_CHANNEL_ID}")
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


# ==========================================
# 🛠️ LOGGING COG (Event Listeners)
# ==========================================
class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = LoggingService(bot) # Binds the service to the cog

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ Hardcoded Logging Service is online! Channel ID: {LOG_CHANNEL_ID}")

    # 📝 1. Message Deleted Listener
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        fields = [
            ("Author", f"{message.author.mention} (`{message.author.id}`)"),
            ("Channel", message.channel.mention),
            ("Content", message.content or "*(No text content)*")
        ]
        await self.logger._send_log("⚠️ Message Deleted", f"A message was deleted in {message.channel.mention}", discord.Color.gold(), fields)

    # ✏️ 2. Message Edited Listener
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content:
            return

        fields = [
            ("Author", f"{before.author.mention} (`{before.author.id}`)"),
            ("Channel", before.channel.mention),
            ("Before", before.content),
            ("After", after.content)
        ]
        await self.logger._send_log("ℹ️ Message Edited", f"A message was modified in {before.channel.mention}", discord.Color.blue(), fields)

    # 🛑 3. Command Error Listener
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return

        error_trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        if len(error_trace) > 1000:
            error_trace = error_trace[:1000] + "\n... (Traceback cut short)"

        fields = [
            ("Command", f"`!{ctx.command.name}`" if ctx.command else "Unknown Command"),
            ("By User", ctx.author.mention),
            ("Traceback", f"```py\n{error_trace}\n```")
        ]
        await self.logger._send_log("🚨 Command Error Encountered", str(error), discord.Color.red(), fields)


async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
