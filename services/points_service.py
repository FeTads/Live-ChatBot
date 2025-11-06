
import json, os, threading

class PointsService:
    """Sistema simples de pontos local, salvo em points.json."""
    def __init__(self, storage_path="points.json", logger=lambda *a, **k: None):
        self.storage_path = storage_path
        self.log = logger
        self._lock = threading.Lock()
        self._data = {}
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            else:
                self._data = {}
        except Exception as e:
            self.log(f"❌ Erro ao carregar {self.storage_path}: {e}", "error")
            self._data = {}

    def _save(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"❌ Erro ao salvar {self.storage_path}: {e}", "error")

    def get(self, user: str) -> int:
        with self._lock:
            return int(self._data.get(user.lower(), 0))

    def add(self, user: str, amount: int) -> int:
        with self._lock:
            u = user.lower()
            self._data[u] = int(self._data.get(u, 0)) + int(amount)
            self._save()
            return self._data[u]

    def set(self, user: str, amount: int) -> int:
        with self._lock:
            u = user.lower()
            self._data[u] = int(amount)
            self._save()
            return self._data[u]

    def transfer(self, from_user: str, to_user: str, amount: int) -> bool:
        if amount <= 0:
            return False
        with self._lock:
            fu, tu = from_user.lower(), to_user.lower()
            if int(self._data.get(fu, 0)) < amount:
                return False
            self._data[fu] = int(self._data.get(fu, 0)) - amount
            self._data[tu] = int(self._data.get(tu, 0)) + amount
            self._save()
            return True
