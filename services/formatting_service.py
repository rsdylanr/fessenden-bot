import discord
from datetime import datetime

class FormattingService:
    def __init__(self, bot):
        self.bot = bot
        # High-contrast UI colors
        self.colors = {
            "tech": 0x2b2d31,     # Dark Grey (Discord Theme)
            "success": 0x2ecc71,  # Green
            "error": 0xe74c3c,    # Red
            "warning": f"0xf1c40f", # Yellow
            "info": 0x3498db      # Blue
        }

    def system_embed(self, title: str, description: str, status: str = "info"):
        """Standardized UI for System Logs and Command Outputs."""
        color = self.colors.get(status, self.colors["info"])
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(
            text="Fessenden System Output", 
            icon_url=self.bot.user.display_avatar.url
        )
        return embed

    def data_table(self, headers: list, rows: list):
        """Formats lists of data into a readable ASCII table for code blocks."""
        if not rows:
            return "```text\nNo data available.\n```"

        # Calculate padding
        widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
        
        # Build Table
        head = " | ".join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
        sep = "-+-".join("-" * w for w in widths)
        body = "\n".join(" | ".join(f"{str(row[i]):<{widths[i]}}" for i in range(len(headers))) for row in rows)
        
        return f"```text\n{head}\n{sep}\n{body}\n```"

    def sensor_log(self, label: str, value: str, trend: str = ""):
        """Specific formatting for the Bio-Experiment / Saliva logger."""
        return f"**{label}:** `{value}` {trend}"
