#!/usr/bin/env python3
"""
A film asserts things about a project. This module is where those assertions
are checked against the project itself.

The problem is specific and it has already happened. The five films serving on
sprezzature.ai say **"127 chart kinds"** on screen. The catalogue they describe
holds 167 entries and has since September. The number is baked into ten
``index.html`` files and into five rendered MP4s, so nothing short of a re-cut
can correct it — and nothing anywhere was watching. A film is the one artefact
in the suite that makes claims about the code while living outside it, which is
exactly why it drifts: prose in a README gets read, a number burned into a
keyframe does not.

So a claim here is not a copywriting note. It is a declared pair — the text on
screen, and the place in the code that decides whether that text is true — and
it is checked in **both directions**:

``verify_all``
    every declared claim still matches what the code says;
``undeclared_numbers``
    every number visible in the composition is a declared claim. Without this
    half, the guard only protects the numbers someone remembered to declare,
    which is the same as protecting the ones that were never going to drift.

Only *visible* text is scanned. Stylesheet lengths, keyframe percentages,
animation offsets and hex colours are numbers too, and counting them would
bury the four or five assertions that matter under several hundred that do not
— a measure nobody can read is a measure nobody runs.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Literal

#: How a claim's true value is read out of the code. Each one is deliberately
#: dull: a claim must be checkable by a reader holding the repository, not by
#: running the project.
Method = Literal["json_len", "json_key_len", "regex_count", "line_count", "literal"]

#: Elements whose text content is markup machinery, never something a viewer
#: reads. Their contents are dropped before any number is counted.
_NON_VISIBLE_TAGS = frozenset({"style", "script", "template", "head", "title", "meta"})

#: A run of digits, optionally with thousands separators or a decimal part.
#: Deliberately not anchored to word boundaries on the left: "x127" should
#: still surface, because on screen it reads as a number.
#:
#: The plain space in the separator set is load-bearing, not generosity. The
#: French thousands separator is U+00A0, so this class first listed only
#: that -- and the branch could never fire, because `visible_text` collapses
#: runs of `\s` and Python counts U+00A0 as whitespace, so "1 000" always
#: arrived here already spaced with U+0020. Both forms are listed now, so the
#: rule holds whether a caller passes raw markup or normalised text.
_NUMBER = re.compile("\\d[\\d ,._\u00a0\u202f]*\\d|\\d")


class _VisibleText(HTMLParser):
    """
    Collect the text a viewer would actually see in a composition.

    A composition is HTML, so the cheap way to find its claims is to read its
    text. The care is all in what to leave out: ``<style>`` carries hundreds of
    numbers and ``<script>`` carries hundreds more, and none of them are
    assertions about the project.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        # A counter, not a boolean: nested suppressed elements are legal, and a
        # boolean would re-enable collection at the first inner close tag.
        self._suppressed = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _NON_VISIBLE_TAGS:
            self._suppressed += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _NON_VISIBLE_TAGS and self._suppressed:
            self._suppressed -= 1

    def handle_data(self, data: str) -> None:
        if not self._suppressed:
            self.chunks.append(data)

    @property
    def text(self) -> str:
        """The visible text, runs of whitespace collapsed to single spaces."""
        return re.sub(r"\s+", " ", " ".join(self.chunks)).strip()


@dataclass(frozen=True)
class ClaimSource:
    """
    Where a claim's truth is read from.

    Parameters
    ----------
    path : str
        Path to the deciding file, relative to the root passed to
        :func:`verify`. May reach into a sibling repository
        (``sprezzature-figures/...``), which is how a film about the whole
        suite checks a claim about one brick.
    method : Method
        How to turn that file into the claimed value. ``json_len`` is the
        length of a parsed JSON array; ``json_key_len`` the length of the value
        at ``selector``; ``regex_count`` the number of matches of ``selector``;
        ``line_count`` the number of non-blank lines; ``literal`` asserts
        ``selector`` appears in the file verbatim.
    selector : str
        The key, pattern or string the method needs. Unused by ``json_len``
        and ``line_count``.
    """

    path: str
    method: Method
    selector: str = ""


