"""Settings — reads from env vars or ~/.gifboom/config.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GIFBOOM_",
        env_file=str(Path.home() / ".gifboom" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- API Keys ---
    giphy_api_key: str = Field(default="", alias="GIPHY_API_KEY")
    tenor_api_key: str = Field(default="", alias="TENOR_API_KEY")
    klipy_api_key: str = Field(default="", alias="KLIPY_API_KEY")

    # --- Defaults ---
    default_provider: Literal["giphy", "tenor", "klipy", "local"] = "giphy"
    default_limit: int = 10
    default_output_dir: Path = Path.home() / "Downloads" / "gifboom"

    # --- Cache ---
    cache_dir: Path = Path.home() / ".gifboom" / "cache"
    cache_size_gb: float = 1.0

    # --- Conversion ---
    default_video_crf: int = 23
    default_video_fps: int = 15
    default_gif_colors: int = 256

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=str(Path.home() / ".gifboom" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()
