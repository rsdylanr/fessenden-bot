import discord
from discord.ext import commands
from typing import Optional

class TTTButton(discord.ui.Button['TicTacToeView']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x, self.y = x, y

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if interaction.user != view.current_player:
            return await interaction.response.send_message("Not your turn!", ephemeral=True)

        if view.board[self.y][self.x] != 0:
            return await interaction.response.send_message("Spot taken!", ephemeral=True)

        # Logic
        char = 'X' if view.current_player == view.player_x else 'O'
        self.label, self.disabled = char, True
        self.style = discord.ButtonStyle.danger if char == 'X' else discord.ButtonStyle.success
        view.board[self.y][self.x] = 1 if char == 'X' else 2

        winner = view.check_winner()
        content = f"🎮 {view.player_x.mention} vs {view.player_o.mention}"
        
        if winner:
            if winner == 3:
                content = "🤝 **Tie!** No points exchanged."
            else:
                win_user = view.player_x if winner == 1 else view.player_o
                lose_user = view.player_o if winner == 1 else view.player_x
                content = f"🏆 {win_user.mention} wins!"
                
                if view.wager > 0:
                    await view.points_service.update_game_score(win_user.id, view.wager)
                    await view.points_service.update_game_score(lose_user.id, -view.wager)
                    content += f" (+{view.wager} Game Points)"
            
            for child in view.children: child.disabled = True
            view.stop()
        else:
            view.current_player = view.player_o if view.current_player == view.player_x else view.player_x
            content += f"\n\n**Next Turn:** {view.current_player.mention}"

        await interaction.response.edit_message(content=content, view=view)

class TicTacToeView(discord.ui.View):
    def __init__(self, player_x, player_o, wager, points_service):
        super().__init__(timeout=300)
        self.player_x, self.player_o, self.wager, self.points_service = player_x, player_o, wager, points_service
        self.current_player = player_x
        self.board = [[0]*3 for _ in range(3)]
        for y in range(3):
            for x in range(3): self.add_item(TTTButton(x, y))

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != 0: return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != 0: return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != 0: return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != 0: return self.board[0][2]
        if all(all(row) for row in self.board): return 3
        return None

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wager_enabled = True

    @commands.hybrid_command(name="tictactoe")
    async def tictactoe(self, ctx, opponent: discord.Member, wager: Optional[int] = 0):
        if opponent.bot or opponent == ctx.author: return await ctx.send("Invalid opponent.")
        if wager > 0 and not self.wager_enabled: return await ctx.send("❌ Wagering disabled.")

        view = TicTacToeView(ctx.author, opponent, wager, self.bot.points)
        msg = f"🎮 {ctx.author.mention} challenged {opponent.mention}!"
        if wager > 0: msg += f"\n🏆 **Stakes:** {wager} Game Points"
        await ctx.send(msg, view=view)

    @commands.hybrid_command(name="game_top")
    async def game_top(self, ctx):
        rows = await self.bot.db.get_game_leaderboard()
        if not rows: return await ctx.send("Leaderboard is empty.")
        
        data = ""
        for i, r in enumerate(rows, 1):
            u = self.bot.get_user(r['user_id'])
            name = u.display_name if u else f"ID: {r['user_id']}"
            data += f"**{i}.** {name} — `{r['discord_points']}`\n"
            
        await ctx.send(embed=discord.Embed(title="🏆 Top Gamers", description=data, color=0x00ff00))

async def setup(bot):
    await bot.add_cog(Games(bot))
