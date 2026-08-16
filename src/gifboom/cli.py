"""gifboom CLI — entry point for all commands."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from gifboom import __version__

app = typer.Typer(
    name="gifboom",
    help="🎬 Search, download, convert, and process GIFs. CLI & AI-ready.",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()

# ─── Sub-apps ────────────────────────────────────────────────────────────────
cache_app = typer.Typer(
    name="cache",
    help="📦 Manage local GIF download cache.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
convert_app = typer.Typer(
    name="convert",
    help="🎬 Convert GIF ↔ Video (MP4/WebM/MOV), trim, and optimize file sizes.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
app.add_typer(cache_app)
app.add_typer(convert_app)


# ─── Global Callback & Version Flag ──────────────────────────────────────────


def version_callback(value: bool):
    """Print version and exit when --version or -v is passed."""
    if value:
        rprint(f"🎬 [bold cyan]gifboom[/bold cyan] version [bold green]v{__version__}[/bold green]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show gifboom version and exit.",
        ),
    ] = None,
):
    """
    🎬 [bold cyan]gifboom[/bold cyan] — The ultimate open-source GIF engine for CLI & AI.

    [bold yellow]⚡ Popular Commands:[/bold yellow]
      🔍 [bold green]gifboom search "happy cat"[/bold green]          Search GIFs across GIPHY, Tenor, KLIPY
      🔑 [bold green]gifboom keys giphy[/bold green]                   Get API key (opens browser dashboard)
      📥 [bold green]gifboom download "q:happy cat"[/bold green]        Search & download top result
      🎬 [bold green]gifboom convert gif2video cat.gif[/bold green]     Convert GIF → MP4 (up to 10× smaller!)
      📽️ [bold green]gifboom convert video2gif clip.mp4[/bold green]    Convert video clip → high-quality GIF
      🖼️ [bold green]gifboom still cat.gif --at 1.5[/bold green]        Extract a single PNG frame
      🗂️ [bold green]gifboom sheet cat.gif --frames 9[/bold green]      Generate a 3×3 PNG frame grid

    💡 Run [bold cyan]gifboom COMMAND --help[/bold cyan] for detailed options and examples.
    """
    pass


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
    query: Annotated[str, typer.Argument(help="Search query term (e.g. 'happy cat', 'dance')")],
    provider: Annotated[
        str | None, typer.Option("--provider", "-p", help="Provider: giphy | tenor | klipy | local")
    ] = None,
    limit: Annotated[
        int, typer.Option("--limit", "-n", help="Max number of results to fetch")
    ] = 10,
    offset: Annotated[int, typer.Option("--offset", help="Pagination offset index")] = 0,
    rating: Annotated[
        str, typer.Option("--rating", "-r", help="Content rating filter: g | pg | pg-13 | r")
    ] = "g",
    fmt: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: plain | json | tsv | markdown | table"),
    ] = "plain",
):
    """
    🔍 Search GIFs across GIPHY, Tenor, KLIPY, or local files.

    Results are printed as plain URLs by default. Use --format to change output.

    Examples:

      gifboom search "happy cat"

      gifboom search "mind blown" --format json --limit 5

      gifboom search "fireworks" --provider tenor --limit 10

      gifboom search "birthday" --provider local

      gifboom search "dance" --format table --rating pg
    """
    from gifboom.providers.registry import get_provider

    p = get_provider(provider)  # type: ignore[arg-type]
    result = _run(p.search(query, limit=limit, offset=offset, rating=rating))

    if fmt == "table":
        table = Table(title=f"[bold]{query}[/] — {result.total} results ({result.provider})")
        table.add_column("ID", style="dim")
        table.add_column("Title")
        table.add_column("Dimensions")
        table.add_column("URL", overflow="fold")
        for item in result.items:
            table.add_row(item.id[:8], item.title[:40], f"{item.width}×{item.height}", item.url)
        console.print(table)
    else:
        _format_result(result.items, fmt)


# ─── download ────────────────────────────────────────────────────────────────


@app.command()
def download(
    url: Annotated[str, typer.Argument(help="Direct GIF URL or search query (e.g. 'q:happy cat')")],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Custom output path for the downloaded .gif"),
    ] = None,
    provider: Annotated[
        str | None, typer.Option("--provider", "-p", help="Provider if using 'q:query' syntax")
    ] = None,
    force: Annotated[
        bool, typer.Option("--force", help="Bypass local disk cache and force re-download")
    ] = False,
):
    """
    📥 Download a GIF by URL or search & auto-save the top result.

    Pass a direct URL to download it, or use the 'q:<query>' syntax
    to search and download the first matching result automatically.

    Examples:

      gifboom download https://media.giphy.com/media/xyz/giphy.gif

      gifboom download https://media.giphy.com/media/xyz/giphy.gif -o ~/Desktop/cat.gif

      gifboom download "q:happy cat" -o ~/Downloads/cat.gif

      gifboom download "q:mind blown" --provider tenor --force
    """
    from gifboom.downloader import download_gif

    if url.startswith("q:"):
        from gifboom.providers.registry import get_provider

        query = url[2:].strip()
        result = _run(get_provider(provider).search(query, limit=1))  # type: ignore
        if not result.items:
            rprint("[red]No results found.[/]")
            raise typer.Exit(1)
        url = result.items[0].url
        rprint(f"[dim]Found:[/] {url}")

    path = _run(download_gif(url, output_path=output, force=force))
    rprint(f"[green]✓[/] Saved: {path}")


# ─── still ───────────────────────────────────────────────────────────────────


@app.command()
def still(
    source: Annotated[str, typer.Argument(help="Path to local GIF or HTTP URL")],
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output PNG path")] = None,
    at: Annotated[
        str, typer.Option("--at", help="Timestamp to extract (e.g. '1.5' or '00:00:01.5')")
    ] = "0",
):
    """
    🖼️ Extract a single PNG frame from a GIF at a given timestamp.

    Useful for creating preview thumbnails or inspecting a specific moment.
    Supports both local files and HTTP URLs.

    Examples:

      gifboom still cat.gif

      gifboom still cat.gif --at 1.5 -o frame.png

      gifboom still https://media.giphy.com/media/xyz/giphy.gif --at 2.0 -o preview.png
    """
    from gifboom.converters import gif_still

    out = output or Path(source).with_suffix(".still.png")
    gif_still(Path(source) if not source.startswith("http") else source, out, at=at)
    rprint(f"[green]✓[/] Saved still frame: {out}")


# ─── sheet ───────────────────────────────────────────────────────────────────


@app.command()
def sheet(
    source: Annotated[str, typer.Argument(help="Path to local GIF or HTTP URL")],
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output PNG path")] = None,
    frames: Annotated[
        int, typer.Option("--frames", "-n", help="Total number of frames to sample")
    ] = 9,
    cols: Annotated[int, typer.Option("--cols", help="Number of columns in grid layout")] = 3,
):
    """
    🗂️ Generate a PNG contact sheet — a grid of frames sampled across the GIF.

    Great for previewing what a GIF looks like without playing it.
    By default creates a 3×3 grid of 9 evenly-spaced frames.

    Examples:

      gifboom sheet cat.gif

      gifboom sheet cat.gif --frames 9 --cols 3 -o preview.png

      gifboom sheet cat.gif --frames 6 --cols 2 -o grid.png
    """
    from gifboom.converters import gif_sheet

    out = output or Path(source).with_suffix(".sheet.png")
    gif_sheet(
        Path(source) if not source.startswith("http") else source, out, frames=frames, cols=cols
    )
    rprint(f"[green]✓[/] Saved contact sheet: {out}")


# ─── convert sub-commands ────────────────────────────────────────────────────


@convert_app.command("gif2video")
def convert_gif2video(
    input: Annotated[Path, typer.Argument(help="Source .gif file path")],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Destination video path (.mp4, .webm, .mov)")
    ],
    crf: Annotated[
        int,
        typer.Option("--crf", help="Video quality/compression (0=lossless, 23=default, 51=worst)"),
    ] = 23,
    fps: Annotated[
        int | None, typer.Option("--fps", help="Target FPS (default keeps source FPS)")
    ] = None,
    scale: Annotated[
        str | None, typer.Option("--scale", help="Scale filter e.g. '640:-1' (width:height)")
    ] = None,
):
    """
    🎬 Convert animated GIF → MP4, WebM, or MOV video.

    Videos are 5–20× smaller than GIFs and play smoother on social media,
    Discord, and websites. Output format is inferred from the file extension.

    Examples:

      gifboom convert gif2video cat.gif -o cat.mp4

      gifboom convert gif2video cat.gif -o cat.webm

      gifboom convert gif2video cat.gif -o cat.mp4 --crf 18

      gifboom convert gif2video cat.gif -o cat.mp4 --fps 30 --scale 1280:-1
    """
    from gifboom.converters import gif_to_video

    out = gif_to_video(input, output, crf=crf, fps=fps, scale=scale)
    orig = input.stat().st_size / (1024 * 1024)
    new = out.stat().st_size / (1024 * 1024)
    rprint(f"[green]✓[/] Converted ({orig:.1f}MB → {new:.1f}MB): {out}")


@convert_app.command("video2gif")
def convert_video2gif(
    input: Annotated[Path, typer.Argument(help="Source video file path (.mp4, .mov, .webm)")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Destination .gif file path")],
    fps: Annotated[int, typer.Option("--fps", help="Target frame rate")] = 15,
    scale: Annotated[str, typer.Option("--scale", help="Scale filter e.g. '480:-1'")] = "480:-1",
    colors: Annotated[int, typer.Option("--colors", help="Palette color depth (2-256)")] = 256,
    start: Annotated[
        str | None,
        typer.Option("--start", "-s", help="Start time timestamp e.g. '00:00:02' or '2.0'"),
    ] = None,
    end: Annotated[
        str | None, typer.Option("--end", "-e", help="End time timestamp e.g. '00:00:07' or '7.0'")
    ] = None,
):
    """
    📽️ Convert video file → high-quality animated GIF (2-pass palette generation).

    Uses a two-pass ffmpeg approach for best color quality. Clip a specific
    time range using --start and --end.

    Examples:

      gifboom convert video2gif clip.mp4 -o clip.gif

      gifboom convert video2gif clip.mp4 -o clip.gif --start 5 --end 10

      gifboom convert video2gif clip.mp4 -o clip.gif --fps 20 --scale 640:-1 --colors 128

      gifboom convert video2gif clip.mp4 -o clip.gif --start 00:01:20 --end 00:01:25
    """
    from gifboom.converters import video_to_gif

    out = video_to_gif(input, output, fps=fps, scale=scale, colors=colors, start=start, end=end)
    rprint(f"[green]✓[/] Converted video → GIF: {out}")


@convert_app.command("optimize")
def convert_optimize(
    input: Annotated[Path, typer.Argument(help="Source .gif file path")],
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Destination .gif path")
    ] = None,
    colors: Annotated[
        int, typer.Option("--colors", help="Reduced color count (e.g. 64 or 128)")
    ] = 128,
):
    """
    ⚡ Reduce GIF file size by lowering color depth (palette quantization).

    Lower --colors = smaller file, fewer colors. Good range is 64–128.
    For Discord emoji the sweet spot is usually --colors 64.

    Examples:

      gifboom convert optimize cat.gif -o cat_small.gif

      gifboom convert optimize cat.gif -o cat_small.gif --colors 64

      gifboom convert optimize emote.gif -o emote_small.gif --colors 32
    """
    from gifboom.converters import gif_optimize

    out = output or input.with_stem(input.stem + "_optimized")
    gif_optimize(input, out, colors=colors)
    orig = input.stat().st_size / 1024
    new = out.stat().st_size / 1024
    rprint(f"[green]✓[/] {orig:.1f}KB → {new:.1f}KB ({(1 - new / orig) * 100:.0f}% smaller): {out}")


@convert_app.command("trim")
def convert_trim(
    input: Annotated[Path, typer.Argument(help="Source .gif file path")],
    start: Annotated[str, typer.Option("--start", "-s", help="Start timestamp e.g. '0.5'")],
    end: Annotated[str, typer.Option("--end", "-e", help="End timestamp e.g. '3.0'")],
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Destination .gif path")
    ] = None,
):
    """✂️ Trim a GIF to a specific time range."""
    from gifboom.converters import gif_trim

    out = output or input.with_stem(input.stem + "_trimmed")
    gif_trim(input, out, start=start, end=end)
    rprint(f"[green]✓[/] Trimmed GIF: {out}")


@convert_app.command("batch")
def convert_batch(
    in_dir: Annotated[Path, typer.Argument(help="Directory containing GIF files to convert")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Target format: mp4 | webm | mov")
    ] = "mp4",
    out_dir: Annotated[
        Path | None, typer.Option("--out-dir", help="Destination output directory")
    ] = None,
    crf: Annotated[int, typer.Option("--crf", help="Video compression level")] = 23,
    fps: Annotated[int | None, typer.Option("--fps", help="Target FPS")] = None,
):
    """📦 Batch convert all GIFs in a directory into videos."""
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
    rprint(f"\n[bold green]Done![/] Processed {len(gifs)} files → {target_dir}")


# ─── cache sub-commands ───────────────────────────────────────────────────────


@cache_app.command("stats")
def cache_stats():
    """📊 Show disk cache statistics (item count and memory size)."""
    from gifboom.downloader import cache_stats as _stats

    s = _stats()
    rprint(f"[bold]Cache Directory:[/] {s['dir']}")
    rprint(f"  Cached Items: {s['items']}")
    rprint(f"  Disk Usage:   {s['size_mb']} MB / {s['limit_gb']} GB")


@cache_app.command("clear")
def cache_clear():
    """🧹 Clear all downloaded GIFs from the local disk cache."""
    from gifboom.downloader import cache_clear as _clear

    _clear()
    rprint("[green]✓[/] Local disk cache cleared.")


# ─── keys ────────────────────────────────────────────────────────────────────


@app.command("keys")
def keys(
    provider: Annotated[
        str | None,
        typer.Argument(help="Provider name: giphy | tenor | klipy (leave empty to list all)"),
    ] = None,
    open_browser: Annotated[
        bool,
        typer.Option("--open/--no-open", "-o", help="Automatically open key portal in web browser"),
    ] = True,
):
    """🔑 List API key portals or launch developer dashboards in web browser."""
    import webbrowser

    from gifboom.providers.registry import get_all_providers_info

    info = get_all_providers_info()
    providers_map = {item["name"]: item for item in info}

    if provider:
        p_name = provider.lower()
        if p_name not in providers_map or not providers_map[p_name]["url"]:
            rprint(
                f"[red]Unknown or keyless provider:[/] {provider}. Available options: giphy, tenor, klipy"
            )
            raise typer.Exit(1)
        item = providers_map[p_name]
        rprint(f"[bold cyan]Launching API key portal for {item['name'].upper()}...[/]")
        rprint(f"🔗 Portal URL: [link={item['url']}]{item['url']}[/link]")
        if item["env_var"]:
            env_var = item["env_var"]
            rprint(
                f"💡 After getting key, set it via: "
                f"[bold green]gifboom config set {env_var}=your_key[/bold green]"
            )
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
            status = (
                "[bold green]Configured ✓[/bold green]"
                if item["configured"]
                else "[bold yellow]Key missing ⚠️[/bold yellow]"
            )
            table.add_row(item["name"], status, item["env_var"], item["url"])

        console.print(table)
        rprint(
            "\n💡 [bold]To open a portal in browser:[/] "
            "[cyan]gifboom keys <provider>[/cyan] (e.g. `gifboom keys giphy`)"
        )
        rprint(
            "💡 [bold]To set your API key:[/] [cyan]gifboom config set GIPHY_API_KEY=your_key[/cyan]\n"
        )


# ─── config ──────────────────────────────────────────────────────────────────


@app.command()
def config(
    action: Annotated[str, typer.Argument(help="Action: show | set KEY=VALUE")],
    key_value: Annotated[
        str | None, typer.Argument(help="Setting to configure e.g. GIPHY_API_KEY=xyz")
    ] = None,
):
    """⚙️ View or update local gifboom settings (~/.gifboom/.env)."""
    from gifboom.config import settings

    env_file = Path.home() / ".gifboom" / ".env"

    if action == "show":
        rprint(f"[bold]gifboom config[/] ({env_file})")
        rprint(f"  GIPHY_API_KEY:    {'***' if settings.giphy_api_key else '[red]not set[/]'}")
        rprint(f"  TENOR_API_KEY:    {'***' if settings.tenor_api_key else '[red]not set[/]'}")
        rprint(f"  KLIPY_API_KEY:    {'***' if settings.klipy_api_key else '[red]not set[/]'}")
        rprint(f"  default_provider: {settings.default_provider}")
        rprint(f"  cache_dir:        {settings.cache_dir}")
    elif action == "set" and key_value:
        env_file.parent.mkdir(parents=True, exist_ok=True)
        lines = env_file.read_text().splitlines() if env_file.exists() else []
        key = key_value.split("=")[0]
        lines = [line for line in lines if not line.startswith(key + "=")]
        lines.append(key_value)
        env_file.write_text("\n".join(lines) + "\n")
        rprint(f"[green]✓[/] Saved {key_value!r} to {env_file}")
    else:
        rprint("[red]Usage:[/] gifboom config show | set KEY=VALUE")


# ─── version ─────────────────────────────────────────────────────────────────


@app.command()
def version():
    """📌 Show gifboom version information."""
    rprint(f"🎬 [bold cyan]gifboom[/bold cyan] version [bold green]v{__version__}[/bold green]")


if __name__ == "__main__":
    app()