@dataclass(frozen=True)
class Claim:
    """
    One assertion a film makes, and where it is checked.

    Parameters
    ----------
    text : str
        The assertion as it appears on screen, verbatim. Kept because the
        failure message has to let a reader find the frame to re-cut, and a
        bare number does not.
    value : int or str
        The asserted value. An ``int`` for a count; a ``str`` for a
        ``literal`` claim.
    source : ClaimSource
        The place in the code that decides whether ``value`` is still true.
    """

    text: str
    value: int | str
    source: ClaimSource


@dataclass(frozen=True)
class Verdict:
    """The result of checking one claim. ``ok`` is the only thing CI reads."""

    claim: Claim
    actual: int | str | None
    ok: bool
    detail: str


def visible_text(html: str) -> str:
    """
    Extract the text a viewer sees from a composition's HTML.

    Parameters
    ----------
    html : str
        The composition markup.

    Returns
    -------
    str
        Visible text with whitespace collapsed. ``<style>``, ``<script>`` and
        document-head content are excluded.

    Examples
    --------
    >>> visible_text("<style>.a{width:127px}</style><p>167 kinds</p>")
    '167 kinds'
    """
    parser = _VisibleText()
    parser.feed(html)
    parser.close()
    return parser.text


def numbers_in(text: str) -> list[str]:
    """
    Every number appearing in *text*, in order, as written.

    Returns the written form rather than an ``int`` because that is what has to
    appear in a failure message: a viewer looking for "1,000" will not find
    "1000".

    Parameters
    ----------
    text : str
        Visible text, normally from :func:`visible_text`.

    Returns
    -------
    list[str]
        The numbers as they appear, duplicates kept.
    """
    return _NUMBER.findall(text)


def _as_int(written: str) -> int | None:
    """Parse a written number, tolerating the separators a designer may use."""
    # Non-breaking space is the French thousands separator and appears in the
    # suite's own French compositions; a plain comma or period may be either a
    # separator or a decimal point, and for a count the distinction does not
    # matter because a count is never fractional.
    cleaned = written
    for sep in (" ", "\u00a0", "\u202f", ",", "_", "."):
        cleaned = cleaned.replace(sep, "")
    try:
        return int(cleaned)
    except ValueError:
        return None


def read_actual(source: ClaimSource, root: Path | str) -> int | str:
    """
    Read a claim's true value out of the code.

    Parameters
    ----------
    source : ClaimSource
        What to read and how.
    root : Path or str
        Directory ``source.path`` is relative to.

    Returns
    -------
    int or str
        The count, or for a ``literal`` claim the selector when it was found.

    Raises
    ------
    FileNotFoundError
        If the deciding file is absent. Deliberately not swallowed: a claim
        whose source has moved is unverified, and unverified must not read as
        verified. This is the failure mode that let "127" survive.
    ValueError
        If the method cannot be applied to the file's contents.
    """
    target = Path(root) / source.path
    if not target.exists():
        raise FileNotFoundError(f"claim source is missing: {target}")

    if source.method == "json_len":
        parsed = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(parsed, list):
            raise ValueError(f"{source.path}: json_len needs a top-level array")
        return len(parsed)

    if source.method == "json_key_len":
        parsed = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict) or source.selector not in parsed:
            raise ValueError(f"{source.path}: no key {source.selector!r}")
        return len(parsed[source.selector])

    if source.method == "regex_count":
        return len(re.findall(source.selector, target.read_text(encoding="utf-8")))

    if source.method == "line_count":
        lines = target.read_text(encoding="utf-8").splitlines()
        return sum(1 for line in lines if line.strip())

    if source.method == "literal":
        body = target.read_text(encoding="utf-8")
        if source.selector not in body:
            raise ValueError(f"{source.path}: does not contain {source.selector!r}")
        return source.selector

    raise ValueError(f"unknown method: {source.method!r}")


