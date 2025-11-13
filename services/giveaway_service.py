
import json, os, threading, time, random
from datetime import datetime

class GiveawayService:
    """Gerencia o estado do sorteio atual e histórico em giveaways.json"""
    def __init__(self, storage_path="giveaways.json", logger=lambda *a, **k: None):
        self.storage_path = storage_path
        self.log = logger
        self._lock = threading.Lock()
        self._data = {"history": [], "current": None}
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            else:
                self._data = {"history": [], "current": None}
        except Exception as e:
            self.log(f"❌ Erro ao carregar {self.storage_path}: {e}", "error")
            self._data = {"history": [], "current": None}

    def _save(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"❌ Erro ao salvar {self.storage_path}: {e}", "error")

    def current(self):
        with self._lock:
            return self._data.get("current") or None

    def history(self):
        with self._lock:
            return list(self._data.get("history", []))

    def create(self, title: str):
        now_iso = datetime.utcnow().isoformat() + "Z"
        with self._lock:
            self._data["current"] = {
                "title": title.strip() or "Sorteio",
                "started_at": now_iso,
                "entrants": [],
                "closed": False,
                "winner": None
            }
            self._save()
        return self._data["current"]

    def close(self, winner: str | None = None):
        with self._lock:
            cur = self._data.get("current")
            if not cur:
                return None
            cur["closed"] = True
            cur["ended_at"] = datetime.utcnow().isoformat() + "Z"
            if winner:
                cur["winner"] = winner

            self._data.setdefault("history", []).insert(0, cur)
            self._data["current"] = None
            self._save()
            return cur

    def enter(self, user: str, tickets: int = 1):
        user = user.strip()
        if not user:
            return False
        
        with self._lock:
            cur = self._data.get("current")
            if not cur or cur.get("closed") or cur.get("winner") is not None:
                return False
   
            cur.setdefault("entrants", [])
            for _ in range(max(1, tickets)):
                cur["entrants"].append(user)

            uniq = sorted(set(cur["entrants"]))
            cur["unique_count"] = len(uniq)
            cur["total_tickets"] = len(cur["entrants"])
            self._save()

            return True

    def pick_winner(self):
        with self._lock:
            cur = self._data.get("current")
            if not cur or not cur.get("entrants"):
                return None
            winner = random.choice(cur["entrants"])
            cur["winner"] = winner
            self._save()
            return winner
