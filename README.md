# gifboom 🎬

> Open-source GIF search, download, conversion, and processing tool — CLI & AI-ready

[![PyPI](https://img.shields.io/pypi/v/gifboom)](https://pypi.org/project/gifboom/)
[![Python](https://img.shields.io/pypi/pyversions/gifboom)](https://pypi.org/project/gifboom/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/gifboom/gifboom/actions/workflows/ci.yml/badge.svg)](https://github.com/gifboom/gifboom/actions)

**gifboom** is a feature-complete open-source alternative to [gifgrep](https://github.com/steipete/gifgrep), extended with video conversion capabilities, API key portal helpers, and native AI integration (MCP & Claude Skill).

## Features

| Feature | Description |
|---|---|
| 🔍 **Search** | GIPHY, Tenor, KLIPY, and local filesystem |
| 🔑 **Keys Portal** | Open developer dashboards to get API keys (`gifboom keys`) |
| 📥 **Download** | Download GIFs by URL or query with smart disk caching |
| 🖼️ **Still** | Extract a single PNG frame at any timestamp |
| 🗂️ **Sheet** | PNG contact sheet (sampled frame grid) |
| 🎬 **GIF → Video** | Convert GIF to MP4 / WebM / MOV |
| 📽️ **Video → GIF** | High-quality two-pass palette conversion |
| ✂️ **Trim** | Clip GIF to a specific time range |
| ⚡ **Optimize** | Reduce GIF color palette and file size |
| 📦 **Batch** | Mass-convert directories of GIFs |
| 🤖 **MCP Server** | Native Model Context Protocol server (9 AI tools) |
| 📋 **Claude Skill** | Standard `SKILL.md` for Claude, Cursor, and Antigravity |

---

## Installation

```bash
pip install gifboom
brew install ffmpeg   # required for video conversion
```

---

## Quick Start

### 1. Get & Set API Keys
```bash
# View available providers and open developer portals in your browser:
gifboom keys              # list all portals and statuses
gifboom keys giphy        # open GIPHY Developer Dashboard in browser
gifboom keys tenor        # open Tenor / Google Cloud Console in browser

# Set API key:
gifboom config set GIPHY_API_KEY=your_key_here
```

### 2. Search & Download
```bash
# Search GIFs (format: plain, json, tsv, markdown, table)
gifboom search "happy cat" --format table

# Download first search result or by direct URL
gifboom download "q:happy cat" --output ~/Downloads/cat.gif
```

### 3. Media Conversion & Processing
```bash
# Extract a frame at 1.5s
gifboom still cat.gif --at 1.5 --output frame.png

# Generate a 3x3 contact sheet grid
gifboom sheet cat.gif --frames 9 --cols 3 --output grid.png

# GIF → MP4 (smaller, web-friendly)
gifboom convert gif2video cat.gif --output cat.mp4

# Video → GIF (high-quality palette)
gifboom convert video2gif video.mp4 --output clip.gif --start 2.0 --end 7.0

# Optimize GIF file size
gifboom convert optimize cat.gif --colors 128 --output cat_small.gif

# Batch convert an entire folder
gifboom convert batch ./gifs/ --format mp4 --out-dir ./videos/
```

---

## AI Agent Integration

### MCP Server (Claude Desktop, Cursor, Antigravity, etc.)

Install MCP dependencies:
```bash
pip install 'gifboom[mcp]'
```

Add to your MCP configuration (e.g. `~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gifboom": {
      "command": "gifboom-mcp",
      "env": {
        "GIPHY_API_KEY": "your_key",
        "TENOR_API_KEY": "your_key"
      }
    }
  }
}
```

**Exposed MCP Tools:** `search_gifs`, `download_gif`, `gif_to_video`, `video_to_gif`, `gif_still`, `gif_sheet`, `gif_trim`, `gif_optimize`, `list_providers`, `open_key_page`.

---

### Claude Skill Standard

The skill definition is available at [`skills/gifboom/SKILL.md`](skills/gifboom/SKILL.md).

To add it to your agent workspace:
```bash
mkdir -p .agents/skills/gifboom
cp skills/gifboom/SKILL.md .agents/skills/gifboom/
```

---

## Available Providers

| Provider | Free Tier | API Key Env Var | Get Key Command |
|---|---|---|---|
| **GIPHY** | 100 req/hr (dev key) | `GIPHY_API_KEY` | `gifboom keys giphy` |
| **Tenor** (Google) | Generous quota | `TENOR_API_KEY` | `gifboom keys tenor` |
| **KLIPY** | Beta (free) | `KLIPY_API_KEY` | `gifboom keys klipy` |
| **local** | No key needed | — | — |

---

## Development

```bash
git clone https://github.com/gifboom/gifboom
cd gifboom
python3.11 -m pip install -e ".[dev]"
pytest tests/ -v
```

---

## License

[MIT](LICENSE) © GifBoom Contributors

## Contributing

Contributions are welcome! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for details.