def verify(claim: Claim, root: Path | str) -> Verdict:
    """
    Check one claim against the code.

    Parameters
    ----------
    claim : Claim
        The assertion to check.
    root : Path or str
        Directory the claim's source path is relative to.

    Returns
    -------
    Verdict
        ``ok`` is False both when the value differs and when the source could
        not be read at all.
    """
    try:
        actual = read_actual(claim.source, root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        # An unreadable source is a failure, never a skip. A guard that goes
        # quiet when its input moves is the shape of defect this suite keeps
        # finding, so it is refused here explicitly.
        return Verdict(claim, None, False, f"could not verify: {exc}")

    if actual == claim.value:
        return Verdict(claim, actual, True, "matches")

    return Verdict(
        claim,
        actual,
        False,
        f"the film says {claim.value!r} ({claim.text!r}); {claim.source.path} says {actual!r}",
    )


def verify_all(claims: list[Claim], root: Path | str) -> list[Verdict]:
    """Check every claim. Returns one :class:`Verdict` per claim, in order."""
    return [verify(claim, root) for claim in claims]


@dataclass(frozen=True)
class UndeclaredNumber:
    """A number visible in a composition that no claim accounts for."""

    written: str
    context: str


def undeclared_numbers(
    html: str,
    claims: list[Claim],
    *,
    ignore: frozenset[int] = frozenset(),
) -> list[UndeclaredNumber]:
    """
    Find numbers on screen that no claim accounts for.

    This is the half that makes the guard worth having. Checking only declared
    claims protects the numbers someone thought to declare — never the one that
    was typed into a keyframe at midnight and then went stale.

    Parameters
    ----------
    html : str
        The composition markup.
    claims : list[Claim]
        The declared claims. A number is accounted for when it equals a claim's
        value or appears inside a claim's text.
    ignore : frozenset[int]
        Values that are legitimately on screen without being claims about the
        project — a year in a wordmark, a version number. Passed explicitly so
        each exemption is written down somewhere a reviewer sees it.

    Returns
    -------
    list[UndeclaredNumber]
        One entry per unaccounted number, with surrounding text so the frame
        can be found.
    """
    text = visible_text(html)
    declared_values = {claim.value for claim in claims}
    declared_text = " ".join(claim.text for claim in claims)

    found: list[UndeclaredNumber] = []
    for written in numbers_in(text):
        parsed = _as_int(written)
        if parsed is not None and (parsed in declared_values or parsed in ignore):
            continue
        if written in declared_text:
            continue
        # Context, not just the digits: a bare "167" in a failure report does
        # not tell anyone which scene to re-cut.
        at = text.find(written)
        start, end = max(0, at - 40), min(len(text), at + len(written) + 40)
        found.append(UndeclaredNumber(written, text[start:end].strip()))
    return found


@dataclass
class ClaimReport:
    """Both directions of the check, for one film, in one object CI can read."""

    verdicts: list[Verdict] = field(default_factory=list)
    undeclared: list[UndeclaredNumber] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when every claim holds and nothing unaccounted is on screen."""
        return all(v.ok for v in self.verdicts) and not self.undeclared

    def lines(self) -> list[str]:
        """Human-readable findings, worst first. Empty when :attr:`ok`."""
        out = [f"FAIL {v.detail}" for v in self.verdicts if not v.ok]
        out += [f"UNDECLARED {u.written!r} in {u.context!r}" for u in self.undeclared]
        return out


def as_claim(raw: dict[str, Any]) -> Claim:
    """
    Build a :class:`Claim` from its YAML/JSON form.

    Parameters
    ----------
    raw : dict
        Keys ``text``, ``value``, and ``source`` (itself ``path`` / ``method``
        / optional ``selector``).

    Returns
    -------
    Claim

    Raises
    ------
    KeyError
        If a required key is absent — a half-written claim must not load as a
        claim that happens to pass.
    """
    src = raw["source"]
    return Claim(
        text=raw["text"],
        value=raw["value"],
        source=ClaimSource(
            path=src["path"],
            method=src["method"],
            selector=src.get("selector", ""),
        ),
    )
