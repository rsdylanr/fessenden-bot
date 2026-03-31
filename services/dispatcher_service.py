import asyncio
import logging

class DispatcherService:
    """
    Fessenden Framework: Central Orchestrator
    Handles: Filter, Context Analysis (# $ *), and Command Execution.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("fessenden.dispatcher")

    async def handle_message(self, message):
        """
        Processes every incoming message to determine if it should 
        be filtered or passed to the command processor.
        """
        # 1. GATEKEEPER: Ignore other bots to prevent loops
        if message.author.bot:
            return

        # 2. SENSOR: Record activity for the game channel heartbeat
        # This allows your stats_service to track which channels are active.
        try:
            self.bot.sensor.record_activity(message.channel.id)
            self.bot.stats.record_message(message.author.id)
        except Exception as e:
            print(f"⚠️ Sensor/Stats Error: {e}")

        # 3. ADMIN BYPASS: If you are an admin, skip filtering
        # This ensures the owner (you) never gets blocked from testing games.
        if message.author.guild_permissions.administrator:
            await self.bot.process_commands(message)
            return

        # 4. CONTEXT ANALYSIS: The '# $ *' Logic
        # Wrapped in a 2-second timeout so a slow AI/DB doesn't silence the bot.
        try:
            # Check if the message is Inappropriate
            result = await asyncio.wait_for(
                self.bot.context.analyze(message), 
                timeout=2.0
            )
            
            if result and result.get("verdict") == "INAPPROPRIATE":
                # Log the violation to your database
                await self.bot.context.log_violation(message, result)
                
                # Optional: Send a silent warning or just return
                # return (Stopping here prevents the !command from running)
                return 

        except asyncio.TimeoutError:
            # If analysis takes too long, we log it and let the command through
            print(f"🕒 Dispatcher: Context Analysis timed out for {message.author}. Bypassing.")
        except Exception as e:
            # If the context service crashes, we still want the bot to work
            print(f"❌ Dispatcher: Context Service Error: {e}")

        # 5. THE BRIDGE: Execute Commands
        # This is the final step that makes !country, !sync, etc., actually work.
        await self.bot.process_commands(message)

# Note: Ensure this is the ONLY DispatcherService class in your project.
