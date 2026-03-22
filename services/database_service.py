import aiosqlite

class DatabaseService:
    def __init__(self, db_path="fessenden.db"):
        self.db_path = db_path

    async def initialize(self):
        """Creates tables if they do not exist when the bot starts."""
        async with aiosqlite.connect(self.db_path) as conn:
            # Users Table (Points and Records)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    records TEXT DEFAULT ''
                )
            """)
            
            # Availability Table (Scheduling and Weights)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS availability (
                    user_id INTEGER,
                    day_of_week TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    weight INTEGER DEFAULT 0,
                    is_pref INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'YES'
                )
            """)
            await conn.commit()

    async def run_query(self, query, params=()):
        """Standard query runner used by all services."""
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute(query, params) as cursor:
                result = await cursor.fetchall()
                await conn.commit()
                # Return the rows if it's a SELECT, otherwise None
                return result if result else None
