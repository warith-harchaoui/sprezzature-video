#!/usr/bin/env python3
"""
The mechanical half of the writing charters, in English and in French.

Two documents govern anything that carries the author's name: a chapter, a
page, a figure caption, a commit message, and a line of film. Both open on
the same instruction, which is why this module exists before any rewriting
does: **measure first.** With no count you correct at random.

What belongs here, and what never will
--------------------------------------
Only the part a regular expression settles. Each rule below is either a
character that is banned outright or a word on a list. Everything else in
those documents is judgement and stays judgement: whether a sentence earns
its place, whether the argument is written rather than hinted at, whether a
bright sixteen-year-old follows it on the first pass.

A checker that pretended to answer those would be worse than none, because a
green tick would stand in for a reading.

The rules
---------
**Em and en dashes.** Banned outright, in both languages. A colon, a
semicolon, a parenthesis or a full stop says the same thing and commits to
which of them it meant.

**Comma followed by "and" / "et".** Tic number one in both documents.

**Opening on a negation.** "Nobody says", "No browser", "None of this".
Both charters ask for what a thing is, with the negation following if it
still earns its place. Checked on the first word only: the same word in the
middle of a sentence is ordinary and stays.

**The reflex antithesis.** "It is not X, it is Y" and its cousins. Once in a
text is a figure; three times is a mould. Counted, never failed on.

**The named tics.** Flat lists from section 6b of each document: verbs of
abstract location, verbs of biting, conference vocabulary, hollow openings.

**Modal density.** Reported, never failed on. Both documents are explicit
that a raw count confuses senses, and that power and permission keep their
modal: "a third party *can* demand this" states enforceability.

Why this lives in a package about video
---------------------------------------
This package exists to check what a film says against the thing it describes.
How it says it is the same job. A film that states a true fact in prose a
machine could have written has still failed the viewer.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import re
from dataclasses import dataclass

DASHES = re.compile(r"[—–]")

COMMA_AND = re.compile(r",\s+(and|et)\b", re.I)

OPENS_NEGATIVE = re.compile(
    r"^(no|not|nobody|none|nothing|never|neither|without"
    r"|aucun|aucune|personne|rien|jamais|ni|pas|sans)\b",
    re.I,
)

ANTITHESIS = re.compile(
    r"\b(is not\s+\w+[,.]\s*it is\b"
    r"|not so much\b|less about\b.{0,40}\bthan about\b"
    r"|n'est pas\s+\w+[,.]\s*c'est\b"
    r"|non pas\b.{0,40}\bmais\b"
    r"|il ne s'agit pas tant\b)",
    re.I,
)

#: French verbs are listed as stems, not infinitives. The charter writes
#: "mordre"; a film writes "une règle qui mord". Matching the infinitive
#: catches the dictionary entry and misses every sentence anybody would
#: actually write, which is the failure a word list exists to avoid.
#: The stems below were each checked against a false friend: "mord" does not
#: appear inside a common French word, where "log" would have matched
#: "logiciel" and "logique", so the location verbs keep their phrase form.
BANNED = {
    "en": (
        "at the heart of", "at the intersection of", "at the crossroads of",
        "on the cusp of", "beneath the surface", "writ large", "in the age of",
        "lies in", "resides in", "rooted in",
        "permeate", "suffuse", "crystallize", "coalesce around",
        "interrogate", "problematize", "mobilize", "foreground", "unpack",
        "leverage", "speak to", "impact",
        "paradigm", "ecosystem", "cornerstone", "keystone", "holistic",
        "synergy", "disruptive", "nuanced", "profound", "truly", "deeply",
        "it is important to note", "it is worth noting", "in a world where",
        "now more than ever", "at its core", "in the final analysis",
        "at the end of the day", "key takeaway",
        "pave the way", "shed new light", "bridge the gap", "gesture",
    ),
    "fr": (
        "au cœur de", "à la croisée de", "au croisement de", "à l'orée de",
        "en filigrane", "en creux", "par-delà", "en toile de fond",
        "à géométrie variable", "en demi-teinte",
        "réside dans", "résident dans", "loge dans", "logent dans",
        "se niche", "se nichent",
        "mord",
        "irrigu", "infus", "innerv", "cristallis", "sédiment", "essaim",
        "convoqu", "interrog", "questionn", "mobilis", "articul",
        "impact",
        "paradigme", "écosystème", "prisme", "clé de voûte",
        "pierre angulaire", "approche holistique", "synergie", "disruptif",
        "à l'ère de", "véritable", "fondamentalement", "profondément",
        "il est important de noter", "force est de constater",
        "dans un monde où", "à l'heure où", "plus que jamais",
        "en définitive", "in fine", "en dernière analyse",
        "faire écho", "résonner avec", "ouvrir la voie", "geste",
    ),
}

MODALS = {
    "en": re.compile(r"\b(can|could|may|might|must|should|possible)\b", re.I),
    "fr": re.compile(
        r"\b(peut|peuvent|pouvoir|possible|doit|doivent|devoir|devrait)\b", re.I
    ),
}


@dataclass(frozen=True)
class Finding:
    """One mechanical breach, with enough to act on it."""

    rule: str
    text: str
    where: str = ""

    def __str__(self) -> str:
        at = f"{self.where}: " if self.where else ""
        return f"{at}{self.rule}\n    {self.text}"


def check_line(text: str, lang: str = "en", where: str = "") -> list[Finding]:
    """Hard findings for one line. Soft counts come from :func:`measure`."""
    if lang not in BANNED:
        raise ValueError(f"no charter for {lang!r}; expected 'en' or 'fr'")
    out: list[Finding] = []
    if DASHES.search(text):
        out.append(Finding("em or en dash", text, where))
    if COMMA_AND.search(text):
        out.append(Finding("comma followed by and/et", text, where))
    # Quotation marks and brackets are stripped: the fault is the first word
    # a reader meets, not the first character in the file.
    if OPENS_NEGATIVE.match(text.strip().lstrip("«\"'“‘([ ")):
        out.append(Finding("opens on a negation", text, where))
    for word in BANNED[lang]:
        if re.search(rf"\b{re.escape(word)}", text, re.I):
            out.append(Finding(f"banned: {word!r}", text, where))
    return out


def measure(lines: list[tuple[str, str]], lang: str = "en") -> dict:
    """Count a whole text at once, which is what both charters ask for first.

    Parameters
    ----------
    lines : list of (where, text)
        Every user-visible string, each with a label naming where it sits.
    lang : str
        ``"en"`` or ``"fr"``.

    Returns
    -------
    dict
        ``findings`` is the hard list. ``antithesis`` and ``modals`` are
        counts: locations worth reading, never verdicts. The charters are
        explicit that a raw modal count confuses the senses, so this reports
        the number and refuses to judge it.
    """
    findings: list[Finding] = []
    antithesis = 0
    modals = 0
    for where, text in lines:
        findings.extend(check_line(text, lang, where))
        if ANTITHESIS.search(text):
            antithesis += 1
        modals += len(MODALS[lang].findall(text))
    return {
        "findings": findings,
        "antithesis": antithesis,
        "modals": modals,
        "lines": len(lines),
    }
