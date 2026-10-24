#!/usr/bin/env python3
"""
Captions for a film, built from the narration script and the **measured**
length of each narration file.

Not transcribed. The text is the script the voice was synthesized from, so it
is exact where a transcriber would only be close — no homophone to repair, no
proper noun to spell wrong, and the French track is a translation of a known
sentence rather than a guess at an audio signal.

The durations are measured here, and that is the one real change from the
script this generalises. That script hard-coded them, with a comment warning
that regenerating a voice line would silently desync the subtitles. It did:
correcting two stale sentences moved them by 43 and 64 milliseconds, and
nothing but a hand edit would have caught it. A number that can be measured
should not be typed.

Timing comes from ``audio_helper.get_audio_duration`` rather than a local
ffprobe call. That is the ai-helpers side of the boundary — video-helper's own
``video_duration`` says in its docstring that it is the mirror of this function
"for the video side", and it raises on an audio-only file, so reaching for it
here would be using the wrong half of a deliberate split.

The WebVTT itself is written by the suite's single VTT module, re-exported from
``sprezzature_audio``. This is not the place for a fifth writer.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

#: Longest caption line before it is split in two. Two short lines read faster
#: than one long one, and a single line wider than the frame is worse than
#: either.
LINE_LIMIT = 58

#: Break *after* these: punctuation keeps its place on the left of a break.
AFTER = (". ", ", ", " ; ")

#: Break *before* these: a connector word moves to the right, so neither half
#: of a split caption reads as a sentence fragment.
BEFORE = (" and ", " et ", " puis ", " then ", " so ", " alors ")


@dataclass(frozen=True)
class Spoken:
    """
    One narration line: when it starts, what it says, and which file says it.

    Parameters
    ----------
    start : float
        Start time in the film, in seconds.
    text : str
        The line, as it was given to the voice.
    audio : Path or None
        The synthesized file. When present its real length is measured; when
        absent, ``duration`` must be supplied.
    duration : float or None
        Length in seconds. Only for lines with no audio file — a translated
        track riding on the original language's timing.
    """

    start: float
    text: str
    audio: Path | None = None
    duration: float | None = None


def measure(path: Path | str) -> float:
    """
    Length of a narration file in seconds.

    Parameters
    ----------
    path : Path or str
        An audio file.

    Returns
    -------
    float
        Duration in seconds.

    Raises
    ------
    FileNotFoundError
        If the file is absent. A missing narration file must not silently
        become a zero-length cue, which would read on screen as a caption that
        never appears.
    """
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"narration file is missing: {target}")

    # Imported lazily: measuring is only needed when a film actually has a
    # voice, and the dependency should not be required to import this module.
    import audio_helper as ah

    return float(ah.get_audio_duration(str(target)))


def split_line(text: str) -> tuple[str, str]:
    """
    Split a long caption at the most balanced sensible break.

    Prefers a break after punctuation, then before a connector word, and only
    falls back to the middle word when neither exists.

    Parameters
    ----------
    text : str
        A caption line longer than :data:`LINE_LIMIT`.

    Returns
    -------
    tuple[str, str]
        The two halves. The second is empty only when *text* is a single word.

    Examples
    --------
    >>> split_line("A command line is a wall. This builds the door.")
    ('A command line is a wall.', 'This builds the door.')
    """
    mid = len(text) / 2
    best: tuple[float, str, str] | None = None

    for seps, keep_left in ((AFTER, True), (BEFORE, False)):
        for sep in seps:
            i = text.find(sep)
            while i != -1:
                cut = i + len(sep.rstrip()) if keep_left else i
                # Refuse breaks that leave a stub: a two-word line on screen
                # for half a cue is noise, not a caption.
                if 14 < cut < len(text) - 14:
                    distance = abs(cut - mid)
                    if best is None or distance < best[0]:
                        best = (distance, text[:cut].strip(), text[cut:].strip())
                i = text.find(sep, i + 1)

    if best is not None:
        return best[1], best[2]

    words = text.split()
    run = 0
    for k, word in enumerate(words):
        run += len(word) + 1
        if run >= mid:
            return " ".join(words[: k + 1]), " ".join(words[k + 1 :])
    return text, ""


def to_cues(lines: list[Spoken]) -> list[tuple[float, float, str]]:
    """
    Turn narration lines into timed cues, splitting the long ones.

    A split line's two halves divide its time in proportion to their lengths,
    so the second half is not still on screen after the voice has moved on.

    Parameters
    ----------
    lines : list[Spoken]
        Narration lines, in order.

    Returns
    -------
    list[tuple[float, float, str]]
        ``(start, end, text)`` triples.

    Raises
    ------
    ValueError
        If a line has neither an audio file nor an explicit duration.
    """
    out: list[tuple[float, float, str]] = []
    for line in lines:
        if line.audio is not None:
            length = measure(line.audio)
        elif line.duration is not None:
            length = line.duration
        else:
            raise ValueError(f"line at {line.start}s has no audio and no duration: {line.text!r}")

        if len(line.text) <= LINE_LIMIT:
            out.append((line.start, line.start + length, line.text))
            continue

        head, tail = split_line(line.text)
        if not tail:
            out.append((line.start, line.start + length, line.text))
            continue
        pivot = line.start + length * (len(head) / (len(head) + len(tail)))
        out += [(line.start, pivot, head), (pivot, line.start + length, tail)]
    return out


def write(lines: list[Spoken], *, translated: bool) -> str:
    """
    Render a WebVTT document for one language of one film.

    Parameters
    ----------
    lines : list[Spoken]
        Narration lines for this language.
    translated : bool
        True for a track in a different language from the audio. Voice tags are
        then omitted: W3C reserves ``<v Name>`` for the same-language captions
        track, and the suite's VTT writer takes the same position.

    Returns
    -------
    str
        A WebVTT document.
    """
    # The suite's one WebVTT writer, re-exported as public API by
    # sprezzature-audio. Imported lazily so this module can be read and tested
    # for its splitting rules without the dependency present.
    from sprezzature_audio import Cue, write_vtt

    cues = [Cue(start=a, end=b, text=t) for a, b, t in to_cues(lines)]
    return str(write_vtt(cues, voices=not translated))
