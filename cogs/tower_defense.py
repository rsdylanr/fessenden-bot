import discord
from discord.ext import commands
import asyncio
import random
import time

class TowerDefenseView(discord.ui.View):
    """
    Phase 3: Co-op Server vs. Boss
    Features: Shared HP, individual cooldowns, and visual progress bars.
    """
    def __init__(self, message_service, boss_name, hp):
        super().__init__(timeout=300)
        self.ms = message_service
        self.boss_name = boss_name
        self.max_hp = hp
        self.current_hp = hp
        self.shield_hp = 50
        self.max_shield = 100
        self.cooldowns = {} # User ID : Last Action Time
        self.logs = ["⚔️ The battle has begun!"]

    async def check_cooldown(self, user_id, seconds=3):
        now = time.time()
        if user_id in self.cooldowns:
            if now - self.cooldowns[user_id] < seconds:
                return False
        self.cooldowns[user_id] = now
        return True

    def create_embed(self):
        # Phase 5: Using the Progress Bar Utility from MessageService
        # (Assuming the method: progress_bar(current, total))
        hp_bar = asyncio.run_coroutine_threadsafe(self.ms.progress_bar(self.current_hp, self.max_hp), self.ms.bot.loop).result()
        shield_bar = asyncio.run_coroutine_threadsafe(self.ms.progress_bar(self.shield_hp, self.max_shield), self.ms.bot.loop).result()
        
        embed = discord.Embed(
            title=f"🛡️ DEFEND FESSENDEN: {self.boss_name}",
            color=0x3498db if self.current_hp > 0 else 0x2ecc71
        )
        
        embed.add_field(name="Boss Health", value=f"{hp_bar}\n({self.current_hp}/{self.max_hp} HP)", inline=False)
        embed.add_field(name="City Shield", value=f"{shield_bar}\n({self.shield_hp}/{self.max_shield} SP)", inline=False)
        
        recent_logs = "\n".join(self.logs[-5:])
        embed.add_field(name="Battle Feed", value=f"```md\n{recent_logs}\n```", inline=False)
        
        embed.set_footer(text=f"Ref: {self.ms.generate_ref()} | Co-op Mission")
        return embed

    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_cooldown(interaction.user.id, 2):
            return await interaction.response.send_message("Your weapons are cooling down!", ephemeral=True)

        dmg = random.randint(5, 15)
        self.current_hp = max(0, self.current_hp - dmg)
        self.logs.append(f"* {interaction.user.display_name} dealt {dmg} damage!")

        if self.current_hp <= 0:
            for child in self.children: child.disabled = True
            self.logs.append(f"🏆 {self.boss_name} HAS BEEN DEFEATED!")
            self.stop()
            
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="🛠️ Repair Shield", style=discord.ButtonStyle.primary)
    async def repair(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_cooldown(interaction.user.id, 5):
            return await interaction.response.send_message("Engineering is busy!", ephemeral=True)

        rep = random.randint(10, 20)
        self.shield_hp = min(self.max_shield, self.shield_hp + rep)
        self.logs.append(f"* {interaction.user.display_name} repaired {rep} shield points.")
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

class TowerDefense(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="boss")
    async def spawn_boss(self, ctx, name: str = "The Ender-Glitched Wither"):
        """Spawns a co-op boss battle for the whole server."""
        view = TowerDefenseView(self.bot.message_service, name, 500)
        msg = await ctx.send(embed=view.create_embed(), view=view)
        
        # Background: Boss attacks the shield every 10 seconds
        while view.current_hp > 0:
            await asyncio.sleep(10)
            if view.current_hp <= 0: break
            
            boss_dmg = random.randint(5, 15)
            view.shield_hp -= boss_dmg
            view.logs.append(f"< {view.boss_name} hit the shield for {boss_dmg}! >")
            
            if view.shield_hp <= 0:
                view.shield_hp = 0
                view.logs.append("‼️ SHIELD DOWN! DAMAGE MULTIPLIED!")
            
            try:
                await msg.edit(embed=view.create_embed())
            except:
                break

async def setup(bot):
    await bot.add_cog(TowerDefense(bot))
