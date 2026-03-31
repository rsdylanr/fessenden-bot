import discord
from discord.ext import commands, tasks
import os
import asyncio
import traceback
from dotenv import load_dotenv

# Service Imports
from services.cloud_db_service import CloudDatabaseService as DatabaseService
from services.points_service import PointsService
from services.event_service import EventService
from services.calendar_service import CalendarService
from services.trivia_service import TriviaService
from services.content_filter_service import ContentFilterService
from services.context_service import ContextService
from services.dispatcher_service import DispatcherService  # <--- Added
from services.game_sensor_service import GameSensorService
from services.stats_service import StatsService
from services.message_service import MessageService
load_dotenv()

class FessendenBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        
        # --- GLOBAL CONFIGURATION ---
        self.owner_id_num = 716581384344567878
        self.renewal_channel_id = 987654321098765432
        self.games_channel_id = 1488240654839582961
        
        # Initialize Core Services
        self.db = DatabaseService()
        self.points = PointsService(self.db)
        self.events = EventService()
        self.calendar = CalendarService(self.db)
        self.trivia = TriviaService()

        # Initialize New Framework Services
        self.filter = ContentFilterService(self)
        self.context = ContextService(self)
        self.dispatcher = DispatcherService(self)
        self.sensor = GameSensorService(self)
        self.stats = StatsService(self)
        self.message_service = MessageService(self)

    async def setup_hook(self):
        """Initializes database, loops, and cogs on startup."""
        await self.db.initialize()
        
        # Sync the Content Filter from Supabase
        await self.filter.sync()
        
        # Start Background Tasks
        self.attendance_loop.start()
        self.reminder_loop.start()
        self.renewal_reminder.start()
        
        # Load Cogs Dynamically
        await self.load_all_extensions()
        
        # Sync Slash Commands (Optional: can be done via !sync command)
        # await self.tree.sync()

    async def on_message(self, message):
        """
        The Central Orchestrator. 
        All messages pass through the Dispatcher for Filter/Context analysis.
        """
        self.stats.record_message(message.author.id)
        self.sensor.record_activity(message.channel.id)
        await self.dispatcher.handle_message(message)
        await self.process_commands(message)

    # --- REST OF YOUR BACKGROUND LOOPS & COG LOADING LOGIC ---
    async def load_all_extensions(self):
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')
        for f in os.listdir('./cogs'):
            if f.endswith('.py') and f != "__init__.py":
                try:
                    await self.load_extension(f'cogs.{f[:-3]}')
                    print(f"✅ Loaded {f}")
                except Exception as e:
                    print(f"❌ Failed to load {f}: {e}")

    def is_owner_check(self, user_id: int):
        return user_id == self.owner_id_num

    @tasks.loop(minutes=1)
    async def attendance_loop(self):
        if self.events.is_active:
            for g in self.guilds:
                for vc in g.voice_channels + g.stage_channels:
                    if vc.members:
                        ids = [m.id for m in vc.members if not m.bot]
                        self.events.record_tick(ids)

    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        reminders = await self.calendar.check_reminders()
        if reminders:
            chan = self.get_channel(self.renewal_channel_id)
            if chan:
                for name, desc in reminders:
                    em = discord.Embed(
                        title="📅 Event Starting Soon!", 
                        description=f"**{name}** starts in 1 hour!\n{desc if desc else ''}", 
                        color=0xF1C40F
                    )
                    await chan.send(content="@everyone", embed=em)

    @tasks.loop(hours=23)
    async def renewal_reminder(self):
        await self.wait_until_ready()
        chan = self.get_channel(self.renewal_channel_id)
        owner = self.get_user(self.owner_id_num)
        if chan and owner:
            embed = discord.Embed(
                title="🚨 Pterodactyl Renewal Notice",
                description=f"Hey {owner.mention}, it has been 23 hours!\n\nRenew your panel now.",
                color=discord.Color.red()
            )
            await chan.send(content=owner.mention, embed=embed)

    @renewal_reminder.before_loop
    @attendance_loop.before_loop
    @reminder_loop.before_loop
    async def before_loops(self):
        await self.wait_until_ready()

# --- BOOT ENTRY POINT ---
bot = FessendenBot()

# --- DYNAMIC CONTROLS (Keep these exactly as you had them) ---
@bot.command(name="sync")
async def sync_slash_commands(ctx):
    if not bot.is_owner_check(ctx.author.id): return
    await ctx.defer()
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"🌍 Synced {len(synced)} slash commands.")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: `{e}`")

# ... (Include your !system group and main() function here)

async def main():
    async with bot:
        await bot.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot shutting down manually.")
