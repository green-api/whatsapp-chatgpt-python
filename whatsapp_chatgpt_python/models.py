"""
Data models
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import time


@dataclass
class GPTSessionData:
    """Session data for GPT conversations"""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    last_activity: int = field(default_factory=lambda: int(time.time()))
    user_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    def update_activity(self):
        self.last_activity = int(time.time())
