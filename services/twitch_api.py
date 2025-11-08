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
        
    def delete_chat_message(self, broadcaster_id: str, moderator_id: str, message_id: str) -> bool:
        """
        Requer escopo: moderator:manage:chat_messages
        DELETE https://api.twitch.tv/helix/moderation/chat?broadcaster_id=...&moderator_id=...&message_id=...
        """
        try:
            url = "https://api.twitch.tv/helix/moderation/chat"
            params = {
                "broadcaster_id": broadcaster_id,
                "moderator_id": moderator_id,
                "message_id": message_id,
            }
            r = requests.delete(url, headers=self._headers(), params=params, timeout=6)
            if r.status_code == 204:
                return True
            else:
                return False
        except Exception as e:
            self.log(f"Helix delete_chat_message erro: {e}", "error")
            return False


    def get_user_id(self, login: str) -> str | None:
        """
        GET https://api.twitch.tv/helix/users?login=<login>
        Retorna o user_id pelo login (sem @). Escopo não é necessário, só Client-Id e Bearer.
        """
        try:
            url = "https://api.twitch.tv/helix/users"
            params = {"login": login.lstrip("@")}
            r = requests.get(url, headers=self._headers(), params=params, timeout=6)
            r.raise_for_status()
            data = r.json()
            arr = data.get("data") or []
            if arr:
                return arr[0].get("id")
            return None
        except Exception as e:
            self.log(f"Helix get_user_id erro: {e}", "error")
            return None

    def timeout_user(self, broadcaster_id: str, moderator_id: str, target_login_or_id: str,
                    duration_seconds: int, reason: str | None = None) -> bool:
        try:
            target_user_id = target_login_or_id
            if not target_user_id.isdigit():
                uid = self.get_user_id(target_login_or_id)
                if not uid:
                    self.log(f"timeout_user: não achei user_id para {target_login_or_id}", "error")
                    return False
                target_user_id = uid

            url = "https://api.twitch.tv/helix/moderation/bans"
            params = {
                "broadcaster_id": str(broadcaster_id),
                "moderator_id": str(moderator_id),
            }
            payload = {
                "data": {
                    "user_id": str(target_user_id),
                    "duration": int(max(1, min(int(duration_seconds), 1209600))),  # 1..14 dias
                    "reason": (reason or "")[:500],  # evita estourar
                }
            }
            r = requests.post(url, headers=self._headers(), params=params, json=payload, timeout=8)
            if r.status_code in (200, 201):
                return True
            else:
                self.log(f"timeout_user falhou: {r.status_code} {r.text}", "error")
                return False
        except Exception as e:
            self.log(f"timeout_user erro: {e}", "error")
            return False

    #TODO: future use cases
    def ban_user(self, broadcaster_id: str, moderator_id: str, target_login_or_id: str,
                 reason: str | None = None) -> bool:
        try:
            target_user_id = target_login_or_id
            if not target_user_id.isdigit():
                uid = self.get_user_id(target_login_or_id)
                if not uid:
                    self.log(f"ban_user: não achei user_id para {target_login_or_id}", "error")
                    return False
                target_user_id = uid

            url = "https://api.twitch.tv/helix/moderation/bans"
            params = {
                "broadcaster_id": str(broadcaster_id),
                "moderator_id": str(moderator_id),
            }
            payload = {
                "data": {
                    "user_id": str(target_user_id),
                    "reason": (reason or "")[:500],
                }
            }
            r = requests.post(url, headers=self._headers(), params=params, json=payload, timeout=8)
            if r.status_code in (200, 201):
                return True
            else:
                self.log(f"ban_user falhou: {r.status_code} {r.text}", "error")
                return False
        except Exception as e:
            self.log(f"ban_user erro: {e}", "error")
            return False

    def unban_user(self, broadcaster_id: str, moderator_id: str, target_login_or_id: str) -> bool:
        try:
            target_user_id = target_login_or_id
            if not target_user_id.isdigit():
                uid = self.get_user_id(target_login_or_id)
                if not uid:
                    self.log(f"unban_user: não achei user_id para {target_login_or_id}", "error")
                    return False
                target_user_id = uid

            url = "https://api.twitch.tv/helix/moderation/bans"
            params = {
                "broadcaster_id": str(broadcaster_id),
                "moderator_id": str(moderator_id),
                "user_id": str(target_user_id),
            }
            r = requests.delete(url, headers=self._headers(), params=params, timeout=6)
            if r.status_code == 204:
                return True
            else:
                self.log(f"unban_user falhou: {r.status_code} {r.text}", "error")
                return False
        except Exception as e:
            self.log(f"unban_user erro: {e}", "error")
            return False