class PointsService:
    def __init__(self, db_service):
        self.db = db_service

    async def add_points(self, user_id: int, amount: int):
        """Adds points to a user and returns their new total."""
        await self.db.run_query('''
            INSERT INTO users (user_id, points) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET points = points + excluded.points
        ''', (user_id, amount))
        
        res = await self.db.run_query('SELECT points FROM users WHERE user_id = ?', (user_id,))
        return res[0] if res else amount

    async def get_stats(self, user_id: int):
        """Returns a tuple of (points, records)."""
        res = await self.db.run_query('SELECT points, records FROM users WHERE user_id = ?', (user_id,))
        # Return 0 points and empty string if user isn't in DB yet
        return res if res else (0, "")

    async def add_infraction(self, user_id: int, note: str):
        """Appends a staff note to the user's permanent record."""
        await self.db.run_query('''
            INSERT INTO users (user_id, records) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET records = records || "\n" || excluded.records
        ''', (user_id, note))