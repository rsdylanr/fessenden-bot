import discord
import uuid
import os
import aiohttp
from io import BytesIO

class MessageTransaction:
    def __init__(self, service):
        self.service = service
        self.actions = []

    def add(self, message):
        if message: self.actions.append(message)
        return message

    async def rollback(self):
        for msg in self.actions:
            try: await msg.delete()
            except: pass
        self.actions.clear()

class MessageService:
    def __init__(self, bot):
        self.bot = bot
        self.color_main = 0x3498db
        self.color_success = 0x2ecc71
        self.color_error = 0xe74c3c
        # Note: We now pull footers and text from self.bot.localization

    def generate_ref(self):
        return str(uuid.uuid4())[:8].upper()

    def start_transaction(self):
        return MessageTransaction(self)

    async def send_localized_success(self, ctx, key, lang="en", delete_after=None, **kwargs):
        """Phase 4: Sends a success message using the Localization strings."""
        ref = self.generate_ref()
        text = self.bot.localization.get(key, lang, **kwargs)
        
        embed = discord.Embed(description=f"✅ {text}", color=self.color_success)
        embed.set_footer(text=f"Ref: {ref} | Fessenden")
        return await ctx.send(embed=embed, delete_after=delete_after)

    async def resilient_reply(self, ctx, transaction, error_key="GENERIC_ERROR", lang="en"):
        """Phase 5: Refined Error Handler with Localization."""
        ref = self.generate_ref()
        await transaction.rollback()
        
        text = self.bot.localization.get(error_key, lang)
        embed = discord.Embed(title="⚠️ System Interruption", description=text, color=self.color_error)
        embed.set_footer(text=f"Ref ID: {ref}")
        
        await ctx.send(embed=embed, delete_after=20)

    async def get_asset(self, path_or_url):
        if path_or_url.startswith(("http://", "https://")):
            async with aiohttp.ClientSession() as session:
                async with session.get(path_or_url) as resp:
                    if resp.status != 200: return None
                    return discord.File(BytesIO(await resp.read()), filename="asset.png")
        return discord.File(path_or_url) if os.path.exists(path_or_url) else None

    async def paginate(self, ctx, title_key, items, lang="en", items_per_page=5):
        """Phase 2 & 4: Paginate with localized titles."""
        pages = [items[i:i + items_per_page] for i in range(0, len(items), items_per_page)]
        title = self.bot.localization.get(title_key, lang)
        ref_id = self.generate_ref()

        def create_embed(idx):
            embed = discord.Embed(title=title, color=self.color_main)
            embed.description = "\n".join([f"• {item}" for item in pages[idx]])
            footer_text = self.bot.localization.get("PAGINATION_FOOTER", lang, current=idx+1, total=len(pages), ref=ref_id)
            embed.set_footer(text=footer_text)
            return embed

        class Paginator(discord.ui.View):
            def __init__(self, factory):
                super().__init__(timeout=60)
                self.index = 0
                self.factory = factory
            @discord.ui.button(label="⬅️", style=discord.ButtonStyle.gray)
            async def prev(self, intr, btn):
                if self.index > 0:
                    self.index -= 1
                    await intr.response.edit_message(embed=self.factory(self.index))
            @discord.ui.button(label="➡️", style=discord.ButtonStyle.gray)
            async def next(self, intr, btn):
                if self.index < len(pages) - 1:
                    self.index += 1
                    await intr.response.edit_message(embed=self.factory(self.index))

        await ctx.send(embed=create_embed(0), view=Paginator(create_embed))
