"""Shared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class GifResult:
    """A single GIF result from any provider."""

    id: str
    title: str
    url: str                  # direct .gif URL
    preview_url: str          # smaller preview
    width: int
    height: int
    size_bytes: int
    duration_s: float | None  # None if unknown
    frame_count: int | None
    provider: Literal["giphy", "tenor", "klipy", "local"]
    tags: list[str] = field(default_factory=list)
    rating: str = "g"


@dataclass
class SearchResult:
    items: list[GifResult]
    total: int
    query: str
    provider: str
    offset: int = 0
