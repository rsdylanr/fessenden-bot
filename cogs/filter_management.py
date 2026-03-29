import discord
from discord import app_commands
from discord.ext import commands

class FilterManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="filter_add", description="Add a word to the filter cloud")
    @app_commands.describe(path="e.g. Offensive/Slurs", word="The word to ban")
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_add(self, interaction: discord.Interaction, path: str, word: str):
        node = self.bot.filter.get_node(path)
        if not node:
            return await interaction.response.send_message(f"❌ Path `{path}` not found.", ephemeral=True)

        if "Words" not in node: node["Words"] = []
        node["Words"].append(word)
        
        await self.bot.filter.save()
        await interaction.response.send_message(f"✅ Added `{word}` to `{path}`.", ephemeral=True)

    @app_commands.command(name="filter_list", description="View words in a specific category")
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_list(self, interaction: discord.Interaction, path: str):
        node = self.bot.filter.get_node(path)
        if not node or "Words" not in node:
            return await interaction.response.send_message("❌ Category empty or not found.", ephemeral=True)
        
        words_list = ", ".join(node["Words"])
        await interaction.response.send_message(f"📁 **{path}**: {words_list}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(FilterManagement(bot))
