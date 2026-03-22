import discord
from discord.ext import commands

class PermissionsService:
    def __init__(self, pool):
        self.pool = pool

    async def initialize_tables(self):
        """Creates the Supabase table for word-based permission flags."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_flags (
                    user_id BIGINT PRIMARY KEY,
                    flags TEXT[] DEFAULT '{}' -- Saves words as a Postgres Array!
                )
            """)

    async def get_flags(self, user_id: int) -> list:
        """Fetches the text-flags array for a user from Supabase."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT flags FROM user_flags WHERE user_id = $1", user_id)
            return row['flags'] if row else []

    async def add_flag(self, user_id: int, flag: str):
        """Adds a text-flag to a user (if it doesn't already exist)."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_flags (user_id, flags) 
                VALUES ($1, ARRAY[$2])
                ON CONFLICT (user_id) 
                DO UPDATE SET flags = array_append(
                    array_remove(user_flags.flags, $2), $2
                )
            """, user_id, flag.lower())

    async def remove_flag(self, user_id: int, flag: str):
        """Removes a text-flag from a user's array."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE user_flags SET flags = array_remove(flags, $1) WHERE user_id = $2
            """, flag.lower(), user_id)

    async def check_permission(self, user_id: int, required_flag: str) -> bool:
        """The ultimate boolean check. Returns True if user has the word flag."""
        # 👑 YOUR DISCORD ID HERE (Bypasses all checks!)
        if user_id == 123456789012345678: 
            return True

        flags = await self.get_flags(user_id)
        return required_flag.lower() in flags


class PermissionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.perm_service = None

    @commands.Cog.listener()
    async def on_ready(self):
        # Grabs the pool we just built in cloud_db_service.py!
        if hasattr(self.bot.db, 'pool'):
            self.perm_service = PermissionsService(self.bot.db.pool)
            await self.perm_service.initialize_tables()
            
            # Bind globally so ALL other cogs can use it!
            self.bot.permissions = self.perm_service
            print("✅ Supabase Custom Permissions (Words) Online!")
        else:
            print("❌ Permissions Error: Could not find the Cloud Database pool.")

    @commands.command(name="grantflag")
    @commands.has_permissions(administrator=True)
    async def grantflag(self, ctx, member: discord.Member, flag: str):
        """Grants a text permission flag to a user in Supabase."""
        await self.bot.permissions.add_flag(member.id, flag)
        await ctx.send(f"✅ Flag `{flag.lower()}` added to {member.mention} in the cloud!")

    @commands.command(name="revokeflag")
    @commands.has_permissions(administrator=True)
    async def revokeflag(self, ctx, member: discord.Member, flag: str):
        """Revokes a text permission flag from a user in Supabase."""
        await self.bot.permissions.remove_flag(member.id, flag)
        await ctx.send(f"❌ Flag `{flag.lower()}` removed from {member.mention} in the cloud.")

    @commands.command(name="myflags")
    async def myflags(self, ctx):
        """Lists your active permission flags."""
        flags = await self.bot.permissions.get_flags(ctx.author.id)
        if not flags:
            await ctx.send("🤷 You have no active permission flags.")
        else:
            await ctx.send(f"📋 Your active flags: `{'`, `'.join(flags)}`")


async def setup(bot):
    await bot.add_cog(PermissionsCog(bot))
