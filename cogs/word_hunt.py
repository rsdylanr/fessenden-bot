import discord
from discord.ext import commands
import random
import asyncio
import time

class WordHunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # A starter dictionary. For a production bot, you'd load a .txt file with 10k+ words.
        self.dictionary = {"FIRE", "WATER", "WIND", "EARTH", "MINE", "CRAFT", "BOLT", "STAR", "GAME", "CODE", "WORD", "HUNT", "COOL", "TEAM", "BOSS"}
        self.vowels = "AEIOU"
        self.consonants = "BCDFGHJKLMNPQRSTVWXYZ"

    def generate_grid(self):
        """Creates a 4x4 grid with a balanced mix of vowels and consonants."""
        grid = []
        for _ in range(16):
            # 30% chance for a vowel to ensure the board is playable
            char = random.choice(self.vowels) if random.random() < 0.3 else random.choice(self.consonants)
            grid.append(char)
        return grid

    def format_grid(self, grid):
        """Formats the list into a visual 4x4 block."""
        display = ""
        for i in range(0, 16, 4):
            display += f"` {grid[i]}   {grid[i+1]}   {grid[i+2]}   {grid[i+3]} `\n"
        return display

    @commands.command(name="wordhunt")
    async def start_wordhunt(self, ctx):
        """Starts a 60-second word finding competition."""
        grid = self.generate_grid()
        ref = self.bot.message_service.generate_ref()
        
        embed = discord.Embed(
            title="🔠 WORD HUNT",
            description=f"Find as many words as possible in 60 seconds!\n\n{self.format_grid(grid)}",
            color=0x3498db
        )
        embed.set_footer(text=f"Ref: {ref} | Type words in chat to score!")
        
        game_msg = await ctx.send(embed=embed)
        
        found_words = []
        scores = {} # UserID: Score
        end_time = time.time() + 60

        def check(m):
            # Must be in the same channel, not a bot, and within the time limit
            return m.channel == ctx.channel and not m.author.bot and time.time() < end_time

        # Phase 4: Text Input Loop
        while time.time() < end_time:
            try:
                # Wait for any message for a short burst
                timeout = end_time - time.time()
                msg = await self.bot.wait_for('message', check=check, timeout=timeout)
                word = msg.content.upper()

                # Validation Logic
                if word in self.dictionary and word not in found_words:
                    # Check if letters exist in the grid (Simplified check)
                    # A more advanced version would check for adjacency (Boggle style)
                    grid_copy = list(grid)
                    can_make = True
                    for letter in word:
                        if letter in grid_copy:
                            grid_copy.remove(letter)
                        else:
                            can_make = False
                            break
                    
                    if can_make:
                        found_words.append(word)
                        user_id = msg.author.id
                        points = len(word) * 10
                        scores[user_id] = scores.get(user_id, 0) + points
                        await msg.add_reaction("✅")
                elif word in found_words:
                    await msg.add_reaction("♻️") # Already found

            except asyncio.TimeoutError:
                break

        # 🏁 Leaderboard Calculation
        if not scores:
            return await ctx.send("⌛ **Time's up!** No words were found. Better luck next time!")

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard = ""
        for i, (uid, score) in enumerate(sorted_scores[:5]):
            user = self.bot.get_user(uid)
            name = user.display_name if user else "Unknown Explorer"
            leaderboard += f"{i+1}. **{name}**: {score} pts\n"

        result_embed = discord.Embed(
            title="🏆 WORD HUNT RESULTS",
            description=f"**Words Found:** {', '.join(found_words)}\n\n**Leaderboard:**\n{leaderboard}",
            color=0x2ecc71
        )
        result_embed.set_footer(text=f"Ref: {ref}")
        await ctx.send(embed=result_embed)

async def setup(bot):
    await bot.add_cog(WordHunt(bot))
