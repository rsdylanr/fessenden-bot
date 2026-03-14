class PointsService:
    def __init__(self, db_service):
        self.db = db_service

    async def add_points(self, user_id, points):
        await self.db.run_query('''
            INSERT INTO users (user_id, points) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET points = points + excluded.points
        ''', (user_id, points))
        return await self.get_points(user_id)

    async def get_points(self, user_id):
        result = await self.db.run_query('SELECT points FROM users WHERE user_id = ?', (user_id,))
        return result[0] if result else 0

    async def add_misbehavior(self, user_id, record):
        await self.db.run_query('''
            INSERT INTO users (user_id, misbehavior_record) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            misbehavior_record = CASE 
                WHEN misbehavior_record = "" THEN excluded.misbehavior_record 
                ELSE misbehavior_record || "\n" || excluded.misbehavior_record 
            END
        ''', (user_id, record))

    async def get_misbehavior_record(self, user_id):
        result = await self.db.run_query('SELECT misbehavior_record FROM users WHERE user_id = ?', (user_id,))
        return result[0] if result else "No record."