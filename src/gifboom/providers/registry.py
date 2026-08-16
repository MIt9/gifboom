"""Provider registry — resolves and returns the right provider."""

from __future__ import annotations

from typing import Literal

from gifboom.config import settings
from gifboom.providers import BaseProvider
from gifboom.providers.giphy import GiphyProvider
from gifboom.providers.klipy import KlipyProvider
from gifboom.providers.local import LocalProvider
from gifboom.providers.tenor import TenorProvider

ProviderName = Literal["giphy", "tenor", "klipy", "local"]

_PROVIDERS: dict[str, type[BaseProvider]] = {
    "giphy": GiphyProvider,
    "tenor": TenorProvider,
    "klipy": KlipyProvider,
    "local": LocalProvider,
}


def get_provider(name: ProviderName | None = None) -> BaseProvider:
    """Return a provider instance by name. Falls back to default from settings."""
    provider_name = name or settings.default_provider
    cls = _PROVIDERS.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown provider: {provider_name!r}. Choose from: {list(_PROVIDERS)}")
    instance = cls()
    if not instance.is_configured():
        raise RuntimeError(
            f"Provider '{provider_name}' requires an API key. "
            f"Set the corresponding env var (e.g. GIPHY_API_KEY) or run: gifboom config set"
        )
    return instance


def available_providers() -> list[str]:
    """Return names of all configured (usable) providers."""
    return [name for name, cls in _PROVIDERS.items() if cls().is_configured()]


def get_all_providers_info() -> list[dict]:
    """Return detailed metadata for all providers."""
    env_vars = {
        "giphy": "GIPHY_API_KEY",
        "tenor": "TENOR_API_KEY",
        "klipy": "KLIPY_API_KEY",
        "local": "",
    }
    info = []
    for name, cls in _PROVIDERS.items():
        instance = cls()
        info.append(
            {
                "name": name,
                "configured": instance.is_configured(),
                "url": instance.api_key_url,
                "env_var": env_vars.get(name, ""),
            }
        )
    return info

