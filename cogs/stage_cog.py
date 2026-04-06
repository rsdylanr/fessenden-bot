import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class StageEvents(commands.GroupCog, name="stage"):
    """
    Consolidated Stage Management System.
    Features: Speaking Tokens, Hard-Caps, and Interruption Tracking.
    """
    def __init__(self, bot, stage_service):
        self.bot = bot
        self.stage = stage_service
        super().__init__()

    # --- Feature #1 & #2: Join & Cooldowns ---
    @app_commands.command(name="join", description="Join the Speaking Token Queue")
    async def join(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if self.stage.is_on_cooldown(user_id):
            return await interaction.response.send_message("⏳ Buffer active. Wait for your cooldown.", ephemeral=True)

        if self.stage.add_to_queue(interaction.channel_id, user_id):
            await interaction.response.send_message(f"✅ {interaction.user.mention} is now in the queue.")
        else:
            await interaction.response.send_message("❌ You are already in the queue.", ephemeral=True)

    # --- Feature #5: Hard-Cap Timer (Changeable Every Time) ---
    @app_commands.command(name="next", description="Move to the next speaker with custom rules")
    @app_commands.describe(limit="Speaker time limit (sec)", buffer="Silence buffer (sec)")
    @app_commands.checks.has_permissions(mute_members=True)
    async def next_speaker(self, interaction: discord.Interaction, limit: int = 90, buffer: int = 30):
        await interaction.response.defer()
        cid = interaction.channel_id
        self.stage.update_config(limit, buffer)

        # Handle Previous Speaker
        prev_id = self.stage.current_speakers.get(cid)
        if prev_id:
            pm = interaction.guild.get_member(prev_id)
            if pm:
                try: await pm.edit(suppress=True)
                except: pass
                self.stage.set_cooldown(prev_id, buffer)

        # Assign Next Speaker
        next_id = self.stage.get_next(cid)
        if not next_id:
            return await interaction.followup.send("📢 Queue empty.")

        nm = interaction.guild.get_member(next_id)
        if nm:
            await nm.edit(suppress=False)
            await interaction.followup.send(f"🎙️ **{nm.display_name}** is now speaking ({limit}s).")
            
            # Hard-Cap Enforcement
            await asyncio.sleep(limit)
            if self.stage.current_speakers.get(cid) == next_id:
                await nm.edit(suppress=True)
                await interaction.channel.send(f"⏱️ Time up for {nm.display_name}.")

    # --- Feature #6: Interruption Tracker ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or not isinstance(after.channel, discord.StageChannel):
            return

        current_token = self.stage.current_speakers.get(after.channel.id)
        # If user unmuted without the Token
        if before.suppress and not after.suppress and member.id != current_token:
            count = self.stage.log_interruption(member.id)
            await member.edit(suppress=True)
            await after.channel.send(f"⚠️ {member.mention}, wait for your token! (Infraction #{count})", delete_after=5)

    @app_commands.command(name="end", description="Clear all session data")
    @app_commands.checks.has_permissions(mute_members=True)
    async def end_session(self, interaction: discord.Interaction):
        self.stage.reset_session(interaction.channel_id)
        await interaction.response.send_message("🛑 Session ended. All stats cleared.")
