"""
In-memory task store with thread-safe access.

Suitable for a POC — tasks are lost on restart.
In production, replace with a persistent store (Redis, SQLite, Postgres).
"""
import threading
from typing import Dict, Optional
from app.agents.models import Task


class TaskStore:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()

    def save(self, task: Task) -> Task:
        with self._lock:
            self._tasks[task.id] = task
            return task

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._tasks.get(task_id)


task_store = TaskStore()
