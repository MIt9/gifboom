"""Base provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from gifboom.models import SearchResult


class BaseProvider(ABC):
    name: str
    api_key_url: str = ""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        rating: str = "g",
    ) -> SearchResult: ...

    @abstractmethod
    async def get_by_id(self, gif_id: str) -> SearchResult: ...

    def is_configured(self) -> bool:
        """Return True if the required API key is set."""
        return True

