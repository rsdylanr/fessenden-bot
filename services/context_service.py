import asyncio
import logging

class ContextService:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("fessenden.context")

    async def analyze(self, message):
        """
        Pure Deterministic Analysis.
        Relies 100% on the Recursive Filter Tree (Supabase).
        No external AI or Sentiment APIs.
        """
        text = message.content
        if not text or len(text.strip()) == 0:
            return {"verdict": "CLEAN"}

        # --- STEP 1: THE RECURSIVE FILTER CHECK ---
        # This uses your get_match logic with Regex Word Boundaries.
        try:
            found_word, category = self.bot.filter.get_match(text)
            
            if found_word:
                return {
                    "verdict": "INAPPROPRIATE", 
                    "reason": f"Filtered Word: {found_word}", 
                    "source": category
                }
        except Exception as e:
            print(f"⚠️ Filter Execution Error: {e}")
            # If the filter fails, we fail-safe to CLEAN to keep the bot alive
            return {"verdict": "CLEAN"}

        # If nothing in the tree is matched, the message is safe.
        return {"verdict": "CLEAN"}

    async def log_violation(self, message, result):
        """Records the filtered event in Supabase for staff review."""
        try:
            payload = {
                "user_id": str(message.author.id),
                "username": str(message.author),
                "content": message.content,
                "reason": result.get("reason"),
                "source": result.get("source"),
                "channel_id": str(message.channel.id)
            }
            # Ensure your 'violation_logs' table exists in Supabase
            await self.bot.db.run_query(
                "INSERT INTO violation_logs (user_id, username, content, reason, source, channel_id) VALUES ($1, $2, $3, $4, $5, $6)",
                payload["user_id"], payload["username"], payload["content"], 
                payload["reason"], payload["source"], payload["channel_id"]
            )
        except Exception as e:
            print(f"❌ Failed to log violation: {e}")
