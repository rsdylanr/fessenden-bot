import discord
from discord.ext import commands
from discord import app_commands

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Check your points and staff record")
    @app_commands.describe(member="The member to check (defaults to yourself)")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        points, records = await self.bot.points.get_stats(target.id)
        
        embed = discord.Embed(
            title=f"👤 {target.display_name}'s Profile",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Total Points", value=f"⭐ `{points}`", inline=True)
        
        # Only show records if they exist, otherwise keep it clean
        val = f"```{records}```" if records else "_No infractions on record._"
        embed.add_field(name="Staff Notes", value=val, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="See the top 10 roasters")
    async def leaderboard(self, interaction: discord.Interaction):
        # Fetch top 10 from DB
        data = await self.bot.db.fetch_all(
            "SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10"
        )
        
        embed = discord.Embed(
            title="🏆 Fessenden Global Leaderboard",
            color=discord.Color.gold()
        )
        
        if not data:
            embed.description = "The board is currently empty. Start an event to earn points!"
        else:
            description = ""
            for i, (user_id, points) in enumerate(data, 1):
                # Medal emojis for top 3
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"**{i}.**")
                description += f"{medal} <@{user_id}> — `{points} pts`\n"
            embed.description = description

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))