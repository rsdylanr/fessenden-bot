import datetime

class CalendarService:
    def __init__(self, db_service):
        self.db = db_service

    async def add_event(self, name: str, event_time: str, description: str):
        """Adds a new event to the database."""
        await self.db.run_query('''
            INSERT INTO events (event_name, event_time, description)
            VALUES (?, ?, ?)
        ''', (name, event_time, description))

    async def get_all_events(self):
        """Retrieves all events sorted by date."""
        return await self.db.fetch_all('''
            SELECT event_name, event_time, description 
            FROM events 
            ORDER BY event_time ASC
        ''')

    async def clear_past_events(self):
        """Optional: Removes events that have already happened to keep the DB clean."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        await self.db.run_query("DELETE FROM events WHERE event_time < ?", (now,))

    async def check_reminders(self):
        """
        Logic for the background task:
        Finds events happening in exactly 1 hour.
        """
        now = datetime.datetime.now()
        one_hour_later = (now + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        
        return await self.db.fetch_all(
            "SELECT event_name, description FROM events WHERE event_time = ?", 
            (one_hour_later,)
        )