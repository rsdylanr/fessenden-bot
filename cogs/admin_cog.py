import discord
from discord.ext import commands
from discord import app_commands

class AdminCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    def has_power(self, i: discord.Interaction):
        return i.user.id == self.bot.owner_id_num or i.user.guild_permissions.administrator

    @app_commands.command(name="event_start")
    async def e_start(self, i: discord.Interaction, name: str, reward: int = 1):
        if not self.has_power(i): return await i.response.send_message("❌ No perms.", ephemeral=True)
        self.bot.events.start_tracking(name, reward)
        await i.response.send_message(f"🟢 Event **{name}** started!")

    @app_commands.command(name="event_stop")
    async def e_stop(self, i: discord.Interaction):
        if not self.has_power(i): return await i.response.send_message("❌ No perms.", ephemeral=True)
        ids = self.bot.events.get_eligible_users()
        for uid in ids: await self.bot.points.add_points(uid, self.bot.events.participation_reward)
        self.bot.events.is_active = False
        await i.response.send_message(f"🛑 Event stopped. {len(ids)} people rewarded.")

async def setup(bot): await bot.add_cog(AdminCog(bot))