"""GIF conversion utilities — GIF ↔ video and GIF processing."""

from __future__ import annotations

import subprocess
from pathlib import Path

from gifboom.resolver import resolve_media_url


def _require_ffmpeg() -> None:
    """Raise if ffmpeg is not installed."""
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "ffmpeg is required for video conversion.\nInstall: brew install ffmpeg  OR  apt install ffmpeg"
        )


def _resolve_input(src: Path | str) -> str:
    s = str(src)
    if s.startswith(("http://", "https://")):
        return resolve_media_url(s)
    return s


def gif_to_video(
    input_path: Path | str,
    output_path: Path,
    crf: int = 23,
    fps: int | None = None,
    scale: str | None = None,
) -> Path:
    """Convert a GIF to MP4 / WebM / MOV.

    Args:
        input_path:  Source .gif file or URL.
        output_path: Destination file. Format inferred from extension.
        crf:         Quality (0=lossless, 51=worst). Default 23.
        fps:         Target frame rate. None = keep source FPS.
        scale:       Scale filter e.g. "640:-1" (width:height, -1 = keep ratio).

    Returns:
        Path to the created file.
    """
    _require_ffmpeg()
    src = _resolve_input(input_path)
    suffix = output_path.suffix.lower()

    vf_parts: list[str] = []
    if scale:
        vf_parts.append(f"scale={scale}")
    if fps:
        vf_parts.append(f"fps={fps}")
    # Smooth palette for GIF source
    vf_parts.append("format=yuv420p")

    vf = ",".join(vf_parts) if vf_parts else "format=yuv420p"

    cmd: list[str] = ["ffmpeg", "-y", "-i", src]

    if suffix == ".webm":
        cmd += ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", str(crf), "-vf", vf]
    else:  # mp4, mov, default
        cmd += ["-c:v", "libx264", "-crf", str(crf), "-vf", vf, "-movflags", "+faststart"]

    cmd.append(str(output_path))
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def video_to_gif(
    input_path: Path | str,
    output_path: Path,
    fps: int = 15,
    scale: str = "480:-1",
    colors: int = 256,
    start: str | None = None,
    end: str | None = None,
) -> Path:
    """Convert video file → high-quality animated GIF (using 2-pass palette).

    Args:
        input_path:  Source video file path or URL.
        output_path: Destination .gif file.
        fps:         Target frame rate. Default 15.
        scale:       Filter scale e.g. "480:-1".
        colors:      Palette size (2-256). Default 256.
        start:       Start timestamp e.g. "00:00:02" or "2.0".
        end:         End timestamp e.g. "00:00:07" or "7.0".

    Returns:
        Path to the created GIF.
    """
    _require_ffmpeg()
    src = _resolve_input(input_path)

    # 1. Generate palette
    palette = output_path.with_suffix(".palette.png")

    ss_args = []
    if start:
        ss_args += ["-ss", start]
    if end:
        ss_args += ["-to", end]

    vf_palette = f"fps={fps},scale={scale}:flags=lanczos,palettegen=max_colors={colors}"
    cmd1 = ["ffmpeg", "-y"] + ss_args + ["-i", src, "-vf", vf_palette, str(palette)]
    subprocess.run(cmd1, check=True, capture_output=True)

    # 2. Render GIF using palette
    vf_use = f"fps={fps},scale={scale}:flags=lanczos[x];[x][1:v]paletteuse"
    cmd2 = ["ffmpeg", "-y"] + ss_args + ["-i", src, "-i", str(palette), "-filter_complex", vf_use, str(output_path)]
    subprocess.run(cmd2, check=True, capture_output=True)

    palette.unlink(missing_ok=True)
    return output_path


def gif_optimize(
    input_path: Path,
    output_path: Path,
    colors: int = 128,
) -> Path:
    """Optimize a GIF by lowering its color depth.

    Args:
        input_path:  Source .gif file.
        output_path: Destination file.
        colors:      Palette color count (2-256). Default 128.

    Returns:
        Path to optimized GIF.
    """
    _require_ffmpeg()
    palette = output_path.with_suffix(".opt_pal.png")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            f"palettegen=max_colors={colors}",
            str(palette),
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-i",
            str(palette),
            "-lavfi",
            "paletteuse",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )
    palette.unlink(missing_ok=True)
    return output_path


def gif_still(
    input_path: Path | str,
    output_path: Path,
    at: str = "0",
) -> Path:
    """Extract a single PNG frame from a GIF.

    Args:
        input_path: Local path or HTTP URL.
        output_path: Destination .png file.
        at: Timestamp e.g. "1.5" (seconds) or "00:00:01.500".

    Returns:
        Path to the PNG file.
    """
    _require_ffmpeg()
    src = _resolve_input(input_path)
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(at), "-i", src, "-frames:v", "1", str(output_path)],
        check=True,
        capture_output=True,
    )
    return output_path


def gif_sheet(
    input_path: Path | str,
    output_path: Path,
    frames: int = 9,
    cols: int = 3,
) -> Path:
    """Generate a PNG contact sheet (grid of frames) from a GIF.

    Args:
        input_path: Local path or HTTP URL.
        output_path: Destination .png file.
        frames: Total number of frames to capture.
        cols: Number of columns in the grid.

    Returns:
        Path to the PNG file.
    """
    _require_ffmpeg()
    src = _resolve_input(input_path)
    rows = -(-frames // cols)  # ceil division
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            src,
            "-vf",
            f"select=not(mod(n\\,1)),scale=160:-1,tile={cols}x{rows}",
            "-frames:v",
            "1",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )
    return output_path


def gif_trim(
    input_path: Path,
    output_path: Path,
    start: str,
    end: str,
) -> Path:
    """Trim a GIF to [start, end] range.

    Args:
        start: Start time e.g. "0.5" or "00:00:00.500".
        end:   End time.
    """
    _require_ffmpeg()
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            start,
            "-to",
            end,
            "-i",
            str(input_path),
            "-lavfi",
            "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )
    return output_path
