import json
import os

class LocalizationService:
    def __init__(self, bot):
        self.bot = bot
        self.default_lang = "en"
        self.strings = {}
        self.load_strings()

    def load_strings(self):
        path = "data/strings.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.strings = json.load(f)

    def get(self, key, lang="en", **kwargs):
        """Retrieves a string and injects variables."""
        # Fallback to English if the theme/lang doesn't have the key
        text = self.strings.get(lang, {}).get(key) or self.strings.get("en", {}).get(key, key)
        
        # Inject variables like {name} or {count}
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
