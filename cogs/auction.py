import discord
from discord.ext import commands
import asyncio
import time

class AuctionView(discord.ui.View):
    """
    Phase 3: The Auction House
    Features a 'Penny Auction' logic where late bids reset the timer.
    """
    def __init__(self, message_service, item_name, starting_bid):
        super().__init__(timeout=None)
        self.message_service = message_service
        self.item_name = item_name
        self.current_bid = starting_bid
        self.highest_bidder = None
        self.end_time = time.time() + 60  # Initial 60-second auction
        self.active = True

    def get_time_remaining(self):
        remaining = self.end_time - time.time()
        return max(0, int(remaining))

    def create_embed(self):
        ref = self.message_service.generate_ref()
        color = 0x3498db if self.active else 0x2ecc71
        
        embed = discord.Embed(
            title=f"🔨 Auction: {self.item_name}",
            description=f"Current Bid: **{self.current_bid} Points**\n"
                        f"Highest Bidder: {self.highest_bidder.mention if self.highest_bidder else 'None'}",
            color=color
        )
        
        status = f"⏳ Ends in: {self.get_time_remaining()}s" if self.active else "✅ Auction Closed"
        embed.add_field(name="Status", value=status)
        embed.set_footer(text=f"Ref: {ref} | Fessenden Economy")
        return embed

    async def update_auction(self, interaction: discord.Interaction):
        # Phase 3: Penny Auction Logic
        # If bid is placed in the last 10 seconds, reset timer to 15 seconds
        time_left = self.get_time_remaining()
        if time_left <= 10:
            self.end_time = time.time() + 15
        
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="+10", style=discord.ButtonStyle.green)
    async def bid_10(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_bid += 10
        self.highest_bidder = interaction.user
        await self.update_auction(interaction)

    @discord.ui.button(label="+50", style=discord.ButtonStyle.green)
    async def bid_50(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_bid += 50
        self.highest_bidder = interaction.user
        await self.update_auction(interaction)

class Auction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="auction")
    async def start_auction(self, ctx, item: str, starting_price: int = 100):
        """Starts a live bidding war for an item."""
        view = AuctionView(self.bot.message_service, item, starting_price)
        msg = await ctx.send(embed=view.create_embed(), view=view)
        
        # Background loop to handle the "Tick" and the "Closing"
        while view.get_time_remaining() > 0:
            await asyncio.sleep(5)
            try:
                await msg.edit(embed=view.create_embed())
            except:
                break
        
        # Auction Finish
        view.active = False
        for child in view.children:
            child.disabled = True
            
        await msg.edit(embed=view.create_embed(), view=view)
        
        if view.highest_bidder:
            await ctx.send(f"🎊 **Sold!** {view.item_name} goes to {view.highest_bidder.mention} for {view.current_bid}!")
        else:
            await ctx.send(f"😔 The auction for {view.item_name} ended with no bids.")

async def setup(bot):
    await bot.add_cog(Auction(bot))
