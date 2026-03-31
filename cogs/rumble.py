import discord
from discord.ext import commands
import random
import asyncio

class RumbleRoyale(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Phase 4: Humorous death messages
        self.death_messages = [
            "{victim} was poked to death by {killer} with a stick.",
            "{victim} tried to swim in lava while fleeing from {killer}.",
            "{victim} forgot how to breathe while looking at {killer}.",
            "{victim} was struck by lightning. {killer} claims it was intentional.",
            "{victim} fell from a high place after {killer} greased the ledge.",
            "{victim} was run over by a rogue minecart driven by {killer}.",
            "{victim} died of embarrassment after missing a shot at {killer}.",
            "{victim} was " "accidentally" " pushed into a pit by {killer}."
        ]
        self.solo_deaths = [
            "{victim} ate a suspicious stew and didn't make it.",
            "{victim} fell out of the world.",
            "{victim} tried to sleep in the Nether.",
            "{victim} was blown up by a creeper."
        ]

    @commands.command(name="rumble")
    async def start_rumble(self, ctx, *, players: str):
        """Starts a battle royale. Usage: !rumble Player1, Player2, Player3..."""
        # Split by comma and clean up whitespace
        entrants = [p.strip() for p in players.split(",") if p.strip()]
        
        if len(entrants) < 2:
            return await self.bot.message_service.send_localized(ctx, "RUMBLE_MIN_PLAYERS", type="error")

        tx = self.bot.message_service.start_transaction()
        ref = self.bot.message_service.generate_ref()
        
        # Phase 2: Loading State
        header_embed = discord.Embed(
            title="⚔️ RUMBLE ROYALE",
            description=f"**Entrants:** {', '.join(entrants)}\n\n*The battle begins now...*",
            color=0xe67e22
        )
        header_embed.set_footer(text=f"Ref: {ref} | Fessenden Arena")
        msg = await ctx.send(embed=header_embed)
        tx.add(msg)

        await asyncio.sleep(3)

        while len(entrants) > 1:
            await asyncio.sleep(2) # Speed of the kill feed
            
            # Determine if it's a PVP kill or an accidental solo death
            if random.random() > 0.2 and len(entrants) >= 2:
                killer = random.choice(entrants)
                victim = random.choice([p for p in entrants if p != killer])
                event = random.choice(self.death_messages).format(killer=f"**{killer}**", victim=f"**{victim}**")
                entrants.remove(victim)
            else:
                victim = random.choice(entrants)
                event = random.choice(self.solo_deaths).format(victim=f"**{victim}**")
                entrants.remove(victim)

            # Phase 1: Real-time updates using the footer for the Ref ID
            feed_embed = discord.Embed(
                title="🩸 Kill Feed",
                description=event,
                color=0xe74c3c
            )
            feed_embed.add_field(name="Survivors Remaining", value=str(len(entrants)))
            feed_embed.set_footer(text=f"Ref: {ref}")
            
            await ctx.send(embed=feed_embed)

        # 🏁 Winner Announcement
        winner = entrants[0]
        winner_embed = discord.Embed(
            title="🏆 CHAMPION FOUND",
            description=f"The dust settles and only **{winner}** stands victorious!",
            color=0x2ecc71
        )
        winner_embed.set_thumbnail(url="https://i.imgur.com/vH3yF0u.png") # Gold Trophy Icon
        winner_embed.set_footer(text=f"Ref: {ref}")
        
        await ctx.send(embed=winner_embed)

async def setup(bot):
    await bot.add_cog(RumbleRoyale(bot))
