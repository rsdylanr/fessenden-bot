import discord
from discord.ext import commands
import asyncio

class TriviaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Trivia System (Hybrid) Online!")

    @commands.hybrid_command(name="trivia", description="Play a game of trivia and earn merits!")
    async def trivia(self, ctx):
        """Starts a trivia game in the channel."""
        await ctx.defer() # ⏱️ Tells Discord: "Give me a second to grab a question!"

        # 1. Grab a question from your TriviaService
        question_data = await self.bot.trivia.get_question()
        if not question_data:
            return await ctx.send("❌ Failed to fetch a trivia question. Try again later!")

        question = question_data['question']
        correct_answer = question_data['correct_answer']
        category = question_data['category']

        embed = discord.Embed(
            title=f"🧠 Trivia Time! ({category})",
            description=f"**Question:** {question}\n\nType your answer in the chat! You have 30 seconds.",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

        # 2. Wait for a user to type the answer
        def check(m):
            return m.channel == ctx.channel and not m.author.bot

        try:
            while True:
                guess_msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                
                if guess_msg.content.lower() == correct_answer.lower():
                    # 🎉 Reward them with Merits in Supabase!
                    await ctx.send(f"✅ {guess_msg.author.mention} got it right! The answer was **{correct_answer}**. You earned 5 Merits!")
                    break
                    
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Times up! Nobody got it. The correct answer was **{correct_answer}**.")


async def setup(bot):
    await bot.add_cog(TriviaCog(bot))
