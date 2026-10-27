#!/usr/bin/env python3
"""
Problem, solution, secret sauce: is a film actually explaining anything?

A film about a software package has about sixty seconds and one job: leave a
viewer who had never heard of it able to say what it is for. Most of them fail
the same way, by opening on what the thing *is* rather than on what goes
wrong without it. The viewer has no reason to care yet, so they leave.

Guy KAWASAKI's pitch order fixes that, and it is old advice because it works:
state the problem, then the solution, then the underlying magic. His own
framing of the third one is the part people get wrong. It is not a feature
list and it is not a demo; it is the one non-obvious thing that makes the
solution possible, said in plain language, which a competitor does not have.
"Really resist just doing a demo" is the standing warning.

What this module does, and what it refuses to do
------------------------------------------------
It checks the **order and the presence** of the three beats, and the shape of
each one. Whether the problem is the *right* problem stays a human question
and always will.

Three failures it does catch, each seen in this suite's own first set of
films:

**No problem beat at all.** The package's first film opened on "167 chart
kinds, every one hand-authored" — a specification, delivered to somebody with
no reason to want one.

**The magic is a feature list.** "Ten packages. Five surfaces each. One
implementation underneath." Three facts, no insight. The viewer cannot repeat
it to a colleague, which is the test.

**The magic arrives before the problem.** A clever mechanism explained to
somebody who does not yet know what it is for reads as showing off.

How a film declares its beats
-----------------------------
In the spec, next to the claims::

    pitch:
      problem:  [0, 1]     # scene indices
      solution: [2, 3]
      magic:    [4, 5]

Indices rather than a copy of the text, so the check runs against the film
that exists rather than against a description of it that can drift.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

#: The three beats, in the order a viewer needs them.
BEATS = ("problem", "solution", "magic")

#: A magic beat under this many words is a label rather than an explanation.
#: Measured against the suite's own films: the shortest one that reads as an
#: insight is "Hue goes. Saturation goes. Lightness holds." at seven words.
MAGIC_MIN_WORDS = 6

#: A problem beat that starts after this fraction of the film has run leaves
#: the viewer watching a solution to nothing. A minute of film gives about
#: twelve seconds of patience.
PROBLEM_BY = 0.22

#: Shapes that say "feature list" rather than "insight": a run of counted
#: nouns, a comma-separated inventory, a specification.
#: Numbers get spelled out in film text more often than they get written as
#: digits: "Ten packages. Five surfaces each." was the line that failed, and
#: a digits-only pattern cleared it.
_COUNT = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
          r"twelve|twenty|thirty|fifty|hundred|un|une|deux|trois|quatre|cinq|"
          r"six|sept|huit|neuf|dix|onze|douze|vingt|trente|cinquante|cent)")

FEATURE_LIST = re.compile(
    rf"(\b{_COUNT}\s+\w+\s*[,.;]\s*{_COUNT}\s+\w+)"   # "Ten packages. Five surfaces"
    r"|(\w+,\s*\w+,\s*\w+,\s*\w+,\s*\w+)"            # five or more comma items
    r"|(\b(?:supports?|includes?|provides?|offers?|features?|"
    r"prend en charge|comprend|fournit|propose)\b)",
    re.I,
)


@dataclass
class Beat:
    """One of the three, as it appears in a film."""

    name: str
    scenes: tuple[int, ...]
    text: str
    start: float
    #: Where the words came from, for a message a reader can act on.
    source: str = ""


@dataclass
class PitchReport:
    """What the three beats look like in one film."""

    film: str
    beats: dict[str, Beat] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.findings


def _words(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text))


def check(film: str, beats: dict[str, Beat], duration: float) -> PitchReport:
    """Report what a film's three beats get wrong, in the order a fix wants.

    Parameters
    ----------
    film : str
        The film's key, used in every message.
    beats : dict
        ``{"problem": Beat, "solution": Beat, "magic": Beat}``. A missing key
        is itself a finding.
    duration : float
        Seconds, so "the problem arrives late" is a measurement rather than
        an impression.

    Returns
    -------
    PitchReport
        Empty findings means the three beats are present, in order, and each
        has the shape its job needs.
    """
    report = PitchReport(film=film, beats=dict(beats))

    missing = [name for name in BEATS if name not in beats]
    if missing:
        report.findings.append(
            f"{film}: no {' and no '.join(missing)} beat. A film that never "
            f"says what goes wrong is a specification with music."
        )
        return report

    order = [beats[name].start for name in BEATS]
    if order != sorted(order):
        got = ", ".join(f"{n} at {beats[n].start:.1f}s" for n in BEATS)
        report.findings.append(
            f"{film}: the beats run out of order ({got}). A mechanism "
            f"explained before the problem it solves reads as showing off."
        )

    latest = duration * PROBLEM_BY
    if beats["problem"].start > latest:
        report.findings.append(
            f"{film}: the problem arrives at {beats['problem'].start:.1f}s, "
            f"past the {latest:.1f}s a {duration:.0f}s film gets. Until then "
            f"the viewer is watching a solution to nothing."
        )

    magic = beats["magic"]
    if _words(magic.text) < MAGIC_MIN_WORDS:
        report.findings.append(
            f"{film}: the secret sauce is {_words(magic.text)} words "
            f"({magic.text!r}). That is a label, not the insight."
        )
    if FEATURE_LIST.search(magic.text):
        report.findings.append(
            f"{film}: the secret sauce reads as a feature list "
            f"({magic.text!r}). Kawasaki's warning applies: the underlying "
            f"magic is the one non-obvious thing that makes the solution "
            f"possible, not an inventory of what ships."
        )
    return report


def from_spec(spec, scene_text, scene_start, duration: float) -> PitchReport:
    """Build the three beats from a spec's ``pitch:`` block and check them.

    Parameters
    ----------
    spec : FilmSpec
        Carries ``pitch``, a mapping of beat name to scene indices.
    scene_text : callable
        ``index -> str``, the words that scene puts on screen.
    scene_start : callable
        ``index -> float``, when that scene begins.
    duration : float
        The film's length in seconds.
    """
    declared = getattr(spec, "pitch", None) or {}
    beats: dict[str, Beat] = {}
    for name in BEATS:
        indices = tuple(declared.get(name, ()))
        if not indices:
            continue
        beats[name] = Beat(
            name=name,
            scenes=indices,
            text=" ".join(scene_text(i) for i in indices).strip(),
            start=min(scene_start(i) for i in indices),
            source=f"scenes {', '.join(str(i) for i in indices)}",
        )
    return check(getattr(spec, "key", "film"), beats, duration)
