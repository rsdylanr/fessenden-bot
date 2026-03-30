import discord
from discord.ext import commands
import asyncio
import random
import time

class ReactionButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=10.0)
        self.start_time = None
        self.winner = None
        self.elapsed = None

    @discord.ui.button(label="CLICK ME!", style=discord.ButtonStyle.green)
    async def click_me(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.elapsed = time.time() - self.start_time
        self.winner = interaction.user
        
        button.disabled = True
        button.label = f"Winner: {self.winner.display_name}"
        await interaction.response.edit_message(view=self)
        self.stop()

class SkillTests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reaction")
    async def reaction_test(self, ctx):
        embed = discord.Embed(
            title="🎯 Reaction Test",
            description="Get ready... the button will appear soon!",
            color=discord.Color.blue()
        )
        msg = await ctx.send(embed=embed)

        await asyncio.sleep(random.uniform(2, 7))

        view = ReactionButton()
        view.start_time = time.time()

        embed.description = "**CLICK NOW!!!**"
        embed.color = discord.Color.gold()
        await msg.edit(embed=embed, view=view)

        await view.wait()

        if view.winner:
            ms = round(view.elapsed, 3)
            await ctx.send(f"🏆 {view.winner.mention} reacted in **{ms}s**!")
            self.bot.stats.record_win(view.winner.id)
        else:
            await ctx.send("⏰ Time's up! No one reacted fast enough.")

async def setup(bot):
    await bot.add_cog(SkillTests(bot))
