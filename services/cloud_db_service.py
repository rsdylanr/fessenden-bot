import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

class CloudDatabaseService:
    def __init__(self):
        self.pool = None
        self.uri = os.getenv("SUPABASE_URI")

    async def initialize(self):
        """Connects to Supabase and creates all your standard tables if they don't exist."""
        if not self.uri:
            print("❌ Cloud DB Error: SUPABASE_URI is missing from your .env file!")
            return

        try:
            self.pool = await asyncpg.create_pool(self.uri)
            print("🌐 ✅ Successfully connected to Supabase Cloud Database!")

            # We initialize all of your standard Fessenden tables in the cloud!
            async with self.pool.acquire() as conn:
                # 1. Users & Points
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        points INT DEFAULT 0,
                        merit_balance INT DEFAULT 0
                    )
                """)

                # 2. Availability & Schedules
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS availability (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        day_of_week TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        weight INT DEFAULT 1,
                        is_pref BOOLEAN DEFAULT FALSE,
                        status TEXT DEFAULT 'pending'
                    )
                """)

                # 3. Settings (For Logging channels, etc.)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                
                print("📁 ✅ All Cloud Tables Synchronized.")

        except Exception as e:
            print(f"❌ Cloud DB Initialization Error: {e}")


    async def run_query(self, query: str, *args):
        """Executes INSERT, UPDATE, DELETE queries (Equivalent to old SQLite execute)."""
        # Postgres uses $1, $2, $3 instead of ? for variables
        query = query.replace("?", "$1") # Quick helper for backward compatibility!
        
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


    async def fetch_all(self, query: str, *args):
        """Executes SELECT queries and returns rows (Equivalent to old fetchall)."""
        query = query.replace("?", "$1")
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            # Converts asyncpg record types into standard tuples so your old code doesn't break
            return [tuple(row.values()) for row in rows]
