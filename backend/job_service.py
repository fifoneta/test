from __future__ import annotations

from typing import Any

try:
    from .job_store import JobStore
except ImportError:  # pragma: no cover - fallback for direct script execution
    from job_store import JobStore


class JobService:
    """Servicio mínimo para crear, actualizar y consultar jobs del backend."""

    def __init__(self, storage_dir: str | None = None):
        self._store = JobStore(storage_dir=storage_dir)

    def create_job(self, job_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        job = payload or {}
        self._store[job_id] = job
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict[str, Any]:
        return dict(self._store[job_id])

    def get_all(self) -> dict[str, dict[str, Any]]:
        return {job_id: dict(job) for job_id, job in self._store.items()}

    def update_job(self, job_id: str, **updates: Any) -> dict[str, Any]:
        job = self._store.setdefault(job_id, {})
        job.update(updates)
        return self.get_job(job_id)

    def exists(self, job_id: str) -> bool:
        return job_id in self._store

    def delete(self, job_id: str) -> None:
        self._store.pop(job_id, None)
