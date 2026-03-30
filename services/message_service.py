import discord
import uuid
from discord.ext import commands

class MessageService:
    def __init__(self, bot):
        self.bot = bot
        self.color_main = 0x3498db
        # Standardized Ref ID Footer
        self.footer_template = "System Ref: {ref} | Fessenden Framework"

    def generate_ref(self):
        """Phase 4: Unique Interaction IDs for log lookup."""
        return str(uuid.uuid4())[:8].upper()

    async def paginate(self, ctx, title, items, items_per_page=5):
        """Phase 2: Smart Pagination & Menus."""
        pages = [items[i:i + items_per_page] for i in range(0, len(items), items_per_page)]
        if not pages:
            return await ctx.send("The list is empty.")

        current_page = 0
        ref_id = self.generate_ref()

        def create_embed(page_index):
            embed = discord.Embed(title=title, color=self.color_main)
            content = "\n".join([f"• {item}" for item in pages[page_index]])
            embed.description = content
            embed.set_footer(text=f"Page {page_index + 1}/{len(pages)} | {self.footer_template.format(ref=ref_id)}")
            return embed

        class PaginationView(discord.ui.View):
            def __init__(self, timeout=60):
                super().__init__(timeout=timeout)

            @discord.ui.button(label="⬅️", style=discord.ButtonStyle.gray)
            async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
                nonlocal current_page
                if current_page > 0:
                    current_page -= 1
                    await interaction.response.edit_message(embed=create_embed(current_page), view=self)

            @discord.ui.button(label="➡️", style=discord.ButtonStyle.gray)
            async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                nonlocal current_page
                if current_page < len(pages) - 1:
                    current_page += 1
                    await interaction.response.edit_message(embed=create_embed(current_page), view=self)

        await ctx.send(embed=create_embed(current_page), view=PaginationView())
