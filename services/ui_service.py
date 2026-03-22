import discord
from typing import Callable, List, Dict, Any, Optional

class UIService:
    """A Factory service that builds Discord UI components dynamically."""
    
    def __init__(self, bot):
        self.bot = bot

    def create_button_view(self, buttons: List[Dict[str, Any]], timeout: int = 60) -> discord.ui.View:
        """
        Generates a view with custom buttons.
        Example item in buttons list:
        {
            "label": "Click Me", 
            "style": discord.ButtonStyle.green, 
            "callback": some_function,
            "emoji": "✅"
        }
        """
        view = discord.ui.View(timeout=timeout)

        for btn_data in buttons:
            button = discord.ui.Button(
                label=btn_data.get("label", "Button"),
                style=btn_data.get("style", discord.ButtonStyle.grey),
                emoji=btn_data.get("emoji"),
                custom_id=btn_data.get("custom_id")
            )

            # Assign the callback function to the button
            if "callback" in btn_data:
                async def make_callback(cb, b):
                    async def _inner(interaction: discord.Interaction):
                        await cb(interaction)
                    return _inner
                
                button.callback = await make_callback(btn_data["callback"], button)

            view.add_item(button)

        return view

    def create_dropdown_view(self, placeholder: str, options: List[discord.SelectOption], callback: Callable, timeout: int = 60) -> discord.ui.View:
        """Generates a view with a single dropdown menu."""
        view = discord.ui.View(timeout=timeout)

        select = discord.ui.Select(placeholder=placeholder, options=options)

        async def _dropdown_callback(interaction: discord.Interaction):
            await callback(interaction, select.values)

        select.callback = _dropdown_callback
        view.add_item(select)

        return view

    def create_modal(self, title: str, inputs: List[Dict[str, Any]], callback: Callable) -> discord.ui.Modal:
        """
        Generates a pop-up text form/modal dynamically.
        Example item in inputs list:
        {
            "label": "Name",
            "placeholder": "Enter name...",
            "style": discord.TextStyle.short,
            "required": True
        }
        """
        class DynamicModal(discord.ui.Modal, title=title):
            def __init__(self):
                super().__init__()
                self.text_inputs = {}

                for inp in inputs:
                    text_input = discord.ui.TextInput(
                        label=inp.get("label", "Field"),
                        style=inp.get("style", discord.TextStyle.short),
                        placeholder=inp.get("placeholder"),
                        required=inp.get("required", True),
                        max_length=inp.get("max_length"),
                        min_length=inp.get("min_length")
                    )
                    self.add_item(text_input)
                    self.text_inputs[inp.get("label")] = text_input

            async def on_submit(self, interaction: discord.Interaction):
                # Sends a dictionary of {Label: Value} to your callback function
                values = {label: widget.value for label, widget in self.text_inputs.items()}
                await callback(interaction, values)

        return DynamicModal()
