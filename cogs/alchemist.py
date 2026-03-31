import discord
from discord.ext import commands

class AlchemistView(discord.ui.View):
    """
    Phase 3: Logic Puzzle / Recipe Combination
    Users select two emojis to 'craft' a third result.
    """
    def __init__(self, message_service, user):
        super().__init__(timeout=60)
        self.message_service = message_service
        self.user = user
        self.ingredient_a = None
        self.ingredient_b = None
        
        # Simple Recipe Book (Key: sorted tuple of ingredients)
        self.recipes = {
            tuple(sorted(["🔥", "💧"])): "💨 (Steam)",
            tuple(sorted(["🔥", "🧱"])): "🌋 (Lava)",
            tuple(sorted(["💧", "🌱"])): "🌳 (Tree)",
            tuple(sorted(["💨", "❄️"])): "🌪️ (Blizzard)",
            tuple(sorted(["🪵", "🔥"])): "🕯️ (Torch)",
            tuple(sorted(["⚡", "🤖"])): "🔌 (Powered Bot)"
        }

    def get_embed(self, result=None):
        ref = self.message_service.generate_ref()
        description = "Select two elements to combine them!"
        if result:
            description = f"### 🧪 Synthesis Result:\n{self.ingredient_a} + {self.ingredient_b} = **{result}**"
        
        embed = discord.Embed(
            title="⚗️ Emoji Alchemist",
            description=description,
            color=0x9b59b6 # Purple for Alchemy
        )
        embed.add_field(name="Selected A", value=self.ingredient_a or "None", inline=True)
        embed.add_field(name="Selected B", value=self.ingredient_b or "None", inline=True)
        embed.set_footer(text=f"Ref: {ref} | Experimenting as {self.user.display_name}")
        return embed

    @discord.ui.select(
        placeholder="Choose Ingredient A...",
        options=[
            discord.SelectOption(label="Fire", emoji="🔥"),
            discord.SelectOption(label="Water", emoji="💧"),
            discord.SelectOption(label="Wind", emoji="💨"),
            discord.SelectOption(label="Earth", emoji="🧱"),
            discord.SelectOption(label="Plant", emoji="🌱"),
            discord.SelectOption(label="Wood", emoji="🪵")
        ]
    )
    async def select_a(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your lab!", ephemeral=True)
        self.ingredient_a = select.values[0]
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.select(
        placeholder="Choose Ingredient B...",
        options=[
            discord.SelectOption(label="Fire", emoji="🔥"),
            discord.SelectOption(label="Water", emoji="💧"),
            discord.SelectOption(label="Ice", emoji="❄️"),
            discord.SelectOption(label="Robot", emoji="🤖"),
            discord.SelectOption(label="Lightning", emoji="⚡"),
            discord.SelectOption(label="Earth", emoji="🧱")
        ]
    )
    async def select_b(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your lab!", ephemeral=True)
        self.ingredient_b = select.values[0]
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Transmute!", style=discord.ButtonStyle.success, row=4)
    async def combine(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.ingredient_a or not self.ingredient_b:
            return await interaction.response.send_message("You need two ingredients!", ephemeral=True)
        
        recipe_key = tuple(sorted([self.ingredient_a, self.ingredient_b]))
        result = self.recipes.get(recipe_key, "💥 (Explosion - No Recipe Found)")
        
        # Phase 2: Edit current state to show result
        await interaction.response.edit_message(embed=self.get_embed(result=result), view=None)
        self.stop()

class Alchemist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="alchemy")
    async def start_alchemy(self, ctx):
        """Opens the Alchemist lab for the user."""
        view = AlchemistView(self.bot.message_service, ctx.author)
        await ctx.send(embed=view.get_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Alchemist(bot))
