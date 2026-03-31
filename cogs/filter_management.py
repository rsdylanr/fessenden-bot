import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class FilterManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def path_autocomplete(self, interaction: discord.Interaction, current: str):
        all_paths = self.bot.filter.get_all_paths()
        return [
            app_commands.Choice(name=p, value=p)
            for p in all_paths if current.lower() in p.lower()
        ][:25]

    @app_commands.command(name="filter_test", description="Admin Diagnostic: Test a string against the filter layers")
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_test(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(ephemeral=True)
        
        # 1. Filter Match
        found_word, category = self.bot.filter.get_match(text)
        
        # 2. Sentiment Check
        sentiment_info = "N/A"
        if len(text) > 5:
            res = await self.bot.context._query_sentiment(text)
            if res:
                sentiment_info = "\n".join([f"• {l['label']}: {round(l['score']*100)}%" for l in res[:3]])

        embed = discord.Embed(title="🔍 Filter Diagnostic", color=0x3498db)
        embed.add_field(name="Input", value=f"```{text}```", inline=False)
        
        if found_word:
            embed.add_field(name="Verdict", value="❌ **MATCHED**", inline=True)
            embed.add_field(name="Details", value=f"Word: `{found_word}`\nNode: `{category}`", inline=True)
        else:
            embed.add_field(name="Verdict", value="✅ **CLEAN**", inline=True)

        embed.add_field(name="Sentiment Engine", value=f"```{sentiment_info}```", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="filter_bulk_add", description="Import a list of words (comma or newline separated)")
    @app_commands.autocomplete(path=path_autocomplete)
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_bulk(self, interaction: discord.Interaction, path: str, words: str):
        await interaction.response.defer(ephemeral=True)
        
        node = self.bot.filter.get_node(path)
        if not node:
            return await interaction.followup.send(f"❌ Path `{path}` not found.")

        raw_list = words.replace("\n", ",").split(",")
        cleaned = [w.strip().lower() for w in raw_list if w.strip()]
        
        if "Words" not in node: node["Words"] = []
        
        added = 0
        for w in cleaned:
            if w not in node["Words"]:
                node["Words"].append(w)
                added += 1
        
        await self.bot.filter.save()
        await interaction.followup.send(f"✅ Imported {added} words to `{path}`.", ephemeral=True)

    @app_commands.command(name="filter_add", description="Add a single word to the filter")
    @app_commands.autocomplete(path=path_autocomplete)
    @app_commands.checks.has_permissions(administrator=True)
    async def filter_add(self, interaction: discord.Interaction, path: str, word: str):
        node = self.bot.filter.get_node(path)
        if not node: return await interaction.response.send_message("❌ Path invalid.", ephemeral=True)
        
        if "Words" not in node: node["Words"] = []
        word = word.lower().strip()
        
        if word not in node["Words"]:
            node["Words"].append(word)
            await self.bot.filter.save()
            await interaction.response.send_message(f"✅ Added `{word}` to `{path}`.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Word already exists.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(FilterManagement(bot))
