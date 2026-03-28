import re
import discord
from typing import Optional, Dict, Any

class ContentFilterService:
    def __init__(self, bot):
        self.bot = bot
        self.tree = {}
        # Hardcoded IDs for those allowed to bypass or manage the filter
        self.masters = [123456789] # Add your Discord ID here

    async def sync(self):
        """Pulls the latest JSON tree from Supabase."""
        row = await self.bot.db.fetch_row("SELECT rules FROM filter_config WHERE id = 1")
        if row:
            self.tree = row['rules']
            print("🛡️ Content Filter: Tree synchronized from Cloud.")

    async def save_to_cloud(self):
        """Pushes the current local tree back to Supabase."""
        await self.bot.db.run_query(
            "UPDATE filter_config SET rules = $1 WHERE id = 1",
            self.tree
        )

    def _get_node(self, path: list) -> Optional[Dict]:
        """Helper to find a specific dictionary node based on a path list."""
        node = self.tree.get("ContentFilter", {}).get("Categories", {})
        for part in path:
            node = node.get("Sub", {}).get(part)
            if not node: return None
        return node

    def _recursive_check(self, data: Dict, text: str, path: str = "ContentFilter", last_settings: Dict = None) -> Optional[Dict]:
        """The 'Reasoning' Engine: Crawls the tree to find a match and its settings."""
        # Update inherited settings if this level has them
        current_settings = data.get("Settings", last_settings)
        
        # 1. Check Regex
        for pattern in data.get("Regex", []):
            if re.search(pattern, text, re.IGNORECASE):
                return {"path": path, "settings": current_settings}

        # 2. Check Words
        for word in data.get("Words", []):
            if word.lower() in text.lower():
                return {"path": path, "settings": current_settings}

        # 3. Check Sub-categories
        sub = data.get("Sub", {})
        for key, value in sub.items():
            result = self._recursive_check(value, text, f"{path} > {key}", current_settings)
            if result: return result
            
        return None

    async def run_check(self, message: discord.Message):
        """Main entry point for filtering."""
        if message.author.id in self.masters or message.author.bot:
            return

        hit = self._recursive_check(self.tree.get("Categories", {}), message.content)
        
        if hit:
            settings = hit['settings'] or {"Action": "Delete", "Severity": 1}
            action = settings.get("Action", "Delete")
            
            # Execute Punishments
            if "Delete" in action:
                try: await message.delete()
                except: pass
            
            if "Log" in action:
                # Add your logging logic here
                pass
                
            if "Ban" in action:
                await message.author.ban(reason=f"Filter: {hit['path']}")

            return hit
        return None
