
import requests
from datetime import datetime, timezone

class TwitchAPIService:
    """Pequeno wrapper da Twitch Helix para dados úteis."""
    def __init__(self, config, logger):
        self.config = config
        self.log = logger

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.config.get('api_token') or self.config.get('oauth_token', '')}",
            "Client-Id": self.config.get("client_id", "")
        }

    def get_user(self, login: str):
        try:
            r = requests.get("https://api.twitch.tv/helix/users", params={"login": login}, headers=self._headers(), timeout=6)
            r.raise_for_status()
            data = r.json().get("data", [])
            return data[0] if data else None
        except Exception as e:
            self.log(f"❌ TwitchAPI get_user erro: {e}", "error")
            return None

    def get_stream(self, user_id: str):
        try:
            r = requests.get("https://api.twitch.tv/helix/streams", params={"user_id": user_id}, headers=self._headers(), timeout=6)
            r.raise_for_status()
            data = r.json().get("data", [])
            return data[0] if data else None
        except Exception as e:
            self.log(f"❌ TwitchAPI get_stream erro: {e}", "error")
            return None

    def get_uptime_seconds(self, channel_login: str = None, user_id: str = None) -> int:
        """Retorna uptime em segundos (0 se offline/erro)."""
        try:
            uid = user_id
            if not uid and channel_login:
                u = self.get_user(channel_login)
                uid = u.get("id") if u else None
            if not uid and self.config.get("target_channel_id"):
                uid = str(self.config["target_channel_id"])
            if not uid:
                return 0

            stream = self.get_stream(uid)
            if not stream or stream.get("type") != "live":
                return 0
            started_at = stream.get("started_at")
            if not started_at:
                return 0
            
            dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return max(0, int((now - dt).total_seconds()))
        except Exception as e:
            self.log(f"❌ TwitchAPI uptime erro: {e}", "error")
            return 0
