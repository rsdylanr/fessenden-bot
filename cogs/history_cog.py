import discord
from discord.ext import commands
import aiohttp
import random

class HistoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://history.muffinlabs.com/date"

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ MuffinLabs History System (Hybrid) Online!")

    async def fetch_history_data(self, month: int = None, day: int = None):
        """Fetches the raw JSON history data from MuffinLabs."""
        url = self.api_url
        if month and day:
            url = f"{self.api_url}/{month}/{day}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
            except Exception as e:
                print(f"❌ Error connecting to History API: {e}")
                return None

    @commands.hybrid_command(name="history", description="View historical events, births, or deaths for today or a specific date.")
    async def history(self, ctx, category: str = "events", month: int = None, day: int = None):
        """
        Pulls history data. 
        Category options: events, births, deaths
        """
        await ctx.defer() # ⏱️ Prevents Discord timeout while fetching data

        # 1. Validation for manual dates
        if month and (month < 1 or month > 12):
            return await ctx.send("❌ Month must be between 1 and 12.")
        if day and (day < 1 or day > 31):
            return await ctx.send("❌ Day must be between 1 and 31.")

        # 2. Fetch data
        data = await self.fetch_history_data(month, day)
        if not data or "data" not in data:
            return await ctx.send("❌ Could not retrieve historical data. Please try again later.")

        # 3. Choose category (Defaults to Events)
        category_map = {"events": "Events", "births": "Births", "deaths": "Deaths"}
        cat_key = category_map.get(category.lower(), "Events")
        
        items = data["data"].get(cat_key, [])
        if not items:
            return await ctx.send(f"🤷 No items found in the `{cat_key}` category for this date.")

        # We reverse it so it goes from Modern History ➔ Ancient History (or vice-versa)
        items.reverse() 
        date_title = data.get("date", "Today in History")

        # 4. Define our UI callback to push to your `UIService.create_pagination_view`
        async def render_page(interaction: discord.Interaction, page_items, current_page, total_pages, view):
            embed = discord.Embed(
                title=f"📜 {date_title} - {cat_key} (Page {current_page}/{total_pages})",
                color=discord.Color.dark_gold()
            )

            for item in page_items:
                year = item.get("year", "N/A")
                text = item.get("text", "No details")
                # Truncate if Wikipedia dumps an insanely long text
                clean_text = text[:300] + "..." if len(text) > 300 else text
                embed.add_field(name=f"🗓️ Year {year}", value=clean_text, inline=False)

            if interaction.response.is_done():
                await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=view)
            else:
                await interaction.response.send_message(embed=embed, view=view)

        # 5. Build the view with the UI Service you just built!
        if hasattr(self.bot, 'ui'):
            paginated_view = self.bot.ui.create_pagination_view(
                items=items,
                items_per_page=5, # 5 history items per page looks cleanest
                callback=render_page
            )
            # Sends the first page
            await paginated_view.send_initial_page(ctx)
        else:
            # Fallback if UI service is broken or offline: Pick a random event and dump it
            item = random.choice(items)
            embed = discord.Embed(
                title=f"📜 {date_title} - Random {cat_key}",
                description=f"**Year {item.get('year')}**:\n{item.get('text')}",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HistoryCog(bot))
