import discord
from discord.ext import commands, tasks
import os
import asyncio
import traceback
from dotenv import load_dotenv

# Service Imports (Kept exactly as your original architecture)
from services.cloud_db_service import CloudDatabaseService as DatabaseService
from services.points_service import PointsService
from services.event_service import EventService
from services.calendar_service import CalendarService
from services.trivia_service import TriviaService

load_dotenv()

class FessendenBot(commands.Bot):
    def __init__(self):
        # Intents.all() is required for tracking Voice Channels and Members
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        
        # --- GLOBAL CONFIGURATION ---
        self.owner_id_num = 716581384344567878
        self.renewal_channel_id = 987654321098765432  # <--- REPLACE WITH YOUR CHANNEL ID
        
        # Initialize Services
        self.db = DatabaseService()
        self.points = PointsService(self.db)
        self.events = EventService()
        self.calendar = CalendarService(self.db)
        self.trivia = TriviaService()

    async def setup_hook(self):
        """Initializes database, loops, and cogs on startup."""
        await self.db.initialize()
        
        # Start Background Tasks
        self.attendance_loop.start()
        self.reminder_loop.start()
        self.renewal_reminder.start()
        
        # Load Cogs Dynamically
        await self.load_all_extensions()

    async def load_all_extensions(self):
        """Discovers and loads all cogs inside the /cogs directory."""
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')
            print("📁 Created missing /cogs directory.")

        for f in os.listdir('./cogs'):
            if f.endswith('.py') and f != "__init__.py":
                try:
                    await self.load_extension(f'cogs.{f[:-3]}')
                    print(f"✅ Loaded {f}")
                except Exception as e:
                    print(f"❌ Failed to load {f}: {e}")

    def is_owner_check(self, user_id: int):
        """Global check for Developer/Owner status."""
        return user_id == self.owner_id_num

    # --- BACKGROUND LOOPS ---

    @tasks.loop(minutes=1)
    async def attendance_loop(self):
        """Tracks points for users in Voice Channels during events."""
        if self.events.is_active:
            for g in self.guilds:
                for vc in g.voice_channels + g.stage_channels:
                    if vc.members:
                        ids = [m.id for m in vc.members if not m.bot]
                        self.events.record_tick(ids)

    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        """Sends a notification for calendar events starting in 1 hour."""
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
        """Pings the owner every 23 hours to renew Pterodactyl hosting."""
        await self.wait_until_ready()
        chan = self.get_channel(self.renewal_channel_id)
        owner = self.get_user(self.owner_id_num)
        
        if chan and owner:
            embed = discord.Embed(
                title="🚨 Pterodactyl Renewal Notice",
                description=(
                    f"Hey {owner.mention}, it has been 23 hours!\n\n"
                    "Please log into your Pterodactyl panel and click the **Renew** button "
                    "to prevent the bot from going offline."
                ),
                color=discord.Color.red()
            )
            await chan.send(content=owner.mention, embed=embed)

    @renewal_reminder.before_loop
    @attendance_loop.before_loop
    @reminder_loop.before_loop
    async def before_loops(self):
        """Ensures the bot is ready before starting background tasks."""
        await self.wait_until_ready()

# --- INSTANTIATION ---

bot = FessendenBot()

# --- 🛠️ ADVANCED DYNAMIC COG & SYSTEM CONTROLS ---

@bot.command(name="sync")
async def sync_slash_commands(ctx):
    """Manual trigger to sync Slash Commands to Discord's API."""
    if not bot.is_owner_check(ctx.author.id):
        return await ctx.send("❌ You do not have permission to sync.")
    
    await ctx.defer()
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"🌍 Successfully synced {len(synced)} global slash commands.")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: `{e}`")


@bot.group(name="system", invoke_without_command=True)
async def system_group(ctx):
    """Base command for managing dynamic systems and reloads."""
    if not bot.is_owner_check(ctx.author.id):
        return await ctx.send("❌ Access Denied.")
    await ctx.send("🔧 Use `!system load <cog>`, `!system reload <cog>`, `!system unload <cog>`, or `!system list`.")


@system_group.command(name="load")
async def load_cog(ctx, extension: str):
    """Hot-loads a brand new cog without restarting the bot."""
    if not bot.is_owner_check(ctx.author.id): return
    
    try:
        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"✅ Successfully hot-loaded `cogs.{extension}`!")
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"Error loading {extension}:\n{error_msg}")
        await ctx.send(f"❌ Failed to load `{extension}`:\n```py\n{str(e)}\n```")


@system_group.command(name="unload")
async def unload_cog(ctx, extension: str):
    """Unloads a cog dynamically."""
    if not bot.is_owner_check(ctx.author.id): return
    
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"✅ Successfully unloaded `cogs.{extension}`!")
    except Exception as e:
        await ctx.send(f"❌ Failed to unload `{extension}`:\n```py\n{str(e)}\n```")


@system_group.command(name="reload")
async def reload_cog(ctx, extension: str):
    """Hot-reloads an existing cog to push updates instantly."""
    if not bot.is_owner_check(ctx.author.id): return
    
    try:
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"✅ Successfully hot-reloaded `cogs.{extension}`!")
    except Exception as e:
        error_msg = traceback.format_exc()
        await ctx.send(f"❌ Failed to reload `{extension}`:\n```py\n{str(e)}\n```")


@system_group.command(name="list")
async def list_cogs(ctx):
    """Lists all active cogs running on the bot."""
    if not bot.is_owner_check(ctx.author.id): return
    
    loaded_cogs = [name.replace('cogs.', '') for name in bot.extensions.keys()]
    
    if not loaded_cogs:
        return await ctx.send("📂 No extensions are currently loaded.")
        
    embed = discord.Embed(
        title="📂 Active System Cogs",
        description="\n".join([f"• `{c}`" for c in loaded_cogs]),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)


@system_group.command(name="refresh_all")
async def refresh_all_cogs(ctx):
    """Hard-refreshes every single cog folder without disconnecting the bot."""
    if not bot.is_owner_check(ctx.author.id): return
    
    await ctx.send("🔄 Refreshing all bot systems...")
    results = []
    
    for f in os.listdir('./cogs'):
        if f.endswith('.py') and f != "__init__.py":
            cog_name = f[:-3]
            try:
                if f"cogs.{cog_name}" in bot.extensions:
                    await bot.reload_extension(f"cogs.{cog_name}")
                    results.append(f"✅ `{cog_name}` reloaded.")
                else:
                    await bot.load_extension(f"cogs.{cog_name}")
                    results.append(f"📥 `{cog_name}` newly loaded.")
            except Exception as e:
                results.append(f"❌ `{cog_name}` failed: `{str(e)}`")

    output = "\n".join(results)
    if len(output) > 2000:
        await ctx.send("✅ System purge complete. (Output too large to display, check logs).")
    else:
        await ctx.send(output)

# --- BOOT ENTRY POINT ---

async def main():
    async with bot:
        await bot.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    try:
        # Standard asyncio run loop that works on all Python versions
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot shutting down manually.")
    except Exception as e:
        print(f"🚨 Bot crashed with critical startup error: {e}")
