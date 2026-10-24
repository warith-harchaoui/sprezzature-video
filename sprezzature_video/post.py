#!/usr/bin/env python3
"""
What happens to a film after it renders: its poster, and its loudness.

Two jobs, both learned the hard way rather than designed.

**The poster has to be frame 0, not an attribute.** A bare MP4 carries no
poster, and an HTML ``poster=`` attribute only governs the page that serves it.
Slack, X and Discord regenerate their own thumbnail server-side from the first
frame, so the only reliable way to choose the idle image everywhere is to make
frame 0 *be* that image. At 30fps it shows for a thirtieth of a second, which
is imperceptible in playback and decisive in a feed.

**Loudness has to be normalised across a series.** Five films cut on different
days, with narration at one level and a music bed at another, arrive at
different perceived volumes; a viewer who adjusts the volume between two films
of the same series notices the series, not the films. This is the one operation
with no primitive in ``video-helper`` — its surface covers muxing, concat,
overlay, compression and subtitle burn, but not ``loudnorm`` — so it is the
single place here that calls ffmpeg directly, and it is marked as such rather
than hidden.

Everything else goes through ``video-helper``, which already owns the ffmpeg
primitives this needs by name: ``image_loop_to_video``, ``concat_videos``,
``video_dimensions``.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

#: EBU R 128 integrated loudness target, in LUFS. -16 rather than broadcast's
#: -23 because these are watched on phones and in browser tabs, where -23 is
#: quiet enough that people reach for the volume.
TARGET_LUFS = -16.0

#: True peak ceiling, dBTP. -1.5 leaves room for the lossy re-encode a social
#: platform will apply on top, which can push a 0 dBTP master into clipping.
TRUE_PEAK = -1.5


def _ffmpeg() -> str:
    """
    Absolute path to ffmpeg, or a clear failure.

    Raises
    ------
    FileNotFoundError
        If ffmpeg is absent. Named explicitly because the alternative is a
        ``FileNotFoundError`` on the string "ffmpeg" from deep inside
        ``subprocess``, which reads as a bug in this package.
    """
    found = shutil.which("ffmpeg")
    if found is None:
        raise FileNotFoundError("ffmpeg is not on PATH; it is required for post-processing")
    return found


def poster(video: Path | str, out: Path | str, *, at: float) -> Path:
    """
    Write a single frame of *video* as a JPEG.

    Parameters
    ----------
    video : Path or str
        The rendered film.
    out : Path or str
        Destination ``.jpg``.
    at : float
        Time of the frame, in seconds. Choose a moment where the film's
        strongest line is fully on screen — not 0.0, which on a film that fades
        in is a frame of empty paper.

    Returns
    -------
    Path
        The written poster.

    Raises
    ------
    RuntimeError
        If ffmpeg produced no file.
    """
    out = Path(out)
    # -ss before -i seeks by keyframe and is fast; the frame may land slightly
    # off the requested time, which is correct for a poster and wrong for a
    # measurement. Accuracy is not worth a full decode here.
    cmd = [
        _ffmpeg(),
        "-y",
        "-v",
        "error",
        "-ss",
        f"{at}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    if not out.exists():
        raise RuntimeError(f"ffmpeg wrote no poster for {video}")
    return out


def bake_poster(video: Path | str, still: Path | str, out: Path | str) -> Path:
    """
    Prepend *still* as the film's first frame, so feeds pick it as the thumbnail.

    Parameters
    ----------
    video : Path or str
        The rendered film.
    still : Path or str
        The image to become frame 0, normally from :func:`poster`.
    out : Path or str
        Destination video.

    Returns
    -------
    Path
        The written video.

    Notes
    -----
    Built from ``video-helper``'s ``image_loop_to_video`` and ``concat_videos``
    rather than a hand-rolled filtergraph: the concat has to match frame rate
    and dimensions exactly or the join stutters, and that matching is precisely
    what the helper already does.
    """
    import video_helper as vh

    video, still, out = Path(video), Path(still), Path(out)
    probe = vh.video_dimensions(str(video))
    fps = int(round(float(probe.get("fps") or 30)))

    work = out.parent / f".{out.stem}-frame0.mp4"
    try:
        # One frame, at the film's own rate and size, so concat does not
        # re-time or re-scale anything.
        vh.image_loop_to_video(
            str(still),
            1.0 / fps,
            str(work),
            frame_rate=fps,
            width=int(probe["width"]),
            height=int(probe["height"]),
        )
        vh.concat_videos([str(work), str(video)], str(out), frame_rate=fps)
    finally:
        work.unlink(missing_ok=True)
    return out


def normalize_loudness(
    video: Path | str,
    out: Path | str,
    *,
    target: float = TARGET_LUFS,
    peak: float = TRUE_PEAK,
) -> Path:
    """
    Normalise integrated loudness to *target* LUFS, leaving the picture alone.

    Parameters
    ----------
    video : Path or str
        Input film.
    out : Path or str
        Output film.
    target : float
        Integrated loudness target in LUFS.
    peak : float
        True peak ceiling in dBTP.

    Returns
    -------
    Path
        The written film.

    Notes
    -----
    Single-pass ``loudnorm``. A two-pass measure-then-apply is more accurate,
    and for a 20-second film the difference is below what anyone hears while
    doubling the work. The video stream is copied, never re-encoded: a
    loudness fix must not cost a generation of picture quality.

    This is the one direct ffmpeg call in the package — ``video-helper`` has no
    loudness primitive. If one is added there, this function should become a
    call to it.
    """
    out = Path(out)
    cmd = [
        _ffmpeg(),
        "-y",
        "-v",
        "error",
        "-i",
        str(video),
        "-af",
        f"loudnorm=I={target}:TP={peak}:LRA=11",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    if not out.exists():
        raise RuntimeError(f"ffmpeg wrote no output for {video}")
    return out


def measured_loudness(video: Path | str) -> float:
    """
    Integrated loudness of *video* in LUFS, as ffmpeg measures it.

    Useful as a check after :func:`normalize_loudness`: a series whose films
    still differ by more than a decibel was not actually normalised, and
    trusting the command without reading its result is how that goes unnoticed.

    Parameters
    ----------
    video : Path or str
        The film to measure.

    Returns
    -------
    float
        Integrated loudness in LUFS.

    Raises
    ------
    RuntimeError
        If ffmpeg's loudnorm filter reported no integrated value.
    """
    cmd = [
        _ffmpeg(),
        "-hide_banner",
        "-nostats",
        "-i",
        str(video),
        "-af",
        "loudnorm=print_format=summary",
        "-f",
        "null",
        "-",
    ]
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    # loudnorm's summary goes to stderr, and the key is "Input Integrated".
    for line in done.stderr.splitlines():
        if "Input Integrated" in line:
            return float(line.split(":")[1].strip().split()[0])
    raise RuntimeError(f"ffmpeg reported no integrated loudness for {video}")
