import discord
import uuid
import os
import aiohttp
import asyncio
from io import BytesIO
from datetime import datetime

class MessageTransaction:
    """
    PHASE 3: ATOMIC TRANSACTIONS
    Tracks messages sent during a command session. 
    If a process fails, .rollback() wipes the evidence.
    """
    def __init__(self, service):
        self.service = service
        self.actions = []

    def add(self, message: discord.Message):
        if message:
            self.actions.append(message)
        return message

    async def rollback(self):
        for msg in self.actions:
            try:
                await msg.delete()
            except:
                pass
        self.actions.clear()

class ManagedView(discord.ui.View):
    """
    PHASE 5: VIEW GARBAGE COLLECTION
    Base class for all UI. Automatically disables buttons on timeout
    to save RAM and provide user feedback.
    """
    def __init__(self, timeout=60):
        super().__init__(timeout=timeout)
        self.message = None

    async def on_timeout(self):
        if self.message:
            try:
                for item in self.children:
                    item.disabled = True
                await self.message.edit(view=self)
            except:
                pass
        self.stop()

class MessageService:
    def __init__(self, bot):
        self.bot = bot
        # Phase 1: Standardized Branding
        self.colors = {
            "main": 0x3498db,
            "success": 0x2ecc71,
            "error": 0xe74c3c,
            "loading": 0xf1c40f
        }
        self.active_views = []

    # --- UTILITIES ---

    def generate_ref(self):
        """PHASE 4: UNIQUE INTERACTION IDS"""
        return str(uuid.uuid4())[:8].upper()

    def start_transaction(self):
        return MessageTransaction(self)

    def sanitize(self, text: str) -> str:
        """PHASE 5: MARKDOWN SANITIZER"""
        chars = ["*", "_", "`", "~", ">", "|", "\\"]
        for char in chars:
            text = text.replace(char, f"\\{char}")
        return text

    # --- CORE MESSAGING ---

    async def send_localized(self, ctx, key, type="main", delete_after=None, **kwargs):
        """PHASE 4: LOCALIZATION & STRING INJECTION"""
        ref = self.generate_ref()
        # Pulls from self.bot.localization (the strings.json handler)
        content = self.bot.localization.get(key, **kwargs)
        
        embed = discord.Embed(description=content, color=self.colors.get(type, 0x3498db))
        embed.set_footer(text=f"Ref: {ref} | Fessenden Framework")
        
        return await ctx.send(embed=embed, delete_after=delete_after)

    async def resilient_reply(self, ctx, transaction, error_key="GENERIC_ERROR"):
        """PHASE 5: FAULT TOLERANCE & HEARTBEAT"""
        ref = self.generate_ref()
        await transaction.rollback()
        
        text = self.bot.localization.get(error_key)
        embed = discord.Embed(title="⚠️ System Interruption", description=text, color=self.colors["error"])
        embed.set_footer(text=f"Error Ref: {ref}")
        
        await ctx.send(embed=embed, delete_after=20)
        print(f"🚨 [Ref: {ref}] Command failed in {ctx.command}")

    # --- MEDIA & ASSETS ---

    async def get_asset(self, path_or_url):
        """PHASE 3: ASSET MANAGER (Local vs URL)"""
        if path_or_url.startswith(("http://", "https://")):
            async with aiohttp.ClientSession() as session:
                async with session.get(path_or_url) as resp:
                    if resp.status != 200: return None
                    return discord.File(BytesIO(await resp.read()), filename="asset.png")
        
        if os.path.exists(path_or_url):
            return discord.File(path_or_url)
        return None

    # --- INTERACTION & UI ---

    async def paginate(self, ctx, title_key, items, items_per_page=5):
        """PHASE 2: SMART PAGINATION"""
        pages = [items[i:i + items_per_page] for i in range(0, len(items), items_per_page)]
        title = self.bot.localization.get(title_key)
        ref_id = self.generate_ref()

        def create_embed(idx):
            embed = discord.Embed(title=title, color=self.colors["main"])
            embed.description = "\n".join([f"• {item}" for item in pages[idx]])
            footer = self.bot.localization.get("PAGINATION_FOOTER", current=idx+1, total=len(pages), ref=ref_id)
            embed.set_footer(text=footer)
            return embed

        class Paginator(ManagedView):
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

        view = Paginator(create_embed)
        msg = await ctx.send(embed=create_embed(0), view=view)
        view.message = msg
        self.active_views.append(view)
