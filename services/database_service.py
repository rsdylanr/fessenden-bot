import aiosqlite
import os

class DatabaseService:
    def __init__(self, db_path="data/roast_bot.db"):
        self.db_path = db_path
        os.makedirs('data', exist_ok=True)

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    misbehavior_record TEXT DEFAULT ""
                )
            ''')
            await db.commit()

    async def run_query(self, query, params=()):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchone()
                await db.commit()
                return result

    async def fetch_all(self, query, params=()):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                return await cursor.fetchall()