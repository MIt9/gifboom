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

# Provider → env var name + API key portal URL.
PROVIDER_META: dict[str, dict[str, str]] = {
    "giphy": {
        "env_var": "GIPHY_API_KEY",
        "url": "https://developers.giphy.com/dashboard/",
    },
    "tenor": {
        "env_var": "TENOR_API_KEY",
        "url": "https://developers.google.com/tenor/guides/quickstart",
    },
    "klipy": {
        "env_var": "KLIPY_API_KEY",
        "url": "https://klipy.co/developer",
    },
}


class ProviderNotConfigured(RuntimeError):
    """Raised when a provider requires an API key that isn't set."""

    def __init__(self, provider: str, env_var: str, url: str):
        self.provider = provider
        self.env_var = env_var
        self.url = url
        super().__init__(
            f"Provider '{provider}' requires an API key (env var {env_var}). "
            f"Get one at {url}, then set it via: gifboom config set {env_var}=your_key"
        )


def get_provider(name: ProviderName | None = None) -> BaseProvider:
    """Return a provider instance by name. Falls back to default from settings."""
    provider_name = name or settings.default_provider
    cls = _PROVIDERS.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown provider: {provider_name!r}. Choose from: {list(_PROVIDERS)}")
    instance = cls()
    if not instance.is_configured():
        meta = PROVIDER_META.get(provider_name, {"env_var": "", "url": ""})
        raise ProviderNotConfigured(provider_name, meta["env_var"], meta["url"])
    return instance


def available_providers() -> list[str]:
    """Return names of all configured (usable) providers."""
    return [name for name, cls in _PROVIDERS.items() if cls().is_configured()]


def get_all_providers_info() -> list[dict]:
    """Return detailed metadata for all providers."""
    info = []
    for name, cls in _PROVIDERS.items():
        instance = cls()
        meta = PROVIDER_META.get(name, {})
        info.append(
            {
                "name": name,
                "configured": instance.is_configured(),
                "url": instance.api_key_url or meta.get("url", ""),
                "env_var": meta.get("env_var", ""),
            }
        )
    return info