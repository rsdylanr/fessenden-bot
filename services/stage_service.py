import time
from typing import Optional, List, Dict

class StageCoordinationService:
    """
    High-performance logic for Stage Channel moderation.
    Solves Pitfall #40 (State Bleed) and #15 (Memory Management).
    """
    __slots__ = ['queues', 'current_speakers', 'cooldowns', 'interruptions', 'active_config']

    def __init__(self):
        self.queues: Dict[int, List[int]] = {}  # {channel_id: [user_id]}
        self.current_speakers: Dict[int, int] = {}  # {channel_id: user_id}
        self.cooldowns: Dict[int, float] = {}  # {user_id: timestamp}
        self.interruptions: Dict[int, int] = {}  # {user_id: count}
        self.active_config = {"limit": 90, "buffer": 30}

    def update_config(self, limit: int, buffer: int):
        self.active_config["limit"] = limit
        self.active_config["buffer"] = buffer

    def add_to_queue(self, channel_id: int, user_id: int) -> bool:
        if channel_id not in self.queues:
            self.queues[channel_id] = []
        if user_id not in self.queues[channel_id]:
            self.queues[channel_id].append(user_id)
            return True
        return False

    def get_next(self, channel_id: int) -> Optional[int]:
        if channel_id in self.queues and self.queues[channel_id]:
            next_user = self.queues[channel_id].pop(0)
            self.current_speakers[channel_id] = next_user
            return next_user
        return None

    def is_on_cooldown(self, user_id: int) -> bool:
        return time.time() < self.cooldowns.get(user_id, 0)

    def set_cooldown(self, user_id: int, seconds: int):
        self.cooldowns[user_id] = time.time() + seconds

    def log_interruption(self, user_id: int) -> int:
        self.interruptions[user_id] = self.interruptions.get(user_id, 0) + 1
        return self.interruptions[user_id]

    def reset_session(self, channel_id: int):
        if channel_id in self.queues: self.queues[channel_id] = []
        if channel_id in self.current_speakers: del self.current_speakers[channel_id]
        self.interruptions = {}
        self.cooldowns = {}
