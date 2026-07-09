import json
import os
from typing import Any, Callable


class PersistableJobState(dict):
    """Dict que persiste su estado cuando se modifica."""

    def __init__(self, data: dict | None = None, persist_cb: Callable[[], None] | None = None):
        super().__init__()
        self._persist_cb = persist_cb
        if data:
            super().update(data)

    def _persist(self) -> None:
        if self._persist_cb is not None:
            self._persist_cb()

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(key, value)
        self._persist()

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        self._persist()

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key in self:
            return self[key]
        super().__setitem__(key, default)
        self._persist()
        return default

    def pop(self, key: str, default: Any = None) -> Any:
        value = super().pop(key, default)
        self._persist()
        return value

    def popitem(self):
        value = super().popitem()
        self._persist()
        return value

    def clear(self) -> None:
        super().clear()
        self._persist()


class JobStore(dict):
    """Almacén de jobs en memoria con persistencia JSON opcional en disco."""

    def __init__(self, storage_dir: str | None = None, filename: str = "jobs.json"):
        super().__init__()
        self.storage_dir = storage_dir or os.getenv("JOB_STORE_DIR") or os.path.join(
            os.path.dirname(__file__), "..", "data", "jobs"
        )
        self.filename = filename
        os.makedirs(self.storage_dir, exist_ok=True)
        self._path = os.path.join(self.storage_dir, filename)
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return

        super().clear()
        for key, value in raw.items():
            if isinstance(value, dict):
                super().__setitem__(key, PersistableJobState(value, self._persist))
            else:
                super().__setitem__(key, value)

    def _persist(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as handle:
                json.dump(self._to_serializable(), handle, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def _to_serializable(self) -> dict:
        return {key: dict(value) if isinstance(value, PersistableJobState) else value for key, value in self.items()}

    def __setitem__(self, key: str, value: Any) -> None:
        if isinstance(value, dict) and not isinstance(value, PersistableJobState):
            value = PersistableJobState(value, self._persist)
        super().__setitem__(key, value)
        self._persist()

    def update(self, *args, **kwargs) -> None:
        for mapping in args:
            if hasattr(mapping, "items"):
                for key, value in mapping.items():
                    self[key] = value
            else:
                raise TypeError("update expected a mapping")
        for key, value in kwargs.items():
            self[key] = value

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key in self:
            return self[key]
        self[key] = default
        return default

    def pop(self, key: str, default: Any = None) -> Any:
        value = super().pop(key, default)
        self._persist()
        return value

    def popitem(self):
        value = super().popitem()
        self._persist()
        return value

    def clear(self) -> None:
        super().clear()
        self._persist()
