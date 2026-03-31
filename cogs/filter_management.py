import discord
from discord import app_commands
from discord.ext import commands

class FilterManagement(commands.Cog):
    """
    Fessenden Framework: Cloud Filter Controller
    Manages the recursive JSON tree stored in Supabase.
    """
    def __init__(self, bot):
        self.bot = bot

    # --- AUTOCOMPLETE LOGIC ---
    async def path_autocomplete(self, interaction: discord.Interaction, current: str):
        """Fetches all valid recursive paths from the FilterService."""
        try:
            all_paths = self.bot.filter.get_all_paths()
            return [
                app_commands.Choice(name=path, value=path)
                for path in all_paths if current.lower() in path.lower()
            ][:25]
        except Exception:
            return []

    # --- COMMANDS ---

    @app_commands.command(name="filter_add", description="Add a word to the filter cloud")
    @app_commands.describe(path="The category path (e.g. Offensive/Slurs)", word="The word to ban")
    @app_commands.autocomplete(path=path_autocomplete)
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_add(self, interaction: discord.Interaction, path: str, word: str):
        await interaction.response.defer(ephemeral=True)
        
        node = self.bot.filter.get_node(path)
        if not node:
            return await interaction.followup.send(f"❌ Path `{path}` not found in the cloud tree.", ephemeral=True)

        if "Words" not in node:
            node["Words"] = []
        
        clean_word = word.lower().strip()
        if clean_word in node["Words"]:
            return await interaction.followup.send(f"ℹ️ `{clean_word}` is already in `{path}`.", ephemeral=True)

        # Update local tree
        node["Words"].append(clean_word)
        
        # Sync to Supabase
        try:
            await self.bot.filter.save()
            # Refresh local memory from DB to ensure alignment
            await self.bot.filter.sync()
            await interaction.followup.send(f"✅ Added `{clean_word}` to `{path}`. Filter is live.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Database Error: {e}", ephemeral=True)

    @app_commands.command(name="filter_remove", description="Remove a word from the filter cloud")
    @app_commands.autocomplete(path=path_autocomplete)
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_remove(self, interaction: discord.Interaction, path: str, word: str):
        await interaction.response.defer(ephemeral=True)
        
        node = self.bot.filter.get_node(path)
        if not node or "Words" not in node:
            return await interaction.followup.send(f"❌ Path `{path}` not found or has no words.", ephemeral=True)

        clean_word = word.lower().strip()
        if clean_word in node["Words"]:
            node["Words"].remove(clean_word)
            await self.bot.filter.save()
            await self.bot.filter.sync()
            await interaction.followup.send(f"🗑️ Removed `{clean_word}` from `{path}`.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ `{clean_word}` not found in `{path}`.", ephemeral=True)

    @app_commands.command(name="filter_list", description="View all words in a specific category")
    @app_commands.autocomplete(path=path_autocomplete)
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_list(self, interaction: discord.Interaction, path: str):
        node = self.bot.filter.get_node(path)
        if not node:
            return await interaction.response.send_message(f"❌ Path `{path}` not found.", ephemeral=True)
        
        words = node.get("Words", [])
        regex = node.get("Regex", [])
        
        embed = discord.Embed(title=f"🛡️ Filter Path: {path}", color=0x3498db)
        
        word_str = ", ".join([f"`{w}`" for w in words]) if words else "*None*"
        regex_str = ", ".join([f"`{r}`" for r in regex]) if regex else "*None*"
        
        embed.add_field(name="Words", value=word_str, inline=False)
        embed.add_field(name="Regex Patterns", value=regex_str, inline=False)
        embed.set_footer(text=f"Fessenden Content Filter v2 | Total Words: {len(words)}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="filter_sync", description="Force a manual sync with the Supabase cloud")
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_sync(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.bot.filter.sync()
        await interaction.followup.send("🔄 Filter tree synchronized with Supabase.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(FilterManagement(bot))
