from discord.ext import commands, tasks
import random
import asyncio

class GameEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_channel_id = 123456789 # Set your games channel ID
        self.game_loop.start()

    def cog_unload(self):
        self.game_loop.cancel()

    @tasks.loop(minutes=5)
    async def game_loop(self):
        # 1. Check if the room is 'Alive'
        if not self.bot.sensor.is_channel_active(self.game_channel_id):
            print(f"💤 Game loop skipped: Channel {self.game_channel_id} is idle.")
            return

        # 2. Pick a random game from your Skill Test list
        game_type = random.choice(["Reaction", "Unscramble", "Math"])
        await self.trigger_game(game_type)

    async def trigger_game(self, game_type):
        channel = self.bot.get_channel(self.game_channel_id)
        if not channel: return

        if game_type == "Math":
            a, b = random.randint(1, 20), random.randint(1, 20)
            await channel.send(f"🔢 **Math Sprint!** What is {a} + {b}?")
            # Logic to wait for answer...

    @game_loop.before_loop
    async def before_game_loop(self):
        await self.bot.wait_until_ready()
