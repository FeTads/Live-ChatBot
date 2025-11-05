from typing import Any, Dict, Optional
from bot import TwitchChatBot

class _GuiProxy:
    def __init__(self, gui=None):
        self._gui = gui
    def set_gui(self, gui):
        self._gui = gui
    def __getattr__(self, name):
        if self._gui is not None:
            return getattr(self._gui, name)
        raise AttributeError(name)

class BotService:
    """Service do bot, com proxy para GUI."""
    def __init__(self, gui=None, config: Optional[Dict[str, Any]] = None):
        self._gui_proxy = _GuiProxy(gui)
        self._bot = TwitchChatBot(gui=self._gui_proxy, config=config or {})

    def set_gui(self, gui):
        self._gui_proxy.set_gui(gui)
        try:
            self._bot.gui = self._gui_proxy
        except Exception:
            pass

    @property
    def impl(self): return self._bot
    def connect(self): return self._bot.connect()
    def disconnect(self): return self._bot.disconnect()
    def send_message(self, text: str): return self._bot.send_message(text)
    def is_connected(self): return bool(getattr(self._bot, 'connected', False))
