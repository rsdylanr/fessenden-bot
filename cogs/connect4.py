import discord
from discord.ext import commands
import random

class MineButton(discord.ui.Button):
    def __init__(self, x, y, is_mine):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y
        self.is_mine = is_mine

    async def callback(self, interaction: discord.Interaction):
        view: GlobalMinesweeperView = self.view
        
        if self.is_mine:
            # PHASE 3: BOOM! Reset logic
            self.style = discord.ButtonStyle.danger
            self.label = "💥"
            await view.explode(interaction, f"{interaction.user.display_name} hit a mine!")
        else:
            # Safe click
            self.style = discord.ButtonStyle.success
            self.label = "💎" # Fessenden Theme: Diamonds instead of numbers
            self.disabled = True
            view.safe_clicks += 1
            
            if view.check_win():
                await view.explode(interaction, "🏆 The board has been cleared! Gems for everyone!")
            else:
                await interaction.response.edit_message(view=view)

class GlobalMinesweeperView(discord.ui.View):
    """
    Phase 1: Persistent Global Minesweeper
    A 5x5 grid where any user can participate.
    """
    def __init__(self, message_service):
        super().__init__(timeout=None) # Persistent until a mine hits
        self.message_service = message_service
        self.safe_clicks = 0
        self.total_safe_spots = 20 # 25 total - 5 mines
        
        # Initialize 5x5 Grid
        mine_locs = random.sample(range(25), 5)
        for i in range(25):
            x, y = i % 5, i // 5
            is_mine = i in mine_locs
            self.add_item(MineButton(x, y, is_mine))

    def check_win(self):
        return self.safe_clicks >= self.total_safe_spots

    async def explode(self, interaction, result_text):
        # Disable all buttons and show mines
        for child in self.children:
            child.disabled = True
            if child.is_mine:
                child.label = "💣"
                child.style = discord.ButtonStyle.danger
        
        ref = self.message_service.generate_ref()
        embed = discord.Embed(title="Global Minesweeper: RESET", description=result_text, color=0xe74c3c)
        embed.set_footer(text=f"Ref: {ref} | Resetting board soon...")
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

class GlobalMinesweeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="minesweeper")
    async def start_minesweeper(self, ctx):
        """Spawns a global minesweeper board."""
        # Phase 4: Localization for the starter message
        description = self.bot.localization.get("MINESWEEPER_START") if hasattr(self.bot, "localization") else "Click a tile to find gems. Hit a mine and the board resets for everyone!"
        
        view = GlobalMinesweeperView(self.bot.message_service)
        
        embed = discord.Embed(
            title="🧨 Global Minesweeper",
            description=description,
            color=0x3498db
        )
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(GlobalMinesweeper(bot))
