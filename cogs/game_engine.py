import discord
from discord.ext import commands, tasks
import random
import asyncio
import time

class GameEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Minecraft/Tech themed words for Unscramble
        self.word_bank = ["OBSIDIAN", "REDSTONE", "BEDROCK", "PYTHON", "DISCORD", "FESSENDEN", "CIRCUIT"]
        self.game_loop.start()

    def cog_unload(self):
        self.game_loop.cancel()

    @tasks.loop(minutes=5)
    async def game_loop(self):
        """The core loop that triggers games only if the room is active."""
        target_id = self.bot.games_channel_id
        
        # 1. Activity Sensor Check
        if not self.bot.sensor.is_channel_active(target_id):
            print(f"💤 Game Loop: Channel {target_id} is idle. Skipping.")
            return

        channel = self.bot.get_channel(target_id)
        if not channel: return

        # 2. Pick a random game
        game_choice = random.choice(["unscramble", "math", "reaction"])
        
        if game_choice == "unscramble":
            await self.run_unscramble(channel)
        elif game_choice == "math":
            await self.run_math(channel)
        elif game_choice == "reaction":
            # Reuses your Reaction command logic
            from cogs.skill_tests import ReactionButton
            await self.run_reaction(channel)

    async def run_unscramble(self, channel):
        original = random.choice(self.word_bank)
        jumbled = "".join(random.sample(original, len(original)))
        
        await channel.send(f"🧩 **Word Unscramble!** Unscramble this word: `{jumbled}`")

        def check(m):
            return m.channel == channel and m.content.upper() == original and not m.author.bot

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            await channel.send(f"🏆 {msg.author.mention} got it! The word was **{original}**.")
        except asyncio.TimeoutError:
            await channel.send(f"⏰ Time's up! The word was **{original}**.")

    async def run_math(self, channel):
        num1, num2 = random.randint(1, 50), random.randint(1, 50)
        answer = num1 + num2
        await channel.send(f"🔢 **Math Sprint!** What is `{num1} + {num2}`?")

        def check(m):
            return m.channel == channel and m.content == str(answer) and not m.author.bot

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            await channel.send(f"⚡ {msg.author.mention} was the fastest! Answer: **{answer}**")
        except asyncio.TimeoutError:
            await channel.send(f"⏰ No one answered in time. The answer was **{answer}**.")

    @game_loop.before_loop
    async def before_game_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(GameEngine(bot))
