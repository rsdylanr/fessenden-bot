import discord
from discord.ext import commands
import asyncio

class MessageService:
    def __init__(self, bot):
        self.bot = bot
        # Phase 1: Standardized Colors
        self.color_info = 0x3498db
        self.color_success = 0x2ecc71
        self.color_error = 0xe74c3c
        self.footer_text = "Fessenden System | Ref: {ref}"

    def _generate_ref(self):
        """Phase 4: Unique Interaction IDs for debugging."""
        import uuid
        return str(uuid.uuid4())[:8].upper()

    async def send_success(self, ctx, text, delete_after=None):
        """Phase 1 & 2: Standardized Success UI with auto-delete."""
        ref = self._generate_ref()
        embed = discord.Embed(description=f"✅ {text}", color=self.color_success)
        embed.set_footer(text=self.footer_text.format(ref=ref))
        return await ctx.send(embed=embed, delete_after=delete_after)

    async def send_error(self, ctx, text, delete_after=10):
        """Phase 3: Permission Pre-Flight & Fallback."""
        ref = self._generate_ref()
        embed = discord.Embed(description=f"❌ {text}", color=self.color_error)
        embed.set_footer(text=self.footer_text.format(ref=ref))
        
        try:
            return await ctx.send(embed=embed, delete_after=delete_after)
        except discord.Forbidden:
            # Fallback to plain text if embeds are blocked in the channel
            return await ctx.send(f"ERROR [{ref}]: {text}", delete_after=delete_after)

    async def prompt_choice(self, ctx, question, options):
        """Phase 2: Interaction Waiter (Buttons)."""
        view = discord.ui.View(timeout=30)
        chosen_option = None

        for option in options:
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.gray)
            
            async def callback(interaction, opt=option):
                nonlocal chosen_option
                chosen_option = opt
                await interaction.response.defer()
                view.stop()
                
            button.callback = callback
            view.add_item(button)

        embed = discord.Embed(description=question, color=self.color_info)
        msg = await ctx.send(embed=embed, view=view)
        
        await view.wait()
        await msg.delete() # Phase 2: Self-destruct after choice
        return chosen_option

    async def progress_bar(self, current, total, length=10):
        """Phase 5: Visual Progress Bar Utility."""
        percent = float(current) / total
        arrow = "▰" * int(round(percent * length))
        spaces = "▱" * (length - len(arrow))
        return f"[{arrow}{spaces}] {int(percent * 100)}%"
