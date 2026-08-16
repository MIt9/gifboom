"""gifboom MCP server — exposes gifboom tools to AI agents via MCP protocol.

Run:
    gifboom-mcp            # stdio transport (Claude Desktop, Cursor)
    gifboom-mcp --http     # HTTP transport (custom integrations)

Claude Desktop config (~/.config/claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "gifboom": {
          "command": "gifboom-mcp",
          "env": {
            "GIPHY_API_KEY": "...",
            "TENOR_API_KEY": "..."
          }
        }
      }
    }
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
from pathlib import Path
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError as e:
    raise ImportError(
        "MCP extra not installed. Run: pip install 'gifboom[mcp]'"
    ) from e

# ─── MCP Server ──────────────────────────────────────────────────────────────

server = Server("gifboom")

# ─── Tool definitions ─────────────────────────────────────────────────────────

TOOLS = [
    Tool(
        name="search_gifs",
        description=(
            "Search for GIFs across multiple providers (GIPHY, Tenor, KLIPY, local). "
            "Returns a list of GIF objects with URLs, titles, dimensions, and metadata."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query e.g. 'happy cat'"},
                "provider": {
                    "type": "string",
                    "enum": ["giphy", "tenor", "klipy", "local"],
                    "description": "GIF provider. Defaults to configured default.",
                },
                "limit": {"type": "integer", "default": 5, "description": "Number of results (1-25)"},
                "offset": {"type": "integer", "default": 0, "description": "Pagination offset"},
                "rating": {"type": "string", "enum": ["g", "pg", "pg-13", "r"], "default": "g"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="download_gif",
        description="Download a GIF from a URL and save it locally. Returns the local file path.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Direct GIF URL"},
                "filename": {"type": "string", "description": "Optional output filename"},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="gif_to_video",
        description=(
            "Convert a GIF file to MP4, WebM, or MOV video. "
            "Requires ffmpeg. Returns the output file path."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to input .gif file"},
                "output_path": {"type": "string", "description": "Path for output video file (.mp4, .webm, .mov)"},
                "crf": {"type": "integer", "default": 23, "description": "Quality (0=lossless, 51=worst)"},
                "fps": {"type": "integer", "description": "Target FPS (optional)"},
                "scale": {"type": "string", "description": "Scale e.g. '640:-1' (optional)"},
            },
            "required": ["input_path", "output_path"],
        },
    ),
    Tool(
        name="video_to_gif",
        description=(
            "Convert a video file (MP4, MOV, WebM, etc.) to an optimized GIF. "
            "Uses two-pass ffmpeg palette for best quality. Returns the output file path."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to input video file"},
                "output_path": {"type": "string", "description": "Path for output .gif file"},
                "fps": {"type": "integer", "default": 15, "description": "Frame rate"},
                "scale": {"type": "string", "default": "480:-1", "description": "Scale filter"},
                "colors": {"type": "integer", "default": 256, "description": "Palette size (2-256)"},
                "start": {"type": "string", "description": "Start time e.g. '1.5' or '00:00:01.5'"},
                "end": {"type": "string", "description": "End time"},
            },
            "required": ["input_path", "output_path"],
        },
    ),
    Tool(
        name="gif_still",
        description="Extract a single PNG frame from a GIF at a specific timestamp.",
        inputSchema={
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "GIF path or URL"},
                "output_path": {"type": "string", "description": "Output .png path"},
                "at": {"type": "string", "default": "0", "description": "Timestamp in seconds e.g. '1.5'"},
            },
            "required": ["source", "output_path"],
        },
    ),
    Tool(
        name="gif_sheet",
        description="Generate a PNG contact sheet (grid of frames) from a GIF.",
        inputSchema={
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "GIF path or URL"},
                "output_path": {"type": "string", "description": "Output .png path"},
                "frames": {"type": "integer", "default": 9, "description": "Total frames to sample"},
                "cols": {"type": "integer", "default": 3, "description": "Grid columns"},
            },
            "required": ["source", "output_path"],
        },
    ),
    Tool(
        name="gif_trim",
        description="Trim a GIF to a specific time range.",
        inputSchema={
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Source .gif path"},
                "output_path": {"type": "string", "description": "Output .gif path"},
                "start": {"type": "string", "description": "Start time e.g. '0.5'"},
                "end": {"type": "string", "description": "End time e.g. '3.0'"},
            },
            "required": ["input_path", "output_path", "start", "end"],
        },
    ),
    Tool(
        name="gif_optimize",
        description="Re-optimize a GIF to reduce file size by reducing color palette.",
        inputSchema={
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Source .gif path"},
                "output_path": {"type": "string", "description": "Output .gif path"},
                "colors": {"type": "integer", "default": 128, "description": "Palette size (2-256)"},
            },
            "required": ["input_path", "output_path"],
        },
    ),
    Tool(
        name="list_providers",
        description="List available GIF providers, configuration status, and API key portal URLs.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="open_key_page",
        description="Get the URL to obtain an API key for a GIF provider (GIPHY, Tenor, KLIPY).",
        inputSchema={
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": ["giphy", "tenor", "klipy"],
                    "description": "Provider name",
                }
            },
            "required": ["provider"],
        },
    ),
]


# ─── Tool handlers ────────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        result = await _dispatch(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def _dispatch(name: str, args: dict) -> Any:
    if name == "search_gifs":
        from gifboom.providers.registry import get_provider
        provider = get_provider(args.get("provider"))  # type: ignore
        result = await provider.search(
            args["query"],
            limit=args.get("limit", 5),
            offset=args.get("offset", 0),
            rating=args.get("rating", "g"),
        )
        return {
            "query": result.query,
            "provider": result.provider,
            "total": result.total,
            "items": [dataclasses.asdict(i) for i in result.items],
        }

    elif name == "download_gif":
        from gifboom.downloader import download_gif
        out_path = Path(args["filename"]) if args.get("filename") else None
        path = await download_gif(args["url"], output_path=out_path)
        return {"path": str(path), "size_bytes": path.stat().st_size}

    elif name == "gif_to_video":
        from gifboom.converters import gif_to_video
        out = gif_to_video(
            Path(args["input_path"]),
            Path(args["output_path"]),
            crf=args.get("crf", 23),
            fps=args.get("fps"),
            scale=args.get("scale"),
        )
        return {"path": str(out), "size_bytes": out.stat().st_size}

    elif name == "video_to_gif":
        from gifboom.converters import video_to_gif
        out = video_to_gif(
            Path(args["input_path"]),
            Path(args["output_path"]),
            fps=args.get("fps", 15),
            scale=args.get("scale", "480:-1"),
            colors=args.get("colors", 256),
            start=args.get("start"),
            end=args.get("end"),
        )
        return {"path": str(out), "size_bytes": out.stat().st_size}

    elif name == "gif_still":
        from gifboom.converters import gif_still
        out = gif_still(args["source"], Path(args["output_path"]), at=args.get("at", "0"))
        return {"path": str(out)}

    elif name == "gif_sheet":
        from gifboom.converters import gif_sheet
        out = gif_sheet(
            args["source"], Path(args["output_path"]),
            frames=args.get("frames", 9), cols=args.get("cols", 3),
        )
        return {"path": str(out)}

    elif name == "gif_trim":
        from gifboom.converters import gif_trim
        out = gif_trim(
            Path(args["input_path"]), Path(args["output_path"]),
            start=args["start"], end=args["end"],
        )
        return {"path": str(out)}

    elif name == "gif_optimize":
        from gifboom.converters import gif_optimize
        out = gif_optimize(
            Path(args["input_path"]), Path(args["output_path"]),
            colors=args.get("colors", 128),
        )
        orig = Path(args["input_path"]).stat().st_size
        new = out.stat().st_size
        return {"path": str(out), "original_bytes": orig, "output_bytes": new, "saved_pct": round((1 - new/orig)*100)}

    elif name == "list_providers":
        from gifboom.providers.registry import get_all_providers_info
        return {"providers": get_all_providers_info()}

    elif name == "open_key_page":
        from gifboom.providers.registry import get_all_providers_info
        info = get_all_providers_info()
        p_name = args["provider"].lower()
        for item in info:
            if item["name"] == p_name:
                return {
                    "provider": p_name,
                    "url": item["url"],
                    "env_var": item["env_var"],
                    "instructions": f"Set key via: gifboom config set {item['env_var']}=your_key",
                }
        raise ValueError(f"Unknown provider: {p_name}")

    else:
        raise ValueError(f"Unknown tool: {name}")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    asyncio.run(stdio_server(server))


if __name__ == "__main__":
    main()
