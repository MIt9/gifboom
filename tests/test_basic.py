"""gifboom tests — basic smoke tests."""

from __future__ import annotations

import pytest


def test_version():
    from gifboom import __version__

    assert isinstance(__version__, str)
    assert "." in __version__


def test_settings_defaults():
    from gifboom.config import settings

    assert settings.default_limit == 10
    assert settings.default_video_fps == 15


def test_local_provider_no_key_needed():
    from gifboom.providers.local import LocalProvider

    p = LocalProvider(search_dirs=[])
    assert p.is_configured() is True


def test_giphy_requires_key(monkeypatch):
    monkeypatch.setenv("GIPHY_API_KEY", "")
    # Re-import to reload env
    import gifboom.config as cfg

    cfg.settings.giphy_api_key = ""
    from gifboom.providers.giphy import GiphyProvider

    p = GiphyProvider()
    assert p.is_configured() is False


def test_registry_unknown_provider():
    from gifboom.providers.registry import get_provider

    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("nonexistent")  # type: ignore


def test_converter_still_requires_ffmpeg(tmp_path, monkeypatch):
    """_require_ffmpeg should raise if ffmpeg is missing."""
    import subprocess

    from gifboom.converters import _require_ffmpeg

    original_run = subprocess.run

    def mock_run(cmd, **kwargs):
        if cmd[0] == "ffmpeg":

            class R:
                returncode = 1

            return R()
        return original_run(cmd, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)
    with pytest.raises(RuntimeError, match="ffmpeg"):
        _require_ffmpeg()


@pytest.mark.asyncio
async def test_local_provider_search_empty():
    from gifboom.providers.local import LocalProvider

    p = LocalProvider(search_dirs=[])
    result = await p.search("anything")
    assert result.items == []
    assert result.total == 0


def test_get_all_providers_info():
    from gifboom.providers.registry import get_all_providers_info

    info = get_all_providers_info()
    assert len(info) >= 4
    names = [i["name"] for i in info]
    assert "giphy" in names
    assert "tenor" in names
    assert "klipy" in names
    giphy_info = next(i for i in info if i["name"] == "giphy")
    assert giphy_info["url"] == "https://developers.giphy.com/dashboard/"
