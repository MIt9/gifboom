<div align="center">

# 🎬 gifboom

### *The ultimate open-source GIF engine for Humans & AI Agents*

[![PyPI Version](https://img.shields.io/pypi/v/gifboom?style=for-the-badge&color=ff4757)](https://pypi.org/project/gifboom/)
[![Python Version](https://img.shields.io/pypi/pyversions/gifboom?style=for-the-badge&color=2ed573)](https://pypi.org/project/gifboom/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.style=for-the-badge&style=for-the-badge&color=70a1ff)](LICENSE)
[![CI Status](https://img.shields.io/github/actions/workflow/status/MIt9/gifboom/ci.yml?branch=main&style=for-the-badge)](https://github.com/MIt9/gifboom/actions)

<br/>

![gifboom hero](https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif)

*“Why spend 20 minutes finding and converting a GIF when `gifboom` can do it in 2 seconds?”*

</div>

---

## 🌟 Why gifboom?

We loved tools like [gifgrep](https://github.com/steipete/gifgrep) for searching GIFs right from the terminal. But we kept asking:

> *“Where is the MP4 conversion? Where is video-to-GIF? What about trimming? And why can't my Claude / Cursor AI agent search and send GIFs for me??”* 🤔

So we built **gifboom** — an open-source, lightning-fast Python CLI + MCP Server that does it all:

* 🔍 **Multi-Provider Search**: GIPHY, Tenor, KLIPY, and local folders in one command.
* 🎬 **GIF ↔ Video Conversion**: Turn heavy 30MB GIFs into silky 2MB MP4s (or vice versa).
* 🖼️ **Stills & Contact Sheets**: Grab single PNG frames or full 3×3 video grids.
* ✂️ **Trim & Shrink**: Slice out the funny 2 seconds and optimize color palettes.
* 🤖 **AI-Native (MCP & Claude Skill)**: Give your AI assistant the power to search, download, and convert media on command!

---

## 🍿 Feature Tour

### 1. 🔍 Instant GIF Search
Find the perfect reaction without leaving your terminal (or let your script get JSON results).

![Cat Searching](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODp1dndxZXFqazBwZnd2dHc4cjR1NjlzbjBqa3J0dXp6emtyOXFiYjAmZXA9djFfaW50ZXJuYWxfZ2lmX2J5X2lkJmN0PWc/3oKIPnAiaMCws8nOsE/giphy.gif)

```bash
# Pretty table format
gifboom search "excited reaction" --format table

# Pure JSON for scripts & AI
gifboom search "mind blown" --format json --limit 5
```

---

### 2. 🎬 GIF ↔ Video Alchemy
Convert giant animated GIFs into lightweight MP4/WebM videos for Twitter, Discord, or web apps. Or turn video clips into crisp GIFs!

![Transformation Magic](https://media.giphy.com/media/12NUbkX6p4xOO4/giphy.gif)

```bash
# Shrink 40MB GIF → 2MB MP4 (huge bandwidth saver!)
gifboom convert gif2video cat.gif -o cat.mp4

# Convert video clip to high-quality GIF
gifboom convert video2gif movie.mp4 -o clip.gif --start 00:01:20 --end 00:01:25
```

---

### 3. 🖼️ Frame Extractor & Contact Sheets
Need a quick PNG snapshot or a grid breakdown of every keyframe?

![Freeze Frame](https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif)

```bash
# Extract single frame at 1.5 seconds
gifboom still dance.gif --at 1.5 -o frame.png

# Generate a 3×3 grid breakdown of 9 frames
gifboom sheet dance.gif --frames 9 --cols 3 -o grid.png
```

---

### 4. 🤖 AI Superpowers (MCP Server & Claude Skill)
Teach your AI agents (Claude Desktop, Cursor, Antigravity, LobeHub) how to handle GIFs autonomously!

![Robot AI](https://media.giphy.com/media/26n6WywJyh39n1pBu/giphy.gif)

```bash
# Install with MCP support
pip install 'gifboom[mcp]'
```

Your AI can now run tools like `search_gifs`, `download_gif`, `gif_to_video`, `open_key_page`, and more.

> 📋 **Claude Skill file included!** Just drop [`skills/gifboom/SKILL.md`](skills/gifboom/SKILL.md) into your `.agents/skills/gifboom/` directory.

---

## 📦 Installation

> **Available on PyPI:** [`gifboom`](https://pypi.org/project/gifboom/)

```bash
# Recommended — with uv (fastest)
uv add gifboom

# or pip
pip install gifboom

# or pipx (isolated global CLI)
pipx install gifboom
```

> **FFmpeg** is required for all video/GIF conversion features:
> ```bash
> brew install ffmpeg          # macOS
> sudo apt install ffmpeg      # Ubuntu / Debian
> ```

### Optional extras
```bash
pip install 'gifboom[mcp]'   # MCP server support
pip install 'gifboom[tui]'   # Interactive TUI (Textual)
pip install 'gifboom[dev]'   # Dev tools (pytest, ruff, mypy)
```

---

## 🚀 Quick Start

### Step 1: Install (see above)


### Step 2: Get Free API Keys in 1-Click 🔑
Don't have API keys yet? No problem! `gifboom` will launch the developer portals for you:

```bash
# Open developer portals directly in your web browser:
gifboom keys giphy    # Opens GIPHY Developer Dashboard
gifboom keys tenor    # Opens Tenor / Google Cloud Console

# Save your key locally:
gifboom config set GIPHY_API_KEY=your_secret_key_here
```

### Step 3: Boom! 💥
```bash
# Download the top "happy cat" GIF directly
gifboom download "q:happy cat" -o ~/Downloads/happy_cat.gif

# Convert to MP4
gifboom convert gif2video ~/Downloads/happy_cat.gif -o ~/Downloads/happy_cat.mp4

# Batch convert a whole folder of GIFs
gifboom convert batch ./my_gifs/ --format mp4 --out-dir ./my_videos/
```

---

## ⚡ Cheat Sheet & Recipes

| Task | Command |
|---|---|
| **Quick search & copy URL** | `gifboom search "party parrot"` |
| **Download specific URL** | `gifboom download https://media.giphy.com/... -o meme.gif` |
| **Discord Emoji Optimizer** | `gifboom convert optimize emote.gif --colors 64 -o emote_small.gif` |
| **Trim awkward start/end** | `gifboom convert trim laugh.gif --start 0.5 --end 2.5 -o clean_laugh.gif` |
| **WebM for websites** | `gifboom convert gif2video hero.gif -o hero.webm --crf 28` |
| **Check cache size** | `gifboom cache stats` |

---

## 🌐 Provider Support

| Provider | Free Tier | Setup Command | Env Variable |
|---|---|---|---|
| **GIPHY** | 100 req/hr (dev key) | `gifboom keys giphy` | `GIPHY_API_KEY` |
| **Tenor** | Generous (Google Cloud) | `gifboom keys tenor` | `TENOR_API_KEY` |
| **KLIPY** | Free beta | `gifboom keys klipy` | `KLIPY_API_KEY` |
| **Local** | Unlimited 💾 | *No key needed* | — |

---

## 🤝 Contributing

We love pull requests! Whether it's adding new GIF providers, improving conversion speed, or writing documentation:

```bash
git clone https://github.com/MIt9/gifboom.git
cd gifboom
python3.11 -m pip install -e ".[dev]"
pytest tests/ -v
```

Check out our [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

<div align="center">

Made with ❤️ and lots of 🍿 by the Open Source Community.

[License: MIT](LICENSE) • [Report Issue](https://github.com/MIt9/gifboom/issues) • [Star on GitHub ⭐](https://github.com/MIt9/gifboom)

</div>
