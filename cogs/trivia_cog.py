import discord
from discord.ext import commands
from discord import app_commands
import random

class TriviaView(discord.ui.View):
    def __init__(self, bot, data, user_id, streak=0):
        super().__init__(timeout=15)
        self.bot = bot
        self.user_id = user_id
        self.correct_ans = data['correct']
        self.streak = streak
        self.answered = False

    async def handle_ans(self, interaction: discord.Interaction, choice: str):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ This isn't your round!", ephemeral=True)
        
        if self.answered: return
        self.answered = True
        self.stop()

        if choice == self.correct_ans:
            self.streak += 1
            await self.bot.points.add_points(self.user_id, 1)
            
            await self.update_best_streak()
            
            next_view = discord.ui.View()
            next_btn = discord.ui.Button(label="Next Question ➡️", style=discord.ButtonStyle.success)
            async def next_callback(i: discord.Interaction):
                await i.response.defer()
                cog = self.bot.get_cog("TriviaCog")
                await cog.start_trivia_round(i, self.streak)
            next_btn.callback = next_callback
            next_view.add_item(next_btn)

            await interaction.response.edit_message(content=f"✅ **Correct!** Streak: `{self.streak}`", view=next_view)
        else:
            restart_view = discord.ui.View()
            restart_btn = discord.ui.Button(label="Try Again 🔄", style=discord.ButtonStyle.danger)
            async def restart_callback(i: discord.Interaction):
                await i.response.defer()
                cog = self.bot.get_cog("TriviaCog")
                await cog.start_trivia_round(i, 0)
            restart_btn.callback = restart_callback
            restart_view.add_item(restart_btn)

            await interaction.response.edit_message(content=f"❌ **Wrong!** Answer: **{self.correct_ans}**", view=restart_view)

    async def update_best_streak(self):
        res = await self.bot.db.run_query("SELECT records FROM users WHERE user_id = ?", (self.user_id,))
        # (Simplified for this full file copy)
        pass

class TriviaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    trivia_group = app_commands.Group(name="trivia", description="Trivia marathon commands")

    async def start_trivia_round(self, interaction, streak=0):
        # Prevent timeout by telling Discord we are working
        if not interaction.response.is_done():
            await interaction.response.defer()

        diff = "easy"
        if streak > 12: diff = "hard"
        elif streak > 5: diff = "medium"

        data = await self.bot.trivia.get_question(difficulty=diff)
        
        view = TriviaView(self.bot, data, interaction.user.id, streak)
        options = data['all']
        random.shuffle(options)
        
        for opt in options:
            btn = discord.ui.Button(label=opt[:80], style=discord.ButtonStyle.secondary)
            btn.callback = lambda i, c=opt: view.handle_ans(i, c)
            view.add_item(btn)

        msg = f"**Difficulty: {diff.upper()}** | **Question {streak + 1}:**\n{data['q']}"
        await interaction.followup.send(msg, view=view)

    @trivia_group.command(name="start", description="Start a new trivia marathon")
    async def trivia_start(self, interaction: discord.Interaction):
        await self.start_trivia_round(interaction)

async def setup(bot):
    await bot.add_cog(TriviaCog(bot))