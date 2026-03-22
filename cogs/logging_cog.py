import discord
from discord.ext import commands
import traceback

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 📝 1. Message Deleted
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        fields = [
            ("Author", f"{message.author.mention} (`{message.author.id}`)"),
            ("Channel", message.channel.mention),
            ("Content", message.content or "*(No text content, likely an image or embed)*")
        ]
        await self.bot.logger.log_warning("Message Deleted", f"A message was deleted in {message.channel.mention}", fields)

    # ✏️ 2. Message Edited
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
        await self.bot.logger.log_info("Message Edited", f"A message was modified in {before.channel.mention}", fields)

    # 📥 3. Member Joined
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        fields = [("Account Created", member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"))]
        await self.bot.logger.log_success("Member Joined", f"{member.mention} has joined the server.", fields)

    # 📤 4. Member Left
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.bot.logger.log_warning("Member Left", f"{member.name} (`{member.id}`) has left the server.")

    # 🛑 5. Command Errors (If a command crashes!)
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        # Ignore CommandNotFound errors to prevent spamming logs
        if isinstance(error, commands.CommandNotFound):
            return

        error_trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        
        # Discord Embeds cannot hold more than 1024 characters per field, so we cut it if it's too long
        if len(error_trace) > 1000:
            error_trace = error_trace[:1000] + "\n... (Traceback cut short)"

        fields = [
            ("Command", f"`!{ctx.command.name}`" if ctx.command else "Unknown Command"),
            ("By User", ctx.author.mention),
            ("Traceback", f"```py\n{error_trace}\n```")
        ]
        await self.bot.logger.log_error("Command Error Encountered", str(error), fields)


async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
