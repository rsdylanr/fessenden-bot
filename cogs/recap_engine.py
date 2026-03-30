import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta

class RecapEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Set the recap for Midnight (00:00)
        self.recap_loop.start()

    def cog_unload(self):
        self.recap_loop.cancel()

    @tasks.loop(time=time(hour=0, minute=0)) # Triggers exactly at midnight
    async def recap_loop(self):
        channel = self.bot.get_channel(self.bot.games_channel_id)
        if not channel: return

        top_chatter = self.bot.stats.get_top_user()
        top_gamer = self.bot.stats.get_top_gamer()

        embed = discord.Embed(
            title="📊 Daily Server Recap",
            description=f"Summary for {datetime.now().strftime('%B %d, %Y')}",
            color=discord.Color.purple()
        )

        # Most Active Chatter
        if top_chatter:
            user = self.bot.get_user(top_chatter[0])
            name = user.display_name if user else "Unknown"
            embed.add_field(name="🗣️ Top Chatter", value=f"{name} ({top_chatter[1]} messages)", inline=False)

        # Top Game Winner
        if top_gamer:
            user = self.bot.get_user(top_gamer[0])
            name = user.display_name if user else "Unknown"
            embed.add_field(name="🎮 Game Champion", value=f"{name} ({top_gamer[1]} wins)", inline=False)

        embed.add_field(name="📈 Community Stats", value=f"Total Messages: **{self.bot.stats.total_messages}**", inline=False)
        embed.set_footer(text="Stats have been reset for the new day.")

        await channel.send(embed=embed)
        
        # Reset the data for the next 24 hours
        self.bot.stats.reset_daily()

    @recap_loop.before_loop
    async def before_recap(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RecapEngine(bot))
