from typing import Any, Dict, Optional
import os
from eventsub import TwitchEventSubClient

class _GuiLoggerProxy:
    """Simula a GUI até a real existir, para não quebrar log_message."""
    def __init__(self, gui=None):
        self._gui = gui
    def set_gui(self, gui):
        self._gui = gui
    def log_message(self, *args, **kwargs):
        if self._gui and hasattr(self._gui, "log_message"):
            return self._gui.log_message(*args, **kwargs)

class EventSubService:
    """Adapter fino para TwitchEventSubClient, tolerante a faltas de config."""
    def __init__(self, gui=None, config: Optional[Dict[str, Any]] = None):
        required_defaults = {
            "api_token":    os.getenv("TWITCH_API_TOKEN", ""),
            "client_id":    os.getenv("TWITCH_CLIENT_ID", ""),
            "client_secret":os.getenv("TWITCH_CLIENT_SECRET", ""),
            # "callback_url":  os.getenv("TWITCH_EVENTSUB_CALLBACK", ""),
            # "webhook_secret":os.getenv("TWITCH_EVENTSUB_SECRET", ""),
        }

        cfg = {**required_defaults, **(config or {})}
        self._gui_proxy = _GuiLoggerProxy(gui)
        self._client = TwitchEventSubClient(gui=self._gui_proxy, config=cfg)

    def set_gui(self, gui):
        self._gui_proxy.set_gui(gui)
        try:
            self._client.gui = self._gui_proxy
        except Exception:
            pass

    @property
    def impl(self) -> TwitchEventSubClient:
        return self._client

    def start(self):
        return self._client.start()

    def stop(self):
        return self._client.stop()

    def is_running(self):
        return bool(getattr(self._client, "running", False))
