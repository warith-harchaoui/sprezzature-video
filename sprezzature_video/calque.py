#!/usr/bin/env python3
"""
Whether a film's second language was written, or only translated.

The defect
----------
A film shot in two languages is two films. The suite's own set had eleven of
them, and for a month the French cut of each one was the English cut rendered
line by line: same number of lines, same sentence boundaries, same clause
order, French words carrying English syntax. On screen that had already been
noticed and fixed — the two languages are composed on adjacent lines, so each
is written with the rest of its own script in view — and the *voice* was the
half nobody had looked at.

It is a quiet defect. Every line is grammatical, every fact is right, and the
only symptom is that the French sounds like a translation, which it is. A
native viewer hears it in the first ten seconds and no reviewer reading a diff
ever will, because a diff of two languages shows two columns of unrelated
words.

What can be measured without reading either language
-----------------------------------------------------
Not meaning. This module cannot tell whether a French line says what an
English one says, and does not try.

What it can see is **correspondence**. A translation preserves the shape of
what it translates: if line 4 of the English is two sentences holding the
numbers 167 and 20, line 4 of the French is two sentences holding 167 and 20.
Two scripts composed independently do not do that. They distribute the same
material differently — one splits a clause the other runs on, one carries a
number a line earlier — because the sentence that lands well is not in the
same place in the two languages.

So the measure is the fraction of positions where the two cuts have the same
*shape*: the same count of sentences and the same numerals in the same order.
A differing number of lines counts against the score by sitting in the
denominator, which is right — a cut with three more lines than its sibling is
evidence on its own.

Calibrated, not guessed
-----------------------
:data:`CALQUE_SCORE` is 0.75 because both sides were measured. The suite's
eleven known-translated cuts scored 0.75 to 0.89. The eleven rewritten ones
scored 0.36 to 0.70 — after two of them, flagged at 0.91 and 0.80 by this
module on its first run, turned out to be genuinely still translated and were
rewritten. That is the whole value of the thing: it caught its own author.

What it is not
--------------
A proof. Two scripts can correspond closely and be well written in both
languages — a film whose lines are each one sentence with no numbers will
score high and may be perfectly composed. So this reports a *suspicion*, names
the positions that correspond, and leaves the judgement where it belongs. It
is a reason to read the two cuts side by side, not a verdict on them.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

#: At or above this, two cuts correspond closely enough to be worth reading
#: side by side. See the module docstring for where the number comes from: the
#: suite's known-translated cuts measured 0.75 to 0.89, its written ones 0.36
#: to 0.70, and the gap between them is where this sits.
CALQUE_SCORE = 0.75

#: End of a sentence: the mark plus whatever follows it, so an abbreviation
#: mid-clause does not split a line in two. Both languages set these the same
#: way; the French space before a colon or a semicolon is not a sentence end
#: in either.
_SENTENCE_END = re.compile(r"[.!?…]+(?:\s|$)")

#: A run of digits. Spelled-out numbers are deliberately not matched: "167"
#: survives translation unchanged and "sixty-four" does not, so counting the
#: written ones would score a faithful translation of a number word as a
#: divergence.
_NUMERAL = re.compile(r"\d+")


def shape(line: str) -> tuple[int, tuple[str, ...]]:
    """
    The part of a line that survives translation.

    Parameters
    ----------
    line : str
        One narration line, in any language.

    Returns
    -------
    tuple
        How many sentences it holds, and its numerals in the order they
        appear. Two lines with the same shape are two lines a translator could
        have produced from each other.

    Examples
    --------
    >>> shape("167 kinds, all hand-written. Twenty rules.")
    (2, ('167',))
    >>> shape("167 types, écrits à la main. Vingt règles.")
    (2, ('167',))
    """
    return (len(_SENTENCE_END.findall(line)), tuple(_NUMERAL.findall(line)))


@dataclass
class CalqueReport:
    """
    How closely two language cuts of one film correspond.

    Parameters
    ----------
    film : str
        The film's key, for a message a reader can act on.
    languages : tuple[str, str]
        Which two cuts were compared, in the order they were given.
    counts : tuple[int, int]
        How many lines each cut has.
    corresponding : list[int]
        Positions, from zero, where the two cuts have the same shape.
    score : float
        Corresponding positions over the longer of the two line counts.
    """

    film: str
    languages: tuple[str, str]
    counts: tuple[int, int]
    corresponding: list[int] = field(default_factory=list)
    score: float = 0.0

    @property
    def suspected(self) -> bool:
        """Whether the two cuts correspond closely enough to be worth reading."""
        return self.score >= CALQUE_SCORE

    def report(self) -> list[str]:
        """
        What to tell a reader, empty when the two cuts diverge.

        Returns
        -------
        list of str
            One line stating the score and what it means, then the positions
            that correspond — because "rewrite the French" is not actionable
            and "lines 2, 3, 5 and 7 line up with their English" is.
        """
        if not self.suspected:
            return []
        first, second = self.languages
        places = ", ".join(str(i + 1) for i in self.corresponding)
        return [
            f"{self.film}: the {second} cut reads as a rendering of the "
            f"{first} one (score {self.score:.2f}, at or above "
            f"{CALQUE_SCORE:.2f}). {len(self.corresponding)} of "
            f"{max(self.counts)} positions have the same sentence count and "
            f"the same numerals in the same order: line(s) {places}. Two cuts "
            f"written separately distribute their material differently; these "
            f"do not. Read them side by side before shipping both."
        ]


def compare_cuts(
    first: list[str],
    second: list[str],
    *,
    film: str = "film",
    languages: tuple[str, str] = ("en", "fr"),
) -> CalqueReport:
    """
    Measure how far one language cut corresponds to another, position by position.

    Parameters
    ----------
    first, second : list of str
        The narration lines of each cut, in film order.
    film : str, optional
        The film's key, used in the report.
    languages : tuple of str, optional
        The two language codes, in the same order as *first* and *second*.

    Returns
    -------
    CalqueReport
        The score, the corresponding positions, and whether it is worth a look.

    Raises
    ------
    ValueError
        If either cut is empty. A film with nothing said in one of its
        languages is a different problem, and scoring it zero would report
        "well written" about a cut that does not exist.

    Examples
    --------
    A translated cut corresponds at every position:

    >>> en = ["Two sentences. With 20 in one.", "And a third."]
    >>> fr = ["Deux phrases. Avec 20 dans une.", "Et une troisième."]
    >>> compare_cuts(en, fr).suspected
    True

    A written one redistributes, and does not:

    >>> fr = ["Deux phrases, dont une porte 20.", "Puis une troisième.", "Fin."]
    >>> round(compare_cuts(en, fr).score, 2)
    0.33
    """
    if not first or not second:
        raise ValueError(
            f"{film}: {languages[0] if not first else languages[1]} has no "
            f"narration, so there is nothing to compare"
        )

    overlap = min(len(first), len(second))
    longest = max(len(first), len(second))
    corresponding = [
        index for index in range(overlap) if shape(first[index]) == shape(second[index])
    ]
    return CalqueReport(
        film=film,
        languages=languages,
        counts=(len(first), len(second)),
        corresponding=corresponding,
        score=len(corresponding) / longest,
    )


def compare_spec(spec: Any, *, languages: tuple[str, str] = ("en", "fr")) -> CalqueReport:
    """
    Run :func:`compare_cuts` over a loaded film spec's narration.

    Parameters
    ----------
    spec : FilmSpec
        A spec carrying ``narration`` for both languages.
    languages : tuple of str, optional
        Which two cuts to compare.

    Returns
    -------
    CalqueReport

    Raises
    ------
    KeyError
        If the spec does not carry both languages. Not swallowed: a spec that
        declares one language and is asked about two has a gap, and reporting
        "no calque" about a cut that was never read is the failure this
        package exists to refuse.
    """
    first, second = languages
    for lang in languages:
        if lang not in spec.narration:
            raise KeyError(
                f"{spec.name}: no {lang} narration in the spec, so the {first}/"
                f"{second} comparison would be about nothing"
            )
    return compare_cuts(
        [line.text for line in spec.narration[first]],
        [line.text for line in spec.narration[second]],
        film=spec.name,
        languages=languages,
    )
