import discord
from discord.ext import commands, tasks
import random
import asyncio
import time

class GameEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Minecraft, Coding, and Fessenden themed word bank
        self.word_bank = [
            "OBSIDIAN", "REDSTONE", "BEDROCK", "PYTHON", "DISCORD", 
            "FESSENDEN", "CIRCUIT", "DATABASE", "REACT", "NETWORK",
            "DIAMOND", "EMERALD", "VILLAGER", "CREEPER", "SKELETON"
        ]
        # Start the background loop
        self.game_loop.start()

    def cog_unload(self):
        self.game_loop.cancel()

    @tasks.loop(minutes=5)
    async def game_loop(self):
        """The core engine that drives interaction."""
        target_id = self.bot.games_channel_id
        
        # 1. Activity Sensor Check (Don't play in an empty room)
        if not self.bot.sensor.is_channel_active(target_id):
            print(f"💤 GameEngine: Channel {target_id} is idle. Skipping cycle.")
            return

        channel = self.bot.get_channel(target_id)
        if not channel:
            return

        # 2. Randomly select the type of interaction
        # Weights: 30% Unscramble, 30% Math, 20% Reaction, 20% Wildcard
        choice = random.choices(
            ["unscramble", "math", "reaction", "wildcard"],
            weights=[30, 30, 20, 20],
            k=1
        )[0]

        if choice == "unscramble":
            await self.run_unscramble(channel)
        elif choice == "math":
            await self.run_math(channel)
        elif choice == "reaction":
            await self.run_reaction_test(channel)
        elif choice == "wildcard":
            await self.run_wildcard_event(channel)

    async def run_unscramble(self, channel):
        """Jumbles a word and waits for the first correct answer."""
        original = random.choice(self.word_bank)
        jumbled = list(original)
        random.shuffle(jumbled)
        jumbled_str = "".join(jumbled)
        
        embed = discord.Embed(
            title="🧩 Word Unscramble",
            description=f"Unscramble this word: **`{jumbled_str}`**",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)

        def check(m):
            return m.channel == channel and m.content.upper() == original and not m.author.bot

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            await channel.send(f"🏆 {msg.author.mention} got it! The word was **{original}**.")
            # Update Stats & Points
            self.bot.stats.record_win(msg.author.id)
            # await self.bot.points.add_points(msg.author.id, 10)
        except asyncio.TimeoutError:
            await channel.send(f"⏰ Time's up! The word was **{original}**.")

    async def run_math(self, channel):
        """Simple arithmetic sprint."""
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)
        operator = random.choice(["+", "-"])
        answer = num1 + num2 if operator == "+" else num1 - num2
        
        embed = discord.Embed(
            title="🔢 Math Sprint",
            description=f"Quick! What is `{num1} {operator} {num2}`?",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

        def check(m):
            return m.channel == channel and m.content == str(answer) and not m.author.bot

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=20.0)
            await channel.send(f"⚡ {msg.author.mention} was the fastest! Correct: **{answer}**")
            # Update Stats & Points
            self.bot.stats.record_win(msg.author.id)
        except asyncio.TimeoutError:
            await channel.send(f"⏰ No one answered in time. The answer was **{answer}**.")

    async def run_reaction_test(self, channel):
        """Triggers the reaction speed test (requires ReactionButton from skill_tests)."""
        # We invoke the command logic manually here
        skill_cog = self.bot.get_cog("SkillTests")
        if skill_cog:
            # We simulate a Context for the cog method if needed, or call logic directly
            # For simplicity, we assume you have the reaction_test command in skill_tests.py
            ctx = await self.bot.get_context(await channel.send("🎯 **Reaction Test Starting...**"))
            await skill_cog.reaction_test(ctx)

    async def run_wildcard_event(self, channel):
        """Triggers a random unpredictable event."""
        wildcard_cog = self.bot.get_cog("WildcardEngine")
        if wildcard_cog:
            await wildcard_cog.trigger_wildcard(channel)

    @game_loop.before_loop
    async def before_game_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(GameEngine(bot))
