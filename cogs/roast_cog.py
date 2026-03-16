import discord
from discord.ext import commands
from discord import app_commands
import random

class RoastVotingView(discord.ui.View):
    def __init__(self, bot, p1, p2):
        super().__init__(timeout=60)
        self.bot = bot
        self.p1, self.p2 = p1, p2
        self.votes = {p1.id: 0, p2.id: 0}
        self.voters = set()

    @discord.ui.button(label="Vote P1", style=discord.ButtonStyle.primary)
    async def p1_btn(self, i, b): await self.process_vote(i, self.p1.id)

    @discord.ui.button(label="Vote P2", style=discord.ButtonStyle.success)
    async def p2_btn(self, i, b): await self.process_vote(i, self.p2.id)

    async def process_vote(self, interaction, user_id):
        if interaction.user.id in self.voters:
            return await interaction.response.send_message("Already voted!", ephemeral=True)
        self.voters.add(interaction.user.id)
        self.votes[user_id] += 1
        await interaction.response.send_message("Vote counted!", ephemeral=True)

class RoastCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_match = []

    @app_commands.command(name="next", description="Pick the next two roasters")
    async def next_match(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            return await interaction.response.send_message("⚠️ Join the Stage/VC first!", ephemeral=True)

        members = [m for m in interaction.user.voice.channel.members if not m.bot]
        if len(members) < 2:
            return await interaction.response.send_message("❌ Not enough people in VC!", ephemeral=True)

        # Logic: Priority to those who haven't gone
        eligible = [m for m in members if m.id not in self.bot.events.has_gone]
        if len(eligible) < 2:
            self.bot.events.has_gone.clear()
            eligible = members

        self.current_match = random.sample(eligible, 2)
        p1, p2 = self.current_match
        self.bot.events.has_gone.update([p1.id, p2.id])

        # Staff briefing: Get records
        _, r1 = await self.bot.points.get_stats(p1.id)
        _, r2 = await self.bot.points.get_stats(p2.id)

        embed = discord.Embed(title="⚔️ Next Battle Ready", color=discord.Color.red())
        embed.add_field(name=p1.display_name, value=f"Record: {r1 or 'Clean'}")
        embed.add_field(name=p2.display_name, value=f"Record: {r2 or 'Clean'}")
        
        await interaction.response.send_message(f"Upcoming: {p1.mention} vs {p2.mention}", embed=embed)

    @app_commands.command(name="vote", description="Start voting for the winner")
    async def start_vote(self, interaction: discord.Interaction):
        if len(self.current_match) < 2:
            return await interaction.response.send_message("No active match!", ephemeral=True)

        p1, p2 = self.current_match
        view = RoastVotingView(self.bot, p1, p2)
        await interaction.response.send_message(f"🗳️ **VOTING STARTED!**\n🔵 {p1.mention}\n🟢 {p2.mention}", view=view)
        
        await view.wait()
        v1, v2 = view.votes[p1.id], view.votes[p2.id]
        
        winner = p1 if v1 > v2 else p2
        # Award 2 points (1 for stage + 1 for win)
        new_total = await self.bot.points.add_points(winner.id, 2)
        
        await interaction.channel.send(f"🏆 {winner.mention} wins with `{max(v1, v2)}` votes! Total Points: `{new_total}`")

async def setup(bot):
    await bot.add_cog(RoastCog(bot))