class DispatcherService:
    def __init__(self, bot):
        self.bot = bot

    async def handle_message(self, message):
        # 1. Ignore bots (Safety first)
        if message.author.bot: 
            return

        # 2. Update Game Channel Heartbeat (For your sensor stats)
        self.bot.sensor.record_activity(message.channel.id)

        # 3. Admin Bypass (So you don't get filtered by your own bot)
        if message.author.guild_permissions.administrator:
            await self.bot.process_commands(message)
            return

        # 4. Context Analysis (# $ *)
        result = await self.bot.context.analyze(message)
        
        if result and result.get("verdict") == "INAPPROPRIATE":
            await self.bot.context.log_violation(message, result)
            return # 🛑 STOP here. Do not process the command.

        # 5. CRITICAL: The "Bridge"
        # If the message is clean, this makes !commands and /commands work.
        await self.bot.process_commands(message)
