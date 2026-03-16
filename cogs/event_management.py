import discord
from discord.ext import commands

class EventManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="start")
    @commands.has_permissions(administrator=True)
    async def start_event(self, ctx, *, event_name: str = "General Event"):
        """Turns on the attendance ticker and sets the event state."""
        if self.bot.events.is_active:
            return await ctx.send("⚠️ An event is already running!")

        self.bot.events.start_tracking()
        
        embed = discord.Embed(
            title="🚀 Event Started!",
            description=f"Now tracking attendance for: **{event_name}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Status", value="Ticketing System: **ONLINE** 🟢")
        embed.set_footer(text="Users staying for 50% of the duration earn points.")
        
        await ctx.send(embed=embed)

    @commands.command(name="stop")
    @commands.has_permissions(administrator=True)
    async def stop_event(self, ctx):
        """Stops the event, calculates 50% stay-time, and awards points."""
        if not self.bot.events.is_active:
            return await ctx.send("❌ No event is currently running.")

        # Get the list of IDs from our Service
        eligible_users = self.bot.events.get_eligible_users()
        self.bot.events.stop_tracking()

        # Award participation points (1 point for being there)
        awarded_count = 0
        for uid in eligible_users:
            try:
                await self.bot.points.add_points(uid, 1)
                awarded_count += 1
            except Exception as e:
                print(f"Failed to award point to {uid}: {e}")

        await ctx.send(f"🏁 **Event Finished!**\n✅ Awarded participation points to **{awarded_count}** members who stayed for at least 50% of the time.")

async def setup(bot):
    await bot.add_cog(EventManagement(bot))