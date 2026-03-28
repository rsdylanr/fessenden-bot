class PointsService:
    def __init__(self, db):
        self.db = db

    async def update_game_score(self, user_id: int, amount: int):
        """Free-to-play: just updates the score in the DB."""
        return await self.db.update_game_points(user_id, amount)

    async def get_all_balances(self, user_id: int):
        """Useful for a balance command later."""
        merits = await self.db.get_merits(user_id)
        points = await self.db.get_game_points(user_id)
        return {"merits": merits, "points": points}
