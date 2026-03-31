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
        # 1. Check Words
        for word in data.get("Words", []):
            if word.lower() in text:
                return word, "Violation"
        
        # 2. Check Regex
        for pattern in data.get("Regex", []):
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    return pattern, "Violation"
            except re.error:
                continue # Skip invalid regex patterns

        # 3. Dive into Sub-categories
        for name, val in data.get("Sub", {}).items():
            res_w, res_cat = self._crawl(val, text)
            if res_w: 
                # Return the specific sub-category name if found
                return res_w, name
        return None, None

    def get_node(self, path: str):
        """Navigates 'Offensive/Slurs' to find the JSON object."""
        current = self.tree.get("ContentFilter", {}).get("Categories", {})
        if not path: return current

        for part in path.split("/"):
            # Check if part is a direct key or inside "Sub"
            if part in current:
                current = current[part]
            elif isinstance(current, dict) and "Sub" in current and part in current["Sub"]:
                current = current["Sub"][part]
            else:
                return None
        return current

    def get_all_paths(self):
        """
        Recursively finds all valid category paths in the tree.
        Returns: ['Offensive', 'Offensive/Slurs', 'Geography/Flags']
        """
        categories = self.tree.get("ContentFilter", {}).get("Categories", {})
        paths = []

        def walk(data, current_path=""):
            for name, val in data.items():
                # Build the path string
                new_path = f"{current_path}/{name}" if current_path else name
                paths.append(new_path)
                
                # If there are sub-categories, walk deeper
                if isinstance(val, dict) and "Sub" in val:
                    walk(val["Sub"], new_path)

        walk(categories)
        return paths
