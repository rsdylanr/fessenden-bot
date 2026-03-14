import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

from services.database_service import DatabaseService
from services.points_service import PointsService
from services.event_service import EventService

load_dotenv()

class FessendenBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.db = DatabaseService()
        self.points = PointsService(self.db)
        self.events = EventService()

    async def setup_hook(self):
        await self.db.initialize()
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

bot = FessendenBot()

async def main():
    async with bot:
        await bot.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())