class DispatcherService:
    def __init__(self, bot):
        self.bot = bot

    async def handle_message(self, message):
        # 1. Ignore bots
        if message.author.bot: 
            return

        # 2. Run your # $ * Analysis
        result = await self.bot.context.analyze(message)
        
        if result and result["verdict"] == "INAPPROPRIATE":
            await self.bot.context.log_violation(message, result)
            return # Stop here so the command doesn't run

        # 3. CRITICAL: This is what makes !commands work
        await self.bot.process_commands(message)
