import asyncio
import logging

class DispatcherService:
    """
    Fessenden Framework: Central Orchestrator
    Updated to leverage the 900-function Parsing Engine.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("fessenden.dispatcher")

    async def handle_message(self, message):
        # 1. GATEKEEPER: Ignore bots
        if message.author.bot:
            return

        # --- 🛡️ PHASE 0: THE PURIFICATION LAYER ---
        # Before we do ANYTHING, we run the message through the 900-function engine.
        try:
            # This handles ZWSP, Bidi-Overrides, and NFC Normalization
            purified = self.bot.parsing.finalize_immutable_context(message.content)
            
            # Security Check: If the parser flags a nesting or Bidi threat, drop it.
            if not purified["security"]["is_bidi_safe"] or not purified["security"]["is_nesting_safe"]:
                self.logger.warning(f"🛡️ Blocked malicious input attempt from {message.author} (ID: {message.author.id})")
                return

            # Attach the purified data to the message object. 
            # Now ANY cog can access message.purified['structure']['arguments']
            message.purified = purified
            
        except Exception as e:
            self.logger.error(f"❌ Critical Parsing Error: {e}")
            # Fallback: if the parser fails, we continue with raw content for safety
            message.purified = None

        # 2. SENSOR: Record activity
        try:
            self.bot.sensor.record_activity(message.channel.id)
            self.bot.stats.record_message(message.author.id)
        except Exception as e:
            self.logger.error(f"⚠️ Sensor/Stats Error: {e}")

        # 3. ADMIN BYPASS: Owners skip filtering
        if message.author.guild_permissions.administrator:
            await self.bot.process_commands(message)
            return

        # 4. CONTEXT ANALYSIS: The '# $ *' Logic
        try:
            # We pass the message, which now carries the 'purified' attribute
            result = await asyncio.wait_for(
                self.bot.context.analyze(message), 
                timeout=2.0
            )
            
            if result and result.get("verdict") == "INAPPROPRIATE":
                await self.bot.context.log_violation(message, result)
                return 

        except asyncio.TimeoutError:
            self.logger.warning(f"🕒 Dispatcher: Context Analysis timeout for {message.author}.")
        except Exception as e:
            self.logger.error(f"❌ Dispatcher: Context Service Error: {e}")

        # 5. THE BRIDGE: Execute Commands
        await self.bot.process_commands(message)
