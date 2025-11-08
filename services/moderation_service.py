import re
import time

LINK_RE = re.compile(
    r"(https?://|www\.)[^\s]+|([a-z0-9-]+\.)+(com|net|org|gg|io|tv)(/[^\s]*)?",
    re.I
)

class ModerationService:
    def __init__(self, config, logger, send_raw, send_message):
        self.config = config
        self.log = logger
        self.send_raw = send_raw
        self.send_message = send_message
        self._permits = {}
        self.api = None

    def _cfg(self):
        return self.config.get("settings", {}).get("moderation", {})

    def _now(self):
        return time.time()

    def grant_permit(self, username, seconds=None, uses=1):
        cfg = self._cfg()
        if seconds is None:
            seconds = int(cfg.get("permit", {}).get("duration_seconds", 60))

        self._permits[username.lower()] = {
            "exp": self._now() + int(seconds),
            "remaining": int(uses) if uses is not None else 1,
        }

    def _get_permit(self, username):
        info = self._permits.get(username.lower())
        if not info:
            return None
        if self._now() > info.get("exp", 0):
            self._permits.pop(username.lower(), None)
            return None
        return info

    def has_permit(self, username):
        info = self._get_permit(username)
        if not info:
            return False
        return info.get("remaining", 0) > 0

    def _consume_permit_if_link(self, username, text):
        if not LINK_RE.search(text or ""):
            return False

        info = self._get_permit(username)
        if not info:
            return False

        info["remaining"] = max(0, int(info.get("remaining", 0)) - 1)
        if info["remaining"] <= 0:
            self._permits.pop(username.lower(), None)
        else:
            self._permits[username.lower()] = info
        return True

    def guard_message(self, username, text, is_mod=False, is_broadcaster=False, message_id=None):
        cfg = self._cfg()
        if not cfg.get("enabled", True):
            return True

        if is_mod or is_broadcaster:
            return True

        if cfg.get("anti_link_spam", False) and LINK_RE.search(text or ""):
            if self._consume_permit_if_link(username, text or ""):
                return True
            self._punish(username, reason="link não permitido", message_id=message_id)
            return False

        if cfg.get("blacklist_enabled", False):
            words = set(map(str.lower, cfg.get("blacklist_words", [])))
            if words:
                low = (text or "").lower()
                for w in words:
                    if w and w in low:
                        self._punish(username, reason="uso de palavra proibida!", message_id=message_id)
                        return False

        return True

    def _punish(self, username, reason="", message_id=None):
        cfg = self._cfg()
        action = (cfg.get("action") or "both").lower()
        timeout_secs = int(cfg.get("timeout_seconds", 10))

        api = getattr(self, "api", None)
        broadcaster_id = str(self.config["target_channel_id"])
        moderator_id   = str(self.config["bot_user_id"])

        deleted = False
        if action in ("delete", "both") and message_id:
            try:
                if api and hasattr(api, "delete_chat_message"):
                    deleted = bool(api.delete_chat_message(
                        broadcaster_id=broadcaster_id,
                        moderator_id=moderator_id,
                        message_id=message_id
                    ))
            except Exception as e:
                self.log(f"❌ Falha no delete via API: {e}", "error")

        if not deleted and action in ("delete", "both"):
            ok = False
            if api and hasattr(api, "timeout_user"):
                ok = api.timeout_user(broadcaster_id, moderator_id, username, 1, reason)
                deleted = True
            if not ok:
                self.log(f"Falha no delete para {username}", "error")
            
        if action in ("timeout", "both") and timeout_secs > 1:
            ok = False
            if api and hasattr(api, "timeout_user"):
                ok = api.timeout_user(broadcaster_id, moderator_id, username, timeout_secs, reason)
            if not ok:
                self.log(f"Falha no timeout para {username}", "error")

        if cfg.get("punish_message_enabled", True):
            msg_tpl = (cfg.get("punish_message") or "").strip()
            if msg_tpl:
                try:
                    self.send_message(
                        msg_tpl.replace("{user}", username).replace("{reason}", reason)
                    )
                except Exception:
                    pass

