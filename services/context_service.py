import re
import discord

class ContextService:
    def __init__(self, bot):
        self.bot = bot
        self.pronouns = {"you", "your", "you're", "youre", "u", "ur", "he", "him", "his", "she", "her", "hers", "they", "them", "theirs"}

    async def analyze(self, message: discord.Message):
        content = message.content.lower()
        curse_word, category = self.bot.filter.get_match(content)
        
        if not curse_word: return None

        # Tokenization (# = Name, $ = Curse, * = Pronoun)
        tokens = content.split()
        template = []
        is_directed = False

        for word in tokens:
            clean = re.sub(r'[^\w\s]', '', word)
            if clean == curse_word.lower() or curse_word.lower() in clean:
                template.append("$")
            elif any(m.name.lower() in word or m.display_name.lower() in word for m in message.mentions):
                template.append("#")
                is_directed = True
            elif clean in self.pronouns:
                template.append("*")
                is_directed = True
            else:
                template.append(word)

        if is_directed:
            return {
                "verdict": "INAPPROPRIATE",
                "template": " ".join(template),
                "category": category,
                "word": curse_word
            }
        return {"verdict": "CLEAN"}

    async def log_violation(self, message, result):
        log_channel = self.bot.get_channel(123456789) # REPLACE THIS ID
        embed = discord.Embed(title="Targeted Insult Detected", color=0xFF4444)
        embed.add_field(name="User", value=message.author.mention)
        embed.add_field(name="Template", value=f"`{result['template']}`")
        embed.add_field(name="Word Found", value=f"||{result['word']}||")
        await log_channel.send(embed=embed)
        await message.delete()
