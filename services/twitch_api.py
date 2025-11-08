import requests
from datetime import datetime, timezone


class TwitchAPIService:
    """Wrapper leve da Twitch Helix para dados e ações de moderação."""
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
            r = requests.get(
                "https://api.twitch.tv/helix/users",
                params={"login": login},
                headers=self._headers(),
                timeout=6
            )
            r.raise_for_status()
            data = r.json().get("data", [])
            return data[0] if data else None
        except Exception as e:
            self.log(f"❌ TwitchAPI get_user erro: {e}", "error")
            return None

    def get_user_id(self, login: str) -> str | None:
        try:
            r = requests.get(
                "https://api.twitch.tv/helix/users",
                params={"login": login.lstrip("@")},
                headers=self._headers(),
                timeout=6
            )
            r.raise_for_status()
            data = r.json().get("data") or []
            return data[0].get("id") if data else None
        except Exception as e:
            self.log(f"Helix get_user_id erro: {e}", "error")
            return None

    def get_stream(self, user_id: str):
        try:
            r = requests.get(
                "https://api.twitch.tv/helix/streams",
                params={"user_id": user_id},
                headers=self._headers(),
                timeout=6
            )
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

    def get_chatters(self, broadcaster_id: str, moderator_id: str, first: int = 1000) -> list[str]:
        """
        Requer escopo: moderator:read:chatters
        GET https://api.twitch.tv/helix/chat/chatters?broadcaster_id=...&moderator_id=...&first=...
        Retorna lista de user_logins.
        """
        url = "https://api.twitch.tv/helix/chat/chatters"
        params = {
            "broadcaster_id": str(broadcaster_id),
            "moderator_id": str(moderator_id),
            "first": int(first),
        }
        try:
            r = requests.get(url, headers=self._headers(), params=params, timeout=6)
            if r.status_code == 401 or r.status_code == 403:
                self.log("❌ Token sem escopo 'moderator:read:chatters' ou bot não é mod no canal.", "error")
                return []
            r.raise_for_status()
            data = r.json()
            return [item.get('user_login') for item in data.get('data', []) if item.get('user_login')]
        except requests.exceptions.HTTPError as e:
            code = getattr(e.response, "status_code", None)
            if code == 400:
                self.log("❌ Erro 400: Parâmetros de API incorretos ao buscar chatters.", "error")
            else:
                self.log(f"❌ Erro HTTP {code} ao buscar chatters.", "error")
            return []
        except Exception as e:
            self.log(f"❌ Erro de conexão ao buscar chatters: {e}", "error")
            return []

    def delete_chat_message(self, broadcaster_id: str, moderator_id: str, message_id: str) -> bool:
        """
        Requer escopo: moderator:manage:chat_messages
        DELETE https://api.twitch.tv/helix/moderation/chat?broadcaster_id=...&moderator_id=...&message_id=...
        """
        try:
            url = "https://api.twitch.tv/helix/moderation/chat"
            params = {
                "broadcaster_id": str(broadcaster_id),
                "moderator_id": str(moderator_id),
                "message_id": message_id,
            }
            r = requests.delete(url, headers=self._headers(), params=params, timeout=6)
            return r.status_code == 204
        except Exception as e:
            self.log(f"Helix delete_chat_message erro: {e}", "error")
            return False

    def timeout_user(self, broadcaster_id: str, moderator_id: str, target_login_or_id: str,
                     duration_seconds: int, reason: str | None = None) -> bool:
        """
        Requer escopo: moderator:manage:banned_users
        POST /helix/moderation/bans + duration => timeout
        """
        try:
            target_user_id = target_login_or_id
            if not str(target_user_id).isdigit():
                uid = self.get_user_id(str(target_login_or_id))
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
                    "reason": (reason or "")[:500],
                }
            }
            r = requests.post(url, headers=self._headers(), params=params, json=payload, timeout=8)
            if r.status_code in (200, 201):
                return True
            self.log(f"timeout_user falhou: {r.status_code} {r.text}", "error")
            return False
        except Exception as e:
            self.log(f"timeout_user erro: {e}", "error")
            return False

    def ban_user(self, broadcaster_id: str, moderator_id: str, target_login_or_id: str,
                 reason: str | None = None) -> bool:
        """
        Requer escopo: moderator:manage:banned_users
        POST /helix/moderation/bans (sem duration) => ban permanente
        """
        try:
            target_user_id = target_login_or_id
            if not str(target_user_id).isdigit():
                uid = self.get_user_id(str(target_login_or_id))
                if not uid:
                    self.log(f"ban_user: não achei user_id para {target_login_or_id}", "error")
                    return False
                target_user_id = uid

            url = "https://api.twitch.tv/helix/moderation/bans"
            params = {
                "broadcaster_id": str(broadcaster_id),
                "moderator_id": str(moderator_id),
            }
            payload = {"data": {"user_id": str(target_user_id), "reason": (reason or "")[:500]}}
            r = requests.post(url, headers=self._headers(), params=params, json=payload, timeout=8)
            if r.status_code in (200, 201):
                return True
            self.log(f"ban_user falhou: {r.status_code} {r.text}", "error")
            return False
        except Exception as e:
            self.log(f"ban_user erro: {e}", "error")
            return False

    def unban_user(self, broadcaster_id: str, moderator_id: str, target_login_or_id: str) -> bool:
        """
        Requer escopo: moderator:manage:banned_users
        DELETE /helix/moderation/bans?broadcaster_id=...&moderator_id=...&user_id=...
        """
        try:
            target_user_id = target_login_or_id
            if not str(target_user_id).isdigit():
                uid = self.get_user_id(str(target_login_or_id))
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
            self.log(f"unban_user falhou: {r.status_code} {r.text}", "error")
            return False
        except Exception as e:
            self.log(f"unban_user erro: {e}", "error")
            return False
