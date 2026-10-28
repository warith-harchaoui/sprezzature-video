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
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

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
#: `un` and `une` are missing from the French side on purpose. They are the
#: indefinite article far more often than they are the numeral, so counting
#: them turns ordinary prose into an inventory: "une puce. Un parcours
#: d'arbre" matched, and the `publish` film's French magic beat -- a genuine
#: insight about two code paths that have to agree -- was reported as a
#: feature list. English has no equivalent trap, because the article is "a"
#: and the numeral is "one", so the rule fired in one language and not the
#: other. An inventory whose first item is "un" loses that item here and is
#: still caught by its second, or by the comma-run alternative below.
#: One through nineteen, in both languages, longest alternative first so
#: "dix-sept" is not matched as "dix" with a stray hyphen.
#:
#: `un` and `une` are missing from the French side on purpose; see the note
#: above. English needs no such care because its article is "a".
_UNITS = (
    r"nineteen|eighteen|seventeen|sixteen|fifteen|fourteen|thirteen|twelve|"
    r"eleven|ten|nine|eight|seven|six|five|four|three|two|one|"
    r"dix-neuf|dix-huit|dix-sept|seize|quinze|quatorze|treize|douze|onze|dix|"
    r"neuf|huit|sept|six|cinq|quatre|trois|deux"
)

#: The tens, which take a unit after a hyphen or a space: "forty-two",
#: "quarante-deux", "quatre-vingt-dix". Listed apart from the units so a
#: compound is matched whole rather than as its first half.
_TENS = (
    r"ninety|eighty|seventy|sixty|fifty|forty|thirty|twenty|"
    r"quatre-vingt-dix|quatre-vingts|quatre-vingt|soixante|cinquante|"
    r"quarante|trente|vingt"
)

#: A written or digited count.
#:
#: The teens and the compound tens were absent until 2026-10-28, and their
#: absence had a cost that is worth recording: the suite's own `audio` film
#: spoke "Seventeen characters a second. Forty-two to a line. Two lines at
#: most." -- three published numbers in a row, the textbook inventory this
#: pattern exists to catch -- and the check passed it, because "seventeen"
#: and "forty-two" were not words it knew. A detector missing the obvious
#: case reads as a clean bill of health.
_COUNT = (
    rf"(?:\d+|(?:{_TENS})(?:[- ](?:{_UNITS}))?|{_UNITS}|"
    r"hundred|thousand|million|cent|mille)"
)

#: An inventory: counted noun phrases in a row, or a long comma run.
#:
#: Up to three words may sit between the count and the break, because a real
#: inventory does not always put the noun straight after the number:
#: "Seventeen characters a second. Forty-two to a line." is the shape, and the
#: original pattern -- count, one word, punctuation -- could not see it.
INVENTORY = re.compile(
    rf"(\b{_COUNT}\s+\w+(?:\s+\w+){{0,3}}\s*[,.;]\s*{_COUNT}\s+\w+)"
    r"|(\w+,\s*\w+,\s*\w+,\s*\w+,\s*\w+)",
    re.I,
)

#: Brochure verbs. Unlike an inventory these are a register rather than a
#: proportion: one "supports" in a magic beat is a sentence written by a
#: feature list even when the rest of the beat is not.
BROCHURE = re.compile(
    r"\b(?:supports?|includes?|provides?|offers?|features?|"
    r"prend en charge|comprend|fournit|propose)\b",
    re.I,
)

#: How much of a magic beat an inventory has to cover before the beat *is* an
#: inventory.
#:
#: A share and not a presence, because the two are different findings and the
#: distinction was paid for. The `audio` film's magic beat quotes five
#: published numbers and then says the thing worth saying -- conventions
#: rather than laws, which is why each one is a flag. Reported on presence it
#: is a feature list; measured, the numbers are a fifth of it and the rest is
#: the insight. A check that cannot tell those apart teaches its reader to
#: ignore it.
INVENTORY_SHARE = 0.5

