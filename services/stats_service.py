from collections import Counter

class StatsService:
    def __init__(self, bot):
        self.bot = bot
        # Temporary storage for the 24-hour cycle
        self.daily_messages = Counter() # {user_id: count}
        self.daily_wins = Counter()     # {user_id: count}
        self.total_messages = 0

    def record_message(self, user_id: int):
        self.daily_messages[user_id] += 1
        self.total_messages += 1

    def record_win(self, user_id: int):
        self.daily_wins[user_id] += 1

    def get_top_user(self):
        if not self.daily_messages: return None
        return self.daily_messages.most_common(1)[0] # (user_id, count)

    def get_top_gamer(self):
        if not self.daily_wins: return None
        return self.daily_wins.most_common(1)[0] # (user_id, count)

    def reset_daily(self):
        self.daily_messages.clear()
        self.daily_wins.clear()
        self.total_messages = 0
