import discord
from discord.ext import commands
from services.time_service import TimeService

class AvailabilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setschedule")
    async def setschedule(self, ctx):
        """Triggers the interactive scheduling UI dropdown using the UIService."""
        
        # 1. Define the Options for the Dropdown
        options = [
            discord.SelectOption(label="Monday", value="monday"),
            discord.SelectOption(label="Tuesday", value="tuesday"),
            discord.SelectOption(label="Wednesday", value="wednesday"),
            discord.SelectOption(label="Thursday", value="thursday"),
            discord.SelectOption(label="Friday", value="friday"),
            discord.SelectOption(label="Saturday", value="saturday"),
            discord.SelectOption(label="Sunday", value="sunday"),
        ]

        # 2. Define what happens when they pick a day (Open the Modal)
        async def dropdown_callback(interaction: discord.Interaction, values: list):
            day = values[0]
            await self._open_time_modal(interaction, day)

        # 3. Ask the UI Factory to build the dropdown view
        view = self.bot.ui.create_dropdown_view(
            placeholder="Choose a day to set schedule...",
            options=options,
            callback=dropdown_callback
        )

        await ctx.send("📅 Select a day from the menu below to set your availability:", view=view)


    async def _open_time_modal(self, interaction: discord.Interaction, day: str):
        """Builds and opens the time input modal using the UIService."""
        
        inputs = [
            {"label": "Start Time (e.g. 3:00 PM)", "placeholder": "3:30 PM", "required": True},
            {"label": "End Time (e.g. 5:00 PM)", "placeholder": "5:00 PM", "required": True}
        ]

        # What happens when they submit the modal
        async def modal_callback(modal_interaction: discord.Interaction, values: dict):
            start_raw = values.get("Start Time (e.g. 3:00 PM)")
            end_raw = values.get("End Time (e.g. 5:00 PM)")

            start = TimeService.parse_time(start_raw)
            end = TimeService.parse_time(end_raw)

            if not start or not end:
                await modal_interaction.response.send_message("❌ Invalid time format! Please include AM or PM (e.g., 3:00 PM).", ephemeral=True)
                return

            await self._send_status_buttons(modal_interaction, day, start, end)

        # Open it
        modal = self.bot.ui.create_modal(title=f"Set Time for {day.title()}", inputs=inputs, callback=modal_callback)
        await interaction.response.send_modal(modal)


    async def _send_status_buttons(self, interaction: discord.Interaction, day: str, start: str, end: str):
        """Sends the final status buttons using the UIService."""

        # Shared saver logic to reduce duplicated code
        async def save_status(btn_interaction: discord.Interaction, status: str):
            await self.bot.availability.add_availability(btn_interaction.user.id, day, start, end, status)
            await btn_interaction.response.edit_message(content=f"💾 Saved: **{status}** for {day.title()} ({start}-{end})", view=None)

        buttons = [
            {"label": "YES (+10)", "style": discord.ButtonStyle.green, "callback": lambda i: save_status(i, "YES")},
            {"label": "MAYBE (+3)", "style": discord.ButtonStyle.blurple, "callback": lambda i: save_status(i, "MAYBE")},
            {"label": "NO (-100)", "style": discord.ButtonStyle.red, "callback": lambda i: save_status(i, "NO")}
        ]

        view = self.bot.ui.create_button_view(buttons)
        await interaction.response.send_message(
            f"✅ Time set for **{day.title()}** ({start} - {end}). Select your status below:", 
            view=view, 
            ephemeral=True
        )


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
