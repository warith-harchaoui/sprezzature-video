#!/usr/bin/env python3
"""
A film as a reviewable text file.

The claims a film makes, the assets it renders from and the lines it speaks all
have to live somewhere a person can read and a reviewer can diff. A Python
literal buried in a generator is none of those things: the four films this
package generalises kept their claims inside a 707-line script, which is
exactly why "127" survived a catalogue growing to 167 — nobody opens a
generator to re-read its strings.

So a spec is YAML, like `assets/*.yaml` everywhere else in the suite, and it
holds the three things that go stale:

``claims``
    what the film asserts, and where each assertion is checked.
``assets``
    what it renders from, classified by whether it can be got again.
``narration``
    what it says, per language, with the audio that says it.

Nothing here describes *motion*. Timing, layout and animation belong to the
renderer behind the seam; this file is the part that has to stay true.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sprezzature_video.assets import Asset, AssetLedger, Provenance
from sprezzature_video.captions import Spoken
from sprezzature_video.claims import Claim, as_claim


@dataclass
class FilmSpec:
    """
    One film's checkable content, loaded from YAML.

    Parameters
    ----------
    name : str
        The film's identifier, used for output filenames.
    claims : list[Claim]
        What the film asserts, each with the place that decides its truth.
    ledger : AssetLedger
        What the film renders from.
    narration : dict[str, list[Spoken]]
        Language code to narration lines.
    """

    name: str
    claims: list[Claim] = field(default_factory=list)
    ledger: AssetLedger = field(default_factory=AssetLedger)
    narration: dict[str, list[Spoken]] = field(default_factory=dict)


def _asset_from(raw: dict[str, Any]) -> Asset:
    """
    Build an :class:`Asset` from its YAML form.

    Raises
    ------
    KeyError
        If ``rel`` or ``provenance`` is absent.
    ValueError
        If ``provenance`` is not one of the three classes, or if a ``sole``
        entry carries no reason. The reason is required because "missing" on
        its own tells nobody what to do, and a ``sole`` asset is the one class
        where nobody can work it out later.
    """
    try:
        provenance = Provenance(raw["provenance"])
    except ValueError as exc:
        kinds = ", ".join(p.value for p in Provenance)
        raise ValueError(
            f"unknown provenance {raw['provenance']!r}; expected one of {kinds}"
        ) from exc

    why = raw.get("why", "")
    if provenance is Provenance.SOLE and not why:
        raise ValueError(f"{raw['rel']}: a 'sole' asset must say why it exists nowhere else")

    return Asset(
        rel=raw["rel"],
        provenance=provenance,
        source=raw.get("source", ""),
        recipe=raw.get("recipe", ""),
        why=why,
    )


def _spoken_from(raw: dict[str, Any], *, base: Path) -> Spoken:
    """
    Build a :class:`Spoken` line from its YAML form.

    ``audio`` is resolved against *base* so a spec can name its narration files
    relative to itself rather than to whatever directory the command ran in.
    """
    audio = raw.get("audio")
    return Spoken(
        start=float(raw["start"]),
        text=raw["text"],
        audio=(base / audio) if audio else None,
        duration=float(raw["duration"]) if raw.get("duration") is not None else None,
    )


def load(path: Path | str) -> FilmSpec:
    """
    Read a film spec from YAML.

    Parameters
    ----------
    path : Path or str
        The ``.yaml`` file.

    Returns
    -------
    FilmSpec

    Raises
    ------
    FileNotFoundError
        If the spec is absent.
    ValueError
        If the document is not a mapping, or a section is malformed. A spec
        that half-loads is worse than one that refuses: the half that vanished
        is the half nothing then checks.

    Examples
    --------
    >>> # claims:
    >>> #   - text: "167 kinds, every one hand-authored."
    >>> #     value: 167
    >>> #     source: {path: "catalog/figures.json", method: json_len}
    """
    import yaml

    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"film spec not found: {target}")

    doc = yaml.safe_load(target.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"{target}: a film spec must be a mapping, got {type(doc).__name__}")

    base = target.parent
    claims = [as_claim(c) for c in doc.get("claims") or []]
    ledger = AssetLedger([_asset_from(a) for a in doc.get("assets") or []])

    narration: dict[str, list[Spoken]] = {}
    for lang, lines in (doc.get("narration") or {}).items():
        narration[lang] = [_spoken_from(line, base=base) for line in lines]

    return FilmSpec(
        name=doc.get("name") or target.stem,
        claims=claims,
        ledger=ledger,
        narration=narration,
    )
