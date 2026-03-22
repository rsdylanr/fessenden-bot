class AvailabilityService:
    def __init__(self, db_service):
        self.db = db_service

    async def add_availability(self, user_id: int, day: str, start: str, end: str, status: str = 'YES', is_pref: bool = False):
        """Saves availability and calculates the weight scoring system."""
        
        weight = 0
        status = status.upper()
        
        if status == 'YES':
            weight += 10
        elif status == 'MAYBE':
            weight += 3
        elif status == 'NO':
            weight += -100

        if is_pref and status != 'NO':
            weight += 5

        pref_val = 1 if is_pref else 0

        # Note: Your DB service uses run_query
        await self.db.run_query('''
            INSERT INTO availability (user_id, day_of_week, start_time, end_time, weight, is_pref, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, day.lower(), start, end, weight, pref_val, status))

    async def clear_user_availability(self, user_id: int, day: str = None):
        if day:
            await self.db.run_query('DELETE FROM availability WHERE user_id = ? AND day_of_week = ?', (user_id, day.lower()))
        else:
            await self.db.run_query('DELETE FROM availability WHERE user_id = ?', (user_id,))

    async def get_best_time(self, day: str):
        """Sums the weights to find the absolute best timeframe for a day."""
        query = '''
            SELECT start_time, end_time, SUM(weight) as total_score 
            FROM availability 
            WHERE day_of_week = ?
            GROUP BY start_time, end_time 
            ORDER BY total_score DESC 
            LIMIT 1
        '''
        res = await self.db.run_query(query, (day.lower(),))
        return res if res else None
