
import json
import os
import re
from datetime import datetime, timezone

_HUMAN = ((365*24*3600, "ano"), (30*24*3600, "mês"), (7*24*3600, "semana"),
          (24*3600, "dia"), (3600, "hora"), (60, "min"), (1, "s"))

def humanize_seconds(total):
    total = int(total or 0)
    if total <= 0:
        return "0s"
    parts = []
    for secs, name in _HUMAN:
        q, total = divmod(total, secs)
        if q:
            parts.append(f"{q} {name}{'' if q==1 else 's'}")
        if len(parts) >= 2:
            break
    return " ".join(parts)

class VariableResolver:
    """Resolves placeholders like {user}, {watchtime}, {followage}, {points}, {uptime} etc."""
    VAR_RE = re.compile(r"\{([a-zA-Z0-9_]+)\}")

    def __init__(self, config, points_service=None, twitch_api=None, users_path="users.json"):
        self.config = config
        self.points = points_service
        self.api = twitch_api
        self.users_path = users_path
        self._users = self._load_users()

    def _load_users(self):
        p = self.users_path
        try:
            if not os.path.exists(p):
                return {}
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_users(self):
        try:
            with open(self.users_path, "w", encoding="utf-8") as f:
                json.dump(self._users, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def ensure_user(self, username):
        u = self._users.get(username.lower())
        if not u:
            u = {"watchtime": 0, "followed_at": None}
            self._users[username.lower()] = u
        return u

    def get_watchtime(self, username, human=True):
        u = self.ensure_user(username)
        wt = int(u.get("watchtime", 0) or 0)
        return humanize_seconds(wt) if human else wt

    def get_followage(self, username):
        u = self.ensure_user(username)
        fa = u.get("followed_at")
        if not fa:
            return "0s"
        try:
            dt = datetime.fromisoformat(fa.replace("Z","+00:00"))
            now = datetime.now(timezone.utc)
            return humanize_seconds((now - dt).total_seconds())
        except Exception:
            return "0s"

    def format(self, text, username, extra=None):
        extra = extra or {}
        def repl(m):
            key = m.group(1).lower()
            if key == "user": return username
            if key == "channel": return self.config.get("channel", "")
            if key == "watchtime": return str(self.get_watchtime(username, True))
            if key == "watchtime_raw": return str(self.get_watchtime(username, False))
            if key == "followage": return str(self.get_followage(username))
            if key == "points" or key == "balance": 
                if self.points: 
                    return str(self.points.get_balance(username))
                return "0"
            if key == "uptime":
                if self.api: 
                    secs = self.api.get_uptime_seconds()
                    return humanize_seconds(secs)
                return "0s"
            return str(extra.get(key, m.group(0)))
        return self.VAR_RE.sub(repl, text)
