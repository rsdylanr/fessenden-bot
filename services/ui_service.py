import discord
from typing import Callable, List, Dict, Any, Optional

class UIService:
    """A Factory service that builds Discord UI components dynamically."""
    
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------------------------
    # 🔘 BUTTON VIEW FACTORY
    # -----------------------------------------------
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

            if "callback" in btn_data:
                # FIXED: Simple closure factory to prevent button callbacks from overriding each other in loops
                def make_callback(cb):
                    async def _inner(interaction: discord.Interaction):
                        await cb(interaction)
                    return _inner
                
                button.callback = make_callback(btn_data["callback"])

            view.add_item(button)

        return view

    # -----------------------------------------------
    # 🔽 DROPDOWN VIEW FACTORY
    # -----------------------------------------------
    def create_dropdown_view(self, placeholder: str, options: List[discord.SelectOption], callback: Callable, timeout: int = 60) -> discord.ui.View:
        """Generates a view with a single dropdown menu."""
        view = discord.ui.View(timeout=timeout)

        select = discord.ui.Select(placeholder=placeholder, options=options)

        async def _dropdown_callback(interaction: discord.Interaction):
            await callback(interaction, select.values)

        select.callback = _dropdown_callback
        view.add_item(select)

        return view

    # -----------------------------------------------
    # 📋 MODAL VIEW FACTORY
    # -----------------------------------------------
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

    # -----------------------------------------------
    # 📄 PAGINATION VIEW FACTORY
    # -----------------------------------------------
    def create_pagination_view(self, items: List[Any], items_per_page: int, callback: Callable, timeout: int = 60) -> discord.ui.View:
        """Generates a view with pagination buttons for navigating through a list of items."""
        
        # FIXED: We need a custom class here so the UI keeps track of its own page state!
        class PaginatedView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=timeout)
                self.current_page = 0
                self.total_pages = (len(items) + items_per_page - 1) // items_per_page
                self.update_buttons()

            def update_buttons(self):
                self.clear_items()
                
                if self.current_page > 0:
                    prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary)
                    prev_button.callback = self.prev_page
                    self.add_item(prev_button)

                if self.current_page < self.total_pages - 1:
                    next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary)
                    next_button.callback = self.next_page
                    self.add_item(next_button)

            async def send_initial_page(self, interaction: discord.Interaction):
                """Helper to pull the first page data."""
                start = self.current_page * items_per_page
                end = start + items_per_page
                page_items = items[start:end]
                await callback(interaction, page_items, self.current_page + 1, self.total_pages, self)

            async def next_page(self, interaction: discord.Interaction):
                if self.current_page < self.total_pages - 1:
                    self.current_page += 1
                    self.update_buttons()
                    start = self.current_page * items_per_page
                    end = start + items_per_page
                    page_items = items[start:end]
                    await callback(interaction, page_items, self.current_page + 1, self.total_pages, self)

            async def prev_page(self, interaction: discord.Interaction):
                if self.current_page > 0:
                    self.current_page -= 1
                    self.update_buttons()
                    start = self.current_page * items_per_page
                    end = start + items_per_page
                    page_items = items[start:end]
                    await callback(interaction, page_items, self.current_page + 1, self.total_pages, self)

        return PaginatedView()

    # -----------------------------------------------
    # ✅ CONFIRMATION VIEW FACTORY (YOUR NEW SYSTEM)
    # -----------------------------------------------
    def create_confirmation_view(self, confirm_callback: Callable, cancel_callback: Optional[Callable] = None, timeout: int = 60) -> discord.ui.View:
        """Generates a view with Confirm and Cancel buttons for user confirmation."""
        
        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=timeout)
                
                confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success)
                confirm_button.callback = self.confirm
                self.add_item(confirm_button)

                # Fixed to fall back cleanly if no cancel_callback is provided
                cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
                cancel_button.callback = self.cancel
                self.add_item(cancel_button)
                    
            async def confirm(self, interaction: discord.Interaction):
                await confirm_callback(interaction)
                self.stop() # stop the view after confirmation
                
            async def cancel(self, interaction: discord.Interaction):
                if cancel_callback:
                    await cancel_callback(interaction)
                else:
                    await interaction.response.send_message("❌ Action cancelled.", ephemeral=True)
                self.stop() # stop the view after cancellation

        return ConfirmationView()
