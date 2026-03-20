from __future__ import annotations

from typing import List


class Notifier:
    """In-memory notifier for simple notification checks."""

    def __init__(self) -> None:
        self._messages: List[str] = []

    def notify(self, message: str) -> None:
        """Store a notification message."""
        self._messages.append(str(message))

    def get_messages(self) -> List[str]:
        """Return all notifications generated so far."""
        return list(self._messages)
