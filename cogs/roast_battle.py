import discord
from discord.ext import commands
import random

class RoastBattle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_match = []

    @commands.command()
    async def next_match(self, ctx):
        if not ctx.author.voice: return await ctx.send("Join a VC first!")
        
        channel = ctx.author.voice.channel
        members = [m for m in channel.members if not m.bot]
        
        # Priority Logic
        priority = [m for m in members if m.id not in self.bot.events.has_gone]
        if len(priority) < 2:
            self.bot.events.has_gone.clear()
            priority = members

        p1, p2 = random.sample(priority, 2)
        self.current_match = [p1, p2]
        self.bot.events.has_gone.update([p1.id, p2.id])

        # Staff Briefing
        r1 = await self.bot.points.get_misbehavior_record(p1.id)
        r2 = await self.bot.points.get_misbehavior_record(p2.id)
        
        embed = discord.Embed(title="⚔️ Next Match Set", color=discord.Color.red())
        embed.add_field(name=p1.display_name, value=f"Record: {r1}")
        embed.add_field(name=p2.display_name, value=f"Record: {r2}")
        await ctx.send(embed=embed)

    @commands.command()
    async def award_winner(self, ctx, winner: discord.Member):
        if not ctx.author.guild_permissions.manage_messages: return
        
        await self.bot.points.add_points(winner.id, 2) # 1 for stage, 1 for win
        await winner.send(f"🏆 You won the roast battle and earned 2 points!")
        await ctx.send(f"✅ {winner.mention} has been awarded.")

async def setup(bot):
    await bot.add_cog(RoastBattle(bot))