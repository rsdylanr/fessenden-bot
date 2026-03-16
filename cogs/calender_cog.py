import discord
from discord.ext import commands
from discord import app_commands
import datetime

class CalendarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="Schedule a future community event")
    @app_commands.describe(
        name="Name of the event", 
        date="YYYY-MM-DD (e.g., 2026-04-15)", 
        time="HH:MM in 24h format (e.g., 18:30 for 6:30 PM)",
        description="Briefly describe the event"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def schedule(self, interaction: discord.Interaction, name: str, date: str, time: str, description: str = None):
        # Validate date format
        try:
            event_time_str = f"{date} {time}"
            # Check if the format is valid
            datetime.datetime.strptime(event_time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return await interaction.response.send_message(
                "❌ Invalid format! Please use `YYYY-MM-DD` and `HH:MM` (24h).", 
                ephemeral=True
            )

        await self.bot.calendar.add_event(name, event_time_str, description)
        
        embed = discord.Embed(title="📅 Event Scheduled", color=discord.Color.blue())
        embed.add_field(name="Event", value=name, inline=False)
        embed.add_field(name="Date/Time", value=f"`{event_time_str}`", inline=True)
        if description:
            embed.add_field(name="Description", value=description, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="calendar", description="View all upcoming events")
    async def calendar(self, interaction: discord.Interaction):
        # Auto-clean old events before showing the list
        await self.bot.calendar.clear_past_events()
        
        events = await self.bot.calendar.get_all_events()
        
        if not events:
            return await interaction.response.send_message("📅 No upcoming events scheduled.")

        embed = discord.Embed(
            title="🗓️ Fessenden Event Calendar", 
            description="Here are our upcoming community events:",
            color=discord.Color.purple()
        )

        for name, etime, desc in events:
            val = f"🕒 **{etime}**"
            if desc:
                val += f"\n> {desc}"
            embed.add_field(name=name, value=val, inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CalendarCog(bot))