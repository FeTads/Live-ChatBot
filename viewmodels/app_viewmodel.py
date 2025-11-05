from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any
from services.bot_service import BotService
from services.eventsub_service import EventSubService

@dataclass
class AppState:
    busy: bool = False
    status_text: str = ""
    messages: List[tuple] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)

class AppViewModel:
    def __init__(self, bot: BotService, eventsub: EventSubService):
        self.bot = bot; self.eventsub = eventsub
        self.state = AppState()
        self.on_state_changed: Callable[[], None] = lambda: None
