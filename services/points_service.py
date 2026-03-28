class PointsService:
    def __init__(self, db):
        self.db = db

    # --- 🔵 GAME POINTS (Automated for Tic-Tac-Toe) ---
    async def get_game_balance(self, user_id: int):
        user = await self.db.get_user(user_id)
        return user.get('discord_points', 0)

    async def update_game_points(self, user_id: int, amount: int):
        """Used for automated game payouts."""
        return await self.db.execute(
            "UPDATE users SET discord_points = discord_points + $1 WHERE id = $2",
            amount, user_id
        )

    # --- 🔴 GOVERNMENT MERITS (Manual Only) ---
    async def award_merit(self, admin_id: int, target_id: int, amount: int, reason: str):
        """This remains manual. No game code should ever call this."""
        await self.db.execute(
            "INSERT INTO merit_history (admin_id, user_id, amount, reason) VALUES ($1, $2, $3, $4)",
            admin_id, target_id, amount, reason
        )
        return await self.db.execute(
            "UPDATE users SET merit_balance = merit_balance + $1 WHERE id = $2",
            amount, target_id
        )
