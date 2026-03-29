import re
import discord

class ContentFilterService:
    def __init__(self, bot):
        self.bot = bot
        self.tree = {}

    async def sync(self):
        """Pulls the latest JSON from Supabase."""
        row = await self.bot.db.fetch_row("SELECT rules FROM filter_config WHERE id = 1")
        if row:
            self.tree = row['rules']
            print("🛡️ FilterService: Cloud Sync Complete.")

    async def save(self):
        """Pushes local tree changes to Supabase."""
        await self.bot.db.run_query(
            "UPDATE filter_config SET rules = $1 WHERE id = 1",
            self.tree
        )

    def get_match(self, text: str):
        """Recursive search: returns (found_word, category_name)"""
        categories = self.tree.get("ContentFilter", {}).get("Categories", {})
        return self._crawl(categories, text.lower())

    def _crawl(self, data, text):
        # Check Words
        for word in data.get("Words", []):
            if word.lower() in text:
                return word, "Violation"
        # Check Regex
        for pattern in data.get("Regex", []):
            if re.search(pattern, text, re.IGNORECASE):
                return pattern, "Violation"
        # Dive into Sub-categories
        for name, val in data.get("Sub", {}).items():
            res_w, _ = self._crawl(val, text)
            if res_w: return res_w, name
        return None, None

    def get_node(self, path: str):
        """Navigates 'Offensive/Slurs' to find the JSON object."""
        current = self.tree.get("ContentFilter", {}).get("Categories", {})
        for part in path.split("/"):
            if part in current: current = current[part]
            elif "Sub" in current and part in current["Sub"]: current = current["Sub"][part]
            else: return None
        return current
