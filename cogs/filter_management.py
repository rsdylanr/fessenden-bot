from discord.ext import commands

class FilterManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="filter")
    async def manage_filter(self, ctx, action: str, path_str: str, *, value: str = None):
        """
        Usage: 
        !filter add_word Links/Malicious "badsite.com"
        !filter set_action Offensive/Slurs "Instant_Ban"
        """
        if ctx.author.id not in self.bot.filter.masters:
            return await ctx.send("❌ Access Denied.")

        path = path_str.split("/")
        node = self.bot.filter._get_node(path)
        
        if not node:
            return await ctx.send(f"❌ Path `{path_str}` not found in JSON tree.")

        if action == "add_word":
            node.setdefault("Words", []).append(value)
            msg = f"✅ Added word `{value}` to `{path_str}`"
        
        elif action == "add_regex":
            node.setdefault("Regex", []).append(value)
            msg = f"✅ Added regex `{value}` to `{path_str}`"
            
        elif action == "set_action":
            node.setdefault("Settings", {})["Action"] = value
            msg = f"✅ Set action for `{path_str}` to `{value}`"
        
        else:
            return await ctx.send("❌ Unknown action. Use `add_word`, `add_regex`, or `set_action`.")

        # Save back to Supabase
        await self.bot.filter.save_to_cloud()
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(FilterMgmt(bot))
