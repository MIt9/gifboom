<div align="center">

# 🎬 gifboom

### *The ultimate open-source GIF engine for Humans & AI Agents*

[![PyPI Version](https://img.shields.io/pypi/v/gifboom?style=for-the-badge&color=ff4757)](https://pypi.org/project/gifboom/)
[![Python Version](https://img.shields.io/pypi/pyversions/gifboom?style=for-the-badge&color=2ed573)](https://pypi.org/project/gifboom/)
[![License: MIT](https://img.shields.io/badge/License-MIT-70a1ff?style=for-the-badge)](LICENSE)
[![CI Status](https://img.shields.io/github/actions/workflow/status/MIt9/gifboom/ci.yml?branch=main&style=for-the-badge)](https://github.com/MIt9/gifboom/actions)

<br/>

![gifboom hero](https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif)

*"Why spend 20 minutes finding and converting a GIF when `gifboom` can do it in 2 seconds?"*

</div>

---

## 📦 Installation

```bash
pip install gifboom        # pip
uv add gifboom             # uv (recommended)
pipx install gifboom       # pipx — isolated global CLI
```

> **FFmpeg** is required for video/GIF conversion:
> ```bash
> brew install ffmpeg        # macOS
> sudo apt install ffmpeg    # Ubuntu / Debian
> ```

**Optional extras:**
```bash
pip install 'gifboom[mcp]'   # MCP server for Claude Desktop / LobeChat
pip install 'gifboom[tui]'   # Interactive terminal UI
pip install 'gifboom[dev]'   # Dev tools (pytest, ruff, mypy)
```

---

## 🌟 Why gifboom?

We loved tools like [gifgrep](https://github.com/steipete/gifgrep) for searching GIFs right from the terminal. But we kept asking:

> *"Where is the MP4 conversion? Where is video-to-GIF? What about trimming? And why can't my Claude / Cursor AI agent search and send GIFs for me??"* 🤔

So we built **gifboom** — an open-source, lightning-fast Python CLI + MCP Server that does it all:

* 🔍 **Multi-Provider Search** — GIPHY, Tenor, KLIPY, and local folders in one command
* 🎬 **GIF ↔ Video Conversion** — Turn heavy 30MB GIFs into silky 2MB MP4s (or vice versa)
* 🖼️ **Stills & Contact Sheets** — Grab single PNG frames or full 3×3 video grids
* ✂️ **Trim & Shrink** — Slice out the funny 2 seconds and optimize color palettes
* 🤖 **AI-Native** — Give your AI assistant GIF superpowers via CLI Skill or MCP Server

---

## 🚀 Quick Start

```bash
# 1. Get a free API key
gifboom keys giphy    # opens GIPHY Developer Dashboard in browser

# 2. Save your key
gifboom config set GIPHY_API_KEY=your_key_here

# 3. Search & download
gifboom download "q:happy cat" -o ~/Downloads/happy_cat.gif

# 4. Convert to MP4
gifboom convert gif2video ~/Downloads/happy_cat.gif -o ~/Downloads/happy_cat.mp4
```

---

## 🍿 Feature Tour

### 🔍 Search

```bash
gifboom search "excited reaction"               # pretty table
gifboom search "mind blown" --format json       # JSON for scripts & AI
gifboom search "fireworks" --provider tenor     # specific provider
gifboom search "birthday" --provider local      # search local files
```

### 🎬 GIF ↔ Video

```bash
gifboom convert gif2video cat.gif -o cat.mp4                           # GIF → MP4
gifboom convert gif2video cat.gif -o cat.webm                          # GIF → WebM
gifboom convert video2gif movie.mp4 -o clip.gif --start 00:01:20 --end 00:01:25
gifboom convert batch ./my_gifs/ --format mp4 --out-dir ./my_videos/   # batch
```

### 🖼️ Frames & Sheets

```bash
gifboom still dance.gif --at 1.5 -o frame.png          # single PNG frame
gifboom sheet dance.gif --frames 9 --cols 3 -o grid.png # 3×3 contact sheet
```

### ✂️ Trim & Optimize

```bash
gifboom convert trim laugh.gif --start 0.5 --end 2.5 -o clean.gif
gifboom convert optimize emote.gif --colors 64 -o emote_small.gif
```

---

## 🤖 AI Integration — Two Flows

### Flow A — CLI + Agent Skill *(shell-based)*

Best for: **Antigravity, Cursor, Windsurf, Claude Code** — any agent with terminal access.

```
AI Agent
   ├─ reads skills/gifboom/SKILL.md   ← knows every command & flag
   └─ runs gifboom CLI via shell      ← gifboom search / convert / download …
```

```bash
pip install gifboom

# Copy the skill to your agent's skills folder:
cp -r skills/gifboom ~/.agents/skills/gifboom
# or for Antigravity:
cp -r skills/gifboom ~/.gemini/config/skills/gifboom
```

### Flow B — MCP Server *(native tool calls)*

Best for: **Claude Desktop, LobeChat, LibreChat** — clients without shell access.

```
AI Agent
   └─ calls MCP tools directly   ← search_gifs() / gif_to_video() / …
         └─ gifboom MCP server   ← no shell needed, structured JSON
```

```bash
pip install 'gifboom[mcp]'
```

`claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "gifboom": {
      "command": "gifboom",
      "args": ["mcp"]
    }
  }
}
```

**Which flow to use?**

| | Flow A — CLI + Skill | Flow B — MCP |
|---|---|---|
| Requires shell | ✅ | ❌ |
| Claude Desktop | ❌ | ✅ |
| Cursor / Antigravity | ✅ | ✅ |
| Extra install | none | `gifboom[mcp]` |

---

## ⚡ Cheat Sheet

| Task | Command |
|---|---|
| Search & copy URL | `gifboom search "party parrot"` |
| Download by URL | `gifboom download https://... -o meme.gif` |
| Discord emoji | `gifboom convert optimize emote.gif --colors 64 -o small.gif` |
| Trim GIF | `gifboom convert trim laugh.gif --start 0.5 --end 2.5 -o out.gif` |
| WebM for web | `gifboom convert gif2video hero.gif -o hero.webm --crf 28` |
| Cache stats | `gifboom cache stats` |

---

## 🌐 Provider Support

| Provider | Free Tier | Env Variable |
|---|---|---|
| **GIPHY** | 100 req/hr | `GIPHY_API_KEY` |
| **Tenor** | Generous (Google Cloud) | `TENOR_API_KEY` |
| **KLIPY** | Free beta | `KLIPY_API_KEY` |
| **Local** | Unlimited 💾 | — |

Run `gifboom keys <provider>` to open the API key portal in your browser.

---

## 🤝 Contributing

```bash
git clone https://github.com/MIt9/gifboom.git
cd gifboom
pip install -e ".[dev]"
pytest tests/ -v
```

Check out [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

<div align="center">

Made with ❤️ and lots of 🍿 by the Open Source Community.

[License: MIT](LICENSE) • [Report Issue](https://github.com/MIt9/gifboom/issues) • [Star on GitHub ⭐](https://github.com/MIt9/gifboom)

</div>
