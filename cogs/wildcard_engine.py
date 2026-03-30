import random

class WildcardService:
    def __init__(self, bot):
        self.bot = bot
        
        self.holidays = [
            "International 'Ping the Admin' Day (Don't actually do it).",
            "National Redstone Engineering Appreciation Day.",
            "The Festival of the Golden Apple.",
            "Official 'Code Refactoring' Friday.",
            "Universal Yorkshire Terrier Appreciation Hour (Pet Marty!)."
        ]
        
        self.thoughts = [
            "If you drop soap on the floor, is the floor clean or is the soap dirty?",
            "Your stomach thinks all potatoes are mashed.",
            "An orange is named an orange, but a carrot isn't named an orange.",
            "If a fly loses its wings, is it called a walk?",
            "Every mirror you buy is used."
        ]

    def get_random_event(self):
        """Returns a tuple of (Event_Type, Content)"""
        category = random.choice(["Holiday", "Thought", "Mystery"])
        
        if category == "Holiday":
            return "🎉 Fake Holiday", random.choice(self.holidays)
        elif category == "Thought":
            return "🤔 Shower Thought", random.choice(self.thoughts)
        else:
            return "🎁 Mystery Drop", "You found a rare **Diamond Ore** block! (+50 points)"
