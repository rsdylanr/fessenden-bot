import discord
from discord.ext import commands
import time

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Check the bot's latency and heartbeat")
    async def ping(self, ctx):
        start_time = time.time()
        message = await ctx.send("📡 Measuring signal...")
        end_time = time.time()

        api_latency = round(self.bot.latency * 1000)
        round_trip = round((end_time - start_time) * 1000)

        embed = discord.Embed(title="📶 Connection Status", color=0x2ecc71)
        embed.add_field(name="API Latency", value=f"`{api_latency}ms`", inline=True)
        embed.add_field(name="Round Trip", value=f"`{round_trip}ms`", inline=True)
        embed.set_footer(text=f"Ref: {self.bot.message_service.generate_ref()}")
        
        await message.edit(content=None, embed=embed)

    @commands.hybrid_command(name="serverinfo", description="Get technical specs of this server")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"📊 {guild.name} Analysis", color=0x3498db)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="Security", value=f"Level {guild.verification_level}", inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
