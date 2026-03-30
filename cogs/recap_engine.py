import discord
from discord.ext import commands, tasks
from datetime import datetime, time

class RecapEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recap_loop.start()

    def cog_unload(self):
        self.recap_loop.cancel()

    @tasks.loop(time=time(hour=0, minute=0))
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

        if top_chatter:
            user = self.bot.get_user(top_chatter[0])
            name = user.display_name if user else "Unknown"
            embed.add_field(name="🗣️ Top Chatter", value=f"{name} ({top_chatter[1]} msgs)", inline=False)

        if top_gamer:
            user = self.bot.get_user(top_gamer[0])
            name = user.display_name if user else "Unknown"
            embed.add_field(name="🎮 Game Champion", value=f"{name} ({top_gamer[1]} wins)", inline=False)

        embed.add_field(name="📈 Stats", value=f"Total Messages: **{self.bot.stats.total_messages}**", inline=False)
        await channel.send(embed=embed)
        self.bot.stats.reset_daily()

    @recap_loop.before_loop
    async def before_recap(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RecapEngine(bot))
