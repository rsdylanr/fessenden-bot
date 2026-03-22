import discord
from discord.ext import commands

class MeritCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Merit Points Cloud System Online!")

    @commands.command(name="merits")
    async def merits(self, ctx, member: discord.Member = None):
        """Checks your merits or another member's merits."""
        target = member or ctx.author
        
        # Pull from Supabase
        balance = await self.bot.db.get_merits(target.id)
        
        embed = discord.Embed(
            title="⚖️ Merit Balance",
            description=f"{target.mention} has **{balance}** merits.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(name="givemerit")
    async def givemerit(self, ctx, member: discord.Member, amount: int):
        """Award merits using Supabase word-flags."""
        # Check custom cloud flag
        can_give = await self.bot.permissions.check_permission(ctx.author.id, "merits.admin")
        
        if not can_give:
            await ctx.send("❌ You do not have the `merits.admin` flag to do that.")
            return

        if amount <= 0:
            await ctx.send("❌ You must award a positive number of merits!")
            return

        await self.bot.db.add_merits(member.id, amount)
        await ctx.send(f"✅ Awarded **{amount}** merits to {member.mention} in the cloud!")

    @commands.command(name="removemerit")
    @commands.has_permissions(administrator=True)
    async def removemerit(self, ctx, member: discord.Member, amount: int):
        """(Admin Only) Deducts merits from a user using standard Discord permissions."""
        if amount <= 0:
            await ctx.send("❌ You must deduct a positive number of merits!")
            return

        await self.bot.db.add_merits(member.id, -amount)
        await ctx.send(f"❌ Deducted **{amount}** merits from {member.mention} in the cloud.")

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        """Displays the top 10 merit earners on the server."""
        top_users = await self.bot.db.get_leaderboard(10)

        if not top_users:
            await ctx.send("🤷 No one has any merits yet!")
            return

        embed = discord.Embed(
            title="🏆 Merit Leaderboard",
            color=discord.Color.gold()
        )

        for index, (user_id, balance) in enumerate(top_users, start=1):
            member = ctx.guild.get_member(user_id)
            name = member.mention if member else f"User ID: {user_id}"
            embed.add_field(name=f"#{index}", value=f"{name}: **{balance}** merits", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(MeritCog(bot))
