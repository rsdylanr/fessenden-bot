import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

class CloudDatabaseService:
    def __init__(self):
        self.pool = None
        self.uri = os.getenv("SUPABASE_URI")

    async def initialize(self):
        """Connects to Supabase and ensures all columns exist."""
        if not self.uri:
            print("❌ Cloud DB Error: SUPABASE_URI is missing!")
            return

        try:
            self.pool = await asyncpg.create_pool(self.uri)
            print("🌐 ✅ Connected to Supabase via asyncpg!")

            async with self.pool.acquire() as conn:
                # Initialize Users table with BOTH Merits and Game Points
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        merit_balance INT DEFAULT 0,
                        discord_points INT DEFAULT 0
                    )
                """)
                
                # Check if discord_points column exists (for existing tables)
                await conn.execute("""
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name='users' AND column_name='discord_points') THEN
                            ALTER TABLE users ADD COLUMN discord_points INT DEFAULT 0;
                        END IF;
                    END $$;
                """)
                
                print("📁 ✅ Database Schema Synchronized.")
        except Exception as e:
            print(f"❌ Cloud DB Initialization Error: {e}")

    async def run_query(self, query: str, *args):
        """Standard EXECUTE for INSERT/UPDATE/DELETE."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch_all(self, query: str, *args):
        """Standard SELECT for returning multiple rows."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetch_row(self, query: str, *args):
        """Standard SELECT for a single row."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    # --- 🔵 GAME POINTS LOGIC (Automated) ---

    async def update_game_points(self, user_id: int, amount: int):
        """Adds/Subtracts from the fun game points only."""
        await self.run_query("""
            INSERT INTO users (user_id, discord_points) VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE 
            SET discord_points = users.discord_points + EXCLUDED.discord_points
        """, user_id, amount)

    async def get_game_points(self, user_id: int) -> int:
        row = await self.fetch_row("SELECT discord_points FROM users WHERE user_id = $1", user_id)
        return row['discord_points'] if row else 0

    # --- 🔴 MERIT LOGIC (Manual/Government) ---

    async def get_merits(self, user_id: int) -> int:
        row = await self.fetch_row("SELECT merit_balance FROM users WHERE user_id = $1", user_id)
        return row['merit_balance'] if row else 0

    async def get_game_leaderboard(self, limit: int = 10):
        """Top players by Game Points, not Merits."""
        return await self.fetch_all("SELECT user_id, discord_points FROM users ORDER BY discord_points DESC LIMIT $1", limit)
