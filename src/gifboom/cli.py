"""gifboom CLI — entry point for all commands."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from gifboom import __version__

app = typer.Typer(
    name="gifboom",
    help="🎬 Search, download, convert and process GIFs. CLI & AI-ready.",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()

# ─── Sub-apps ────────────────────────────────────────────────────────────────
cache_app = typer.Typer(name="cache", help="Manage local cache.", no_args_is_help=True)
convert_app = typer.Typer(name="convert", help="Convert GIF ↔ video.", no_args_is_help=True)
app.add_typer(cache_app)
app.add_typer(convert_app)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _run(coro):
    return asyncio.run(coro)


def _format_result(items, fmt: str):
    if fmt == "json":
        import dataclasses
        print(json.dumps([dataclasses.asdict(i) for i in items], indent=2))
    elif fmt == "tsv":
        for i in items:
            print(f"{i.id}\t{i.title}\t{i.url}\t{i.provider}")
    elif fmt == "markdown":
        for i in items:
            print(f"- [{i.title}]({i.url}) _{i.provider}_")
    else:  # plain
        for i in items:
            print(i.url)


# ─── search ──────────────────────────────────────────────────────────────────

@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    provider: Annotated[Optional[str], typer.Option("--provider", "-p", help="giphy|tenor|klipy|local")] = None,
    limit: Annotated[int, typer.Option("--limit", "-n")] = 10,
    offset: Annotated[int, typer.Option("--offset")] = 0,
    rating: Annotated[str, typer.Option("--rating", "-r", help="g|pg|pg-13|r")] = "g",
    fmt: Annotated[str, typer.Option("--format", "-f", help="plain|json|tsv|markdown")] = "plain",
):
    """Search for GIFs across providers."""
    from gifboom.providers.registry import get_provider
    p = get_provider(provider)  # type: ignore[arg-type]
    result = _run(p.search(query, limit=limit, offset=offset, rating=rating))

    if fmt == "table":
        table = Table(title=f"[bold]{query}[/] — {result.total} results ({result.provider})")
        table.add_column("ID", style="dim")
        table.add_column("Title")
        table.add_column("Size")
        table.add_column("URL", overflow="fold")
        for item in result.items:
            table.add_row(item.id[:8], item.title[:40], f"{item.width}×{item.height}", item.url)
        console.print(table)
    else:
        _format_result(result.items, fmt)


# ─── download ────────────────────────────────────────────────────────────────

@app.command()
def download(
    url: Annotated[str, typer.Argument(help="GIF URL or search query (prefix with 'q:')")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
    provider: Annotated[Optional[str], typer.Option("--provider", "-p")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
):
    """Download a GIF by URL (or search and pick the first result with 'q:<query>')."""
    from gifboom.downloader import download_gif

    if url.startswith("q:"):
        from gifboom.providers.registry import get_provider
        query = url[2:].strip()
        result = _run(get_provider(provider).search(query, limit=1))  # type: ignore
        if not result.items:
            rprint("[red]No results found.[/]")
            raise typer.Exit(1)
        url = result.items[0].url
        rprint(f"[dim]Using:[/] {url}")

    path = _run(download_gif(url, output_path=output, force=force))
    rprint(f"[green]✓[/] Saved: {path}")


# ─── still ───────────────────────────────────────────────────────────────────

@app.command()
def still(
    source: Annotated[str, typer.Argument(help="GIF path or URL")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
    at: Annotated[str, typer.Option("--at", help="Timestamp e.g. 1.5 or 00:00:01.5")] = "0",
):
    """Extract a single PNG frame from a GIF."""
    from gifboom.converters import gif_still
    out = output or Path(source).with_suffix(".still.png")
    gif_still(Path(source) if not source.startswith("http") else source, out, at=at)
    rprint(f"[green]✓[/] Saved still: {out}")


# ─── sheet ───────────────────────────────────────────────────────────────────

@app.command()
def sheet(
    source: Annotated[str, typer.Argument(help="GIF path or URL")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
    frames: Annotated[int, typer.Option("--frames", "-n")] = 9,
    cols: Annotated[int, typer.Option("--cols")] = 3,
):
    """Generate a PNG contact sheet (grid of frames) from a GIF."""
    from gifboom.converters import gif_sheet
    out = output or Path(source).with_suffix(".sheet.png")
    gif_sheet(Path(source) if not source.startswith("http") else source, out, frames=frames, cols=cols)
    rprint(f"[green]✓[/] Saved sheet: {out}")


# ─── convert sub-commands ────────────────────────────────────────────────────

@convert_app.command("gif2video")
def convert_gif2video(
    input: Annotated[Path, typer.Argument(help="Source .gif file")],
    output: Annotated[Path, typer.Option("--output", "-o")],
    crf: Annotated[int, typer.Option("--crf", help="Quality (0=best, 51=worst)")] = 23,
    fps: Annotated[Optional[int], typer.Option("--fps")] = None,
    scale: Annotated[Optional[str], typer.Option("--scale", help="e.g. 640:-1")] = None,
):
    """Convert GIF → MP4 / WebM / MOV."""
    from gifboom.converters import gif_to_video
    out = gif_to_video(input, output, crf=crf, fps=fps, scale=scale)
    rprint(f"[green]✓[/] Converted: {out}")


@convert_app.command("video2gif")
def convert_video2gif(
    input: Annotated[Path, typer.Argument(help="Source video file")],
    output: Annotated[Path, typer.Option("--output", "-o")],
    fps: Annotated[int, typer.Option("--fps")] = 15,
    scale: Annotated[str, typer.Option("--scale")] = "480:-1",
    colors: Annotated[int, typer.Option("--colors", help="Palette size (2-256)")] = 256,
    start: Annotated[Optional[str], typer.Option("--start", "-s")] = None,
    end: Annotated[Optional[str], typer.Option("--end", "-e")] = None,
):
    """Convert video → GIF (two-pass palette, high quality)."""
    from gifboom.converters import video_to_gif
    out = video_to_gif(input, output, fps=fps, scale=scale, colors=colors, start=start, end=end)
    rprint(f"[green]✓[/] Converted: {out}")


@convert_app.command("optimize")
def convert_optimize(
    input: Annotated[Path, typer.Argument(help="Source .gif file")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
    colors: Annotated[int, typer.Option("--colors")] = 128,
):
    """Re-optimize a GIF (reduce colors & file size)."""
    from gifboom.converters import gif_optimize
    out = output or input.with_stem(input.stem + "_optimized")
    gif_optimize(input, out, colors=colors)
    orig = input.stat().st_size / 1024
    new = out.stat().st_size / 1024
    rprint(f"[green]✓[/] {orig:.1f}KB → {new:.1f}KB  ({(1 - new/orig)*100:.0f}% saved): {out}")


@convert_app.command("trim")
def convert_trim(
    input: Annotated[Path, typer.Argument(help="Source .gif file")],
    start: Annotated[str, typer.Option("--start", "-s")],
    end: Annotated[str, typer.Option("--end", "-e")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
):
    """Trim a GIF to [start, end] range."""
    from gifboom.converters import gif_trim
    out = output or input.with_stem(input.stem + "_trimmed")
    gif_trim(input, out, start=start, end=end)
    rprint(f"[green]✓[/] Trimmed: {out}")


@convert_app.command("batch")
def convert_batch(
    in_dir: Annotated[Path, typer.Argument(help="Directory with GIF files")],
    format: Annotated[str, typer.Option("--format", "-f", help="mp4|webm|gif")] = "mp4",
    out_dir: Annotated[Optional[Path], typer.Option("--out-dir")] = None,
    crf: Annotated[int, typer.Option("--crf")] = 23,
    fps: Annotated[Optional[int], typer.Option("--fps")] = None,
):
    """Batch convert all GIFs in a directory."""
    from gifboom.converters import gif_to_video
    target_dir = out_dir or in_dir / "converted"
    target_dir.mkdir(parents=True, exist_ok=True)
    gifs = list(in_dir.glob("*.gif"))
    if not gifs:
        rprint("[yellow]No GIF files found.[/]")
        raise typer.Exit(0)
    for gif in gifs:
        out = target_dir / gif.with_suffix(f".{format}").name
        with console.status(f"Converting {gif.name}..."):
            gif_to_video(gif, out, crf=crf, fps=fps)
        rprint(f"  [green]✓[/] {gif.name} → {out.name}")
    rprint(f"\n[bold green]Done![/] {len(gifs)} files → {target_dir}")


# ─── cache sub-commands ───────────────────────────────────────────────────────

@cache_app.command("stats")
def cache_stats():
    """Show cache statistics."""
    from gifboom.downloader import cache_stats as _stats
    s = _stats()
    rprint(f"[bold]Cache:[/] {s['dir']}")
    rprint(f"  Items:   {s['items']}")
    rprint(f"  Size:    {s['size_mb']} MB / {s['limit_gb']} GB")


@cache_app.command("clear")
def cache_clear():
    """Clear all cached downloads."""
    from gifboom.downloader import cache_clear as _clear
    _clear()
    rprint("[green]✓[/] Cache cleared.")


# ─── keys ────────────────────────────────────────────────────────────────────

@app.command("keys")
def keys(
    provider: Annotated[Optional[str], typer.Argument(help="giphy | tenor | klipy (leave empty to list all)")] = None,
    open_browser: Annotated[bool, typer.Option("--open/--no-open", "-o", help="Open developer portal in web browser")] = True,
):
    """Open provider portal in browser to obtain API keys."""
    import webbrowser
    from gifboom.providers.registry import get_all_providers_info

    info = get_all_providers_info()
    providers_map = {item["name"]: item for item in info}

    if provider:
        p_name = provider.lower()
        if p_name not in providers_map or not providers_map[p_name]["url"]:
            rprint(f"[red]Unknown or keyless provider:[/] {provider}. Choose from: giphy, tenor, klipy")
            raise typer.Exit(1)
        item = providers_map[p_name]
        rprint(f"[bold cyan]Opening API key page for {item['name'].upper()}...[/]")
        rprint(f"🔗 URL: [link={item['url']}]{item['url']}[/link]")
        if item["env_var"]:
            rprint(f"💡 After obtaining key, set it via: [bold green]gifboom config set {item['env_var']}=your_key[/bold green]")
        if open_browser:
            webbrowser.open(item["url"])
    else:
        table = Table(title="🔑 GIF Providers & API Key Portals")
        table.add_column("Provider", style="bold")
        table.add_column("Status")
        table.add_column("Env Var")
        table.add_column("API Key Portal URL")

        for item in info:
            if not item["url"]:
                continue
            status = "[green]Configured[/green]" if item["configured"] else "[yellow]Key missing[/yellow]"
            table.add_row(item["name"], status, item["env_var"], item["url"])

        console.print(table)
        rprint("\n💡 [bold]To open a portal in browser:[/] `gifboom keys <provider>` (e.g. `gifboom keys giphy`)")
        rprint("💡 [bold]To set your key:[/] `gifboom config set GIPHY_API_KEY=your_key`\n")


# ─── config ──────────────────────────────────────────────────────────────────

@app.command()
def config(
    action: Annotated[str, typer.Argument(help="show | set KEY=VALUE")],
    key_value: Annotated[Optional[str], typer.Argument()] = None,
):
    """Show or set configuration values."""
    from gifboom.config import settings
    env_file = Path.home() / ".gifboom" / ".env"

    if action == "show":
        rprint(f"[bold]gifboom config[/] ({env_file})")
        rprint(f"  GIPHY_API_KEY:  {'***' if settings.giphy_api_key else '[red]not set[/]'}")
        rprint(f"  TENOR_API_KEY:  {'***' if settings.tenor_api_key else '[red]not set[/]'}")
        rprint(f"  KLIPY_API_KEY:  {'***' if settings.klipy_api_key else '[red]not set[/]'}")
        rprint(f"  default_provider: {settings.default_provider}")
        rprint(f"  cache_dir: {settings.cache_dir}")
    elif action == "set" and key_value:
        env_file.parent.mkdir(parents=True, exist_ok=True)
        lines = env_file.read_text().splitlines() if env_file.exists() else []
        key = key_value.split("=")[0]
        lines = [l for l in lines if not l.startswith(key + "=")]
        lines.append(key_value)
        env_file.write_text("\n".join(lines) + "\n")
        rprint(f"[green]✓[/] Set {key_value!r} in {env_file}")
    else:
        rprint("[red]Usage:[/] gifboom config show | set KEY=VALUE")



# ─── version ─────────────────────────────────────────────────────────────────

@app.command()
def version():
    """Show gifboom version."""
    rprint(f"gifboom [bold]{__version__}[/]")


if __name__ == "__main__":
    app()
