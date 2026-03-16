import aiosqlite, os

class DatabaseService:
    def __init__(self, path="data/fessenden.db"):
        self.path = path
        os.makedirs('data', exist_ok=True)

    async def initialize(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, records TEXT DEFAULT '')")
            await db.execute("CREATE TABLE IF NOT EXISTS events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, time TEXT, desc TEXT)")
            await db.commit()

    async def run_query(self, query, params=()):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(query, params) as c:
                res = await c.fetchone()
                await db.commit()
                return res

    async def fetch_all(self, query, params=()):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(query, params) as c:
                return await c.fetchall()