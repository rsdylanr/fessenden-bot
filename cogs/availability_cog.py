import discord
from discord.ext import commands

class AvailabilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Availability Scheduling (Hybrid) Online!")

    @commands.hybrid_command(name="setavail", description="Set your gaming availability in the cloud.")
    async def setavail(self, ctx, day: str, start_time: str, end_time: str):
        """Saves your schedule to Supabase."""
        await ctx.defer() # ⏱️ Gives Supabase time to write data

        # Validate the day of the week
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if day.lower() not in days:
            return await ctx.send("❌ Please enter a valid day of the week (e.g., Monday).")

        # Save to Cloud DB
        await self.bot.db.run_query("""
            INSERT INTO availability (user_id, day_of_week, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """, ctx.author.id, day.lower(), start_time, end_time)

        await ctx.send(f"✅ Saved! You are available on **{day.title()}** from **{start_time}** to **{end_time}**.")

    @commands.hybrid_command(name="schedule", description="View everyone's gaming schedules.")
    async def schedule(self, ctx, day: str):
        """Pulls the server schedule for a specific day from Supabase."""
        await ctx.defer()

        rows = await self.bot.db.fetch_all("SELECT user_id, start_time, end_time FROM availability WHERE day_of_week = ?", day.lower())

        if not rows:
            return await ctx.send(f"🤷 No schedules found for {day.title()}.")

        embed = discord.Embed(
            title=f"📅 Gaming Schedule for {day.title()}",
            color=discord.Color.green()
        )

        for user_id, start, end in rows:
            member = ctx.guild.get_member(user_id)
            name = member.mention if member else f"User ID: {user_id}"
            embed.add_field(name=name, value=f"⏰ {start} - {end}", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AvailabilityCog(bot))