#: Kept under the old name: this module shipped with `FEATURE_LIST` public and
#: a caller elsewhere may hold it. It is the union, which is what that name
#: always meant.
FEATURE_LIST = re.compile(
    f"(?:{INVENTORY.pattern})|(?:{BROCHURE.pattern})", re.I
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


def _words_in(text: str) -> list[str]:
    """The words of a fragment, by the one definition this module uses."""
    return re.findall(r"\b[\w'’-]+\b", text)


def _words(text: str) -> int:
    return len(_words_in(text))


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
    if BROCHURE.search(magic.text):
        report.findings.append(
            f"{film}: the secret sauce is written in brochure "
            f"({BROCHURE.search(magic.text).group(0)!r} in {magic.text!r}). "
            f"A package that \"supports\" something is being described to a "
            f"buyer; the underlying magic is explained to a colleague."
        )
    covered = sum(len(_words_in(m.group(0))) for m in INVENTORY.finditer(magic.text))
    total = _words(magic.text)
    if total and covered / total >= INVENTORY_SHARE:
        report.findings.append(
            f"{film}: the secret sauce is {covered} of its {total} words a "
            f"feature list ({magic.text!r}). Kawasaki's warning applies: the "
            f"underlying magic is the one non-obvious thing that makes the "
            f"solution possible, not an inventory of what ships."
        )
    return report


def from_spec(
    spec: Any,
    scene_text: Callable[[int], str],
    scene_start: Callable[[int], float],
    duration: float,
) -> PitchReport:
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


def scene_of(start: float, scene_starts: list[float]) -> int:
    """
    Which scene is on screen at a given second.

    Parameters
    ----------
    start : float
        A moment in the film, in seconds.
    scene_starts : list of float
        When each scene begins, in film order.

    Returns
    -------
    int
        The index of the last scene that has begun, or ``-1`` when the moment
        falls before the first one.

    Examples
    --------
    >>> scene_of(7.0, [0.0, 5.4, 14.3, 23.3])
    1
    >>> scene_of(0.5, [1.0, 5.4])
    -1
    """
    index = -1
    for n, begins in enumerate(scene_starts):
        if start >= begins:
            index = n
        else:
            break
    return index


def from_narration(spec: Any, lang: str, duration: float) -> PitchReport:
    """
    Build the three beats from what a film **says**, and check them.

    Why the voice and not only the screen
    -------------------------------------
    :func:`from_spec` reads the words a scene puts on screen, and a film whose
    scene list is in Kawasaki's order passes it. That is not the same claim as
    "the film explains itself", because a viewer of a sixty-second film takes
    most of it through the narration: the screen carries one sentence a scene,
    the voice carries eight.

    The suite's own set proved the gap. Every one of eleven films passed
    :func:`from_spec`, and three of them said something else out loud —
    ``audio`` recited its five numbers and never reached the sentence that
    makes them interesting, ``maps`` spent its magic beat on a picture and
    skipped the mechanism, ``sprezzature`` named the vision model and stopped
    one clause short of what you do with what it finds. The beats were right
    on screen and hollow in the voice.

    How a line gets a beat
    ----------------------
    By the picture it lands on. A line's scene is the one on screen when it
    starts, and that scene's beat is already declared in ``spec.pitch`` — so
    there is no second mapping to keep in step with the first. A line written
    to land on the problem scene *is* a problem line, and a voice that is
    still explaining the problem while the solution is on screen shows up here
    as a beat running backwards, which is the inconsistency worth catching.

    Parameters
    ----------
    spec : FilmSpec
        Carries ``scenes``, ``pitch`` and ``narration``.
    lang : str
        Which cut to read.
    duration : float
        The film's length in seconds.

    Returns
    -------
    PitchReport
        Empty findings means the voice delivers the three beats, in order,
        each with the shape its job needs.

    Raises
    ------
    KeyError
        If the spec carries no narration for *lang*. A missing cut is not a
        passing one.
    """
    if lang not in spec.narration:
        raise KeyError(
            f"{getattr(spec, 'name', 'film')}: no {lang} narration to check"
        )

    scene_starts = [float(scene["start"]) for scene in spec.scenes]
    declared = getattr(spec, "pitch", None) or {}
    beat_of_scene = {
        index: name for name, indices in declared.items() for index in indices
    }

    # Numbered as the script numbers them, not looked up afterwards: two
    # identical lines in one script -- a refrain, a repeated CTA -- would make
    # ``list.index`` name the first one twice, and a message pointing at the
    # wrong line is worse than one pointing at none.
    spoken: dict[str, list[tuple[int, Any]]] = {name: [] for name in BEATS}
    for number, line in enumerate(spec.narration[lang], 1):
        name = beat_of_scene.get(scene_of(line.start, scene_starts))
        if name in spoken:
            spoken[name].append((number, line))

    beats: dict[str, Beat] = {}
    for name in BEATS:
        numbered = spoken[name]
        if not numbered:
            continue
        beats[name] = Beat(
            name=name,
            scenes=tuple(
                sorted(
                    {scene_of(line.start, scene_starts) for _n, line in numbered}
                )
            ),
            text=" ".join(line.text for _n, line in numbered).strip(),
            start=min(line.start for _n, line in numbered),
            source=f"{lang} narration, line(s) "
            + ", ".join(str(number) for number, _line in numbered),
        )
    return check(f"{getattr(spec, 'name', 'film')}.{lang}", beats, duration)
