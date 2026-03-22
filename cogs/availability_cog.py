import discord
from discord.ext import commands
from services.time_service import TimeService

class AvailabilityModal(discord.ui.Modal, title="Set Availability Time"):
    start_time = discord.ui.TextInput(label="Start Time (e.g. 3:00 PM)", placeholder="3:30 PM", required=True)
    end_time = discord.ui.TextInput(label="End Time (e.g. 5:00 PM)", placeholder="5:00 PM", required=True)

    def __init__(self, day, bot):
        super().__init__()
        self.day = day
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        start = TimeService.parse_time(self.start_time.value)
        end = TimeService.parse_time(self.end_time.value)

        if not start or not end:
            await interaction.response.send_message("❌ Invalid time format! Please include AM or PM (e.g., 3:00 PM).", ephemeral=True)
            return

        # Pass viewing to the final Status Buttons
        view = StatusSelectionView(self.bot, interaction.user.id, self.day, start, end)
        await interaction.response.send_message(
            f"✅ Time set for **{self.day.title()}** ({start} - {end}). Please select your status preference below:", 
            view=view, 
            ephemeral=True
        )

class DayDropdown(discord.ui.Select):
    def __init__(self, bot):
        options = [
            discord.SelectOption(label="Monday", value="monday"),
            discord.SelectOption(label="Tuesday", value="tuesday"),
            discord.SelectOption(label="Wednesday", value="wednesday"),
            discord.SelectOption(label="Thursday", value="thursday"),
            discord.SelectOption(label="Friday", value="friday"),
            discord.SelectOption(label="Saturday", value="saturday"),
            discord.SelectOption(label="Sunday", value="sunday"),
        ]
        super().__init__(placeholder="Choose a day to set schedule...", options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        day = self.values[0]
        await interaction.response.send_modal(AvailabilityModal(day, self.bot))


class StatusSelectionView(discord.ui.View):
    def __init__(self, bot, user_id, day, start, end):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.day = day
        self.start = start
        self.end = end
        self.is_pref = False

    @discord.ui.button(label="YES (+10)", style=discord.ButtonStyle.green)
    async def yes_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.availability.add_availability(self.user_id, self.day, self.start, self.end, "YES", self.is_pref)
        await interaction.response.edit_message(content=f"💾 Saved: **YES** for {self.day.title()} ({self.start}-{self.end})", view=None)

    @discord.ui.button(label="MAYBE (+3)", style=discord.ButtonStyle.blurple)
    async def maybe_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.availability.add_availability(self.user_id, self.day, self.start, self.end, "MAYBE", self.is_pref)
        await interaction.response.edit_message(content=f"💾 Saved: **MAYBE** for {self.day.title()} ({self.start}-{self.end})", view=None)

    @discord.ui.button(label="NO (-100)", style=discord.ButtonStyle.red)
    async def no_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.availability.add_availability(self.user_id, self.day, self.start, self.end, "NO", False)
        await interaction.response.edit_message(content=f"💾 Saved: **NO** for {self.day.title()} ({self.start}-{self.end})", view=None)

    @discord.ui.button(label="Mark Preferred (+5)", style=discord.ButtonStyle.grey, emoji="⭐")
    async def pref_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.is_pref = not self.is_pref
        button.style = discord.ButtonStyle.success if self.is_pref else discord.ButtonStyle.grey
        await interaction.response.edit_message(view=self)


class AvailabilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setschedule")
    async def setschedule(self, ctx):
        """Triggers the interactive scheduling UI dropdown."""
        view = discord.ui.View()
        view.add_item(DayDropdown(self.bot))
        await ctx.send("📅 Select a day from the menu below to set your availability:", view=view)

    @commands.command(name="besttime")
    async def besttime(self, ctx, day: str):
        """Checks the highest score for a timeframe on a given day."""
        best = await self.bot.availability.get_best_time(day)
        if best:
            start, end, score = best
            await ctx.send(f"🏆 The best time for **{day.title()}** is **{start} - {end}** (Score: {score})")
        else:
            await ctx.send(f"🤷 No schedules found for **{day.title()}** yet.")

async def setup(bot):
    await bot.add_cog(AvailabilityCog(bot))
