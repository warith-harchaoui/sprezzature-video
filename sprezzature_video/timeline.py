#!/usr/bin/env python3
"""
Where each narration line actually starts, once the engine has spoken it.

The problem this exists for
---------------------------
A film's lines are written to land on scenes: the one about the problem starts
when the problem is on screen, the one about the mechanism when the mechanism
is. So a script carries a *requested* start per line, read off the scene grid.

What it cannot carry is how long a line takes to say. That is a fact about the
engine, and since `speaker-helper` 0.13 sent offline narration to chatterbox in
every language, it is not even a fact about the engine: the same French
sentence, spoken three times, measured 7.520, 6.760 and 6.640 seconds. A grid
typed by hand against one of those measurements is wrong for the next run by up
to a second, at random.

The suite's films met this as a refusal. The narrator checked each line against
the start of the next one, and when a line overran it printed the overrun and
left the previous track in place — correct, and the reason fourteen cuts out of
twenty-two carried a voice that no longer matched their script for days. The
build neither broke nor advanced.

What this module does instead
-----------------------------
A requested start is a *preference*, not a constraint. A line may never begin
before the scene it talks about, and it may never begin before the line in
front of it has finished. So the start is the later of those two, and the
arithmetic runs down the list once:

    start[0] = requested[0]
    start[i] = max(requested[i], start[i-1] + spoken[i-1] + gap)

A line pushed past its scene is still worth reporting — it is a line arriving
after the picture it describes — so :class:`Layout` keeps the drift per line
rather than only the starts. That turns "this film refuses to build" into "line
4 lands 0.8 s late", which is a sentence somebody can act on by cutting eight
words.

The one hard failure left is the one no layout can absorb: a film has sixty
seconds, and a script that does not fit in sixty seconds does not fit. That is
reported as :attr:`Layout.overflow`, in seconds, so the fix is measured rather
than guessed.

Why here and not in the narrator
--------------------------------
Because it is not about narration. It is about a *film*: scenes have starts, a
film has a length, and a line belongs to the scene it describes. The engine is
behind the same seam as the renderer — this module never calls one, it only
takes the lengths one produced.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Silence left between the end of one line and the start of the next when the
#: layout has to push. Not a style choice: two lines butted end to end read as
#: one run-on sentence, and anything above about a third of a second reads as a
#: mistake. A frame at 30 fps is 33 ms, so this is six frames.
DEFAULT_GAP_S = 0.200

#: How late a line may land relative to the scene it was written for before it
#: is worth a word. Below this the viewer cannot tell; above it the voice is
#: describing a picture that has already changed.
DRIFT_NOTE_S = 0.500


@dataclass(frozen=True)
class Placed:
    """
    One narration line, after layout.

    Parameters
    ----------
    index : int
        Position in the script, from zero.
    requested : float
        Where the script asked this line to start, in seconds.
    start : float
        Where it actually starts.
    duration : float
        Measured length of the spoken line, in seconds.
    text : str
        The line, carried through so a report can quote it.
    """

    index: int
    requested: float
    start: float
    duration: float
    text: str = ""

    @property
    def end(self) -> float:
        """When this line stops being heard, in seconds."""
        return self.start + self.duration

    @property
    def drift(self) -> float:
        """How far after its requested start this line landed, in seconds."""
        return self.start - self.requested


@dataclass
class Layout:
    """
    A whole script laid on one timeline.

    Parameters
    ----------
    lines : list[Placed]
        Every line, in film order.
    duration : float
        The film's length in seconds, which the last line may not run past.
    """

    lines: list[Placed] = field(default_factory=list)
    duration: float = 0.0

    @property
    def end(self) -> float:
        """When the last line stops, in seconds. Zero for an empty script."""
        return self.lines[-1].end if self.lines else 0.0

    @property
    def overflow(self) -> float:
        """
        Seconds by which the script runs past the film, zero when it fits.

        This is the only failure a layout cannot absorb. Everything else is
        drift, which is a note; this is a script that has to lose words.
        """
        return max(0.0, self.end - self.duration)

    @property
    def fits(self) -> bool:
        """Whether the script ends before the film does."""
        return self.overflow <= 0.0

    @property
    def drifted(self) -> list[Placed]:
        """Lines that landed more than :data:`DRIFT_NOTE_S` after their scene."""
        return [line for line in self.lines if line.drift > DRIFT_NOTE_S]

    @property
    def starts(self) -> list[float]:
        """Just the start times, which is what an assembler wants."""
        return [line.start for line in self.lines]

    def report(self) -> list[str]:
        """
        What a reader has to know about this layout, worst first.

        Returns
        -------
        list of str
            Empty when the script fits its film and no line drifted far enough
            to notice. The overflow comes first when there is one, because a
            script that does not fit has to be cut before the drift inside it
            is worth reading.
        """
        out: list[str] = []
        if not self.fits:
            out.append(
                f"the script runs {self.overflow:.3f}s past the film's "
                f"{self.duration:.0f}s. No layout fixes that: the words have to "
                f"go. At the rate this track was spoken that is about "
                f"{self._chars_per_second() * self.overflow:.0f} characters."
            )
        for line in self.drifted:
            out.append(
                f"line {line.index + 1} starts at {line.start:.3f}s, "
                f"{line.drift:.3f}s after the {line.requested:.3f}s it was "
                f"written for: {line.text[:60]!r}"
            )
        return out

    def _chars_per_second(self) -> float:
        """
        How fast this track was actually spoken, over the whole script.

        Measured rather than assumed, because the point of saying "about forty
        characters" is to be useful, and a subtitle convention's seventeen is a
        fact about a reader rather than about this engine. Falls back to that
        convention only when there is nothing to measure.
        """
        chars = sum(len(line.text) for line in self.lines)
        spoken = sum(line.duration for line in self.lines)
        return (chars / spoken) if chars and spoken > 0 else 17.0


def lay_out(
    requested: list[float],
    spoken: list[float],
    *,
    duration: float,
    texts: list[str] | None = None,
    gap: float = DEFAULT_GAP_S,
) -> Layout:
    """
    Place each line at the later of the scene it wants and the room it has.

    Parameters
    ----------
    requested : list of float
        Where each line asks to start, in seconds, in film order. Read off the
        scene grid: a line is written to land on the picture it describes.
    spoken : list of float
        Measured length of each line, in seconds, same order and same length as
        *requested*. Measured off the file the engine wrote, never the engine's
        own reported duration — the file is what gets assembled and what a
        player will time against.
    duration : float
        The film's length in seconds.
    texts : list of str, optional
        The lines themselves, carried into the result so a report can quote
        them. Length must match when given.
    gap : float, optional
        Silence inserted when a line has to be pushed behind the one in front
        of it. Defaults to :data:`DEFAULT_GAP_S`.

    Returns
    -------
    Layout
        Every line placed, with its drift, plus whether the script fits.

    Raises
    ------
    ValueError
        If the lists disagree in length, if a requested start or a measured
        length is negative, or if the requested starts run backwards. All three
        are a caller bug rather than a tight script, and a layout computed from
        any of them would be quietly wrong rather than loudly absent.

    Examples
    --------
    A line that overruns pushes the next one, and only the next one:

    >>> out = lay_out([1.0, 5.0, 12.0], [5.0, 3.0, 2.0], duration=60.0)
    >>> [round(s, 2) for s in out.starts]
    [1.0, 6.2, 12.0]
    >>> out.fits
    True

    A script too long for its film says so in seconds:

    >>> out = lay_out([1.0, 30.0], [20.0, 40.0], duration=60.0)
    >>> round(out.overflow, 2)
    10.0
    """
    if len(requested) != len(spoken):
        raise ValueError(
            f"{len(requested)} requested start(s) against {len(spoken)} measured "
            f"length(s): every line needs both"
        )
    if texts is not None and len(texts) != len(requested):
        raise ValueError(
            f"{len(texts)} text(s) against {len(requested)} line(s)"
        )
    for n, (want, length) in enumerate(zip(requested, spoken, strict=True), 1):
        if want < 0:
            raise ValueError(f"line {n} asks to start at {want}s, before the film")
        if length < 0:
            raise ValueError(f"line {n} measured {length}s, which is not a length")
    # Deliberately uneven: each start is compared with the one after it.
    if any(b < a for a, b in zip(requested, requested[1:], strict=False)):
        raise ValueError(
            "the requested starts run backwards; a script is laid out in film "
            "order, so sort it before asking where it lands"
        )

    words = texts if texts is not None else [""] * len(requested)
    placed: list[Placed] = []
    cursor = 0.0
    for index, (want, length, text) in enumerate(
        zip(requested, spoken, words, strict=True)
    ):
        start = want if index == 0 else max(want, cursor + gap)
        placed.append(
            Placed(
                index=index,
                requested=want,
                start=start,
                duration=length,
                text=text,
            )
        )
        cursor = start + length
    return Layout(lines=placed, duration=duration)
