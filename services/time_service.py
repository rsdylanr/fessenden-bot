import re

class TimeService:
    @staticmethod
    def parse_time(time_str: str):
        """Standardizes loose time formats to HH:MM AM/PM."""
        time_str = time_str.strip().lower()
        
        # Check if AM/PM is missing
        if not re.search(r'[ap]m', time_str):
            return None

        # Match variations of H:MM or H am/pm
        match = re.match(r'^(\d{1,2})(?::(\d{2}))?\s*([ap]m)$', time_str)
        if match:
            hours, minutes, period = match.groups()
            minutes = minutes or "00"
            
            h = int(hours)
            if h < 1 or h > 12:
                return None
                
            return f"{h:02d}:{minutes} {period.upper()}"
        
        return None
