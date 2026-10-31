"""
The calque measure, checked on the two sets it was calibrated against.

Where the cases come from
-------------------------
Not invented. The suite that this package generalises shipped eleven films in
two languages, and the French of all eleven was the English rendered line by
line. Those scripts measured 0.75 to 0.89. They were then rewritten, and the
rewrites measured 0.36 to 0.70 — but only after this module, run for the first
time, flagged two of the supposedly-rewritten cuts at 0.91 and 0.80 and turned
out to be right about both.

So the cases below are the two ends of that measurement, reduced to the
smallest pair of scripts that reproduces each. A threshold tested only against
the side it was tuned on is a threshold that cannot fail.

Author
------
Warith HARCHAOUI <warithmetics@deraison.ai>
"""

from __future__ import annotations

import pytest

from sprezzature_video import calque
from sprezzature_video.captions import Spoken
from sprezzature_video.spec import FilmSpec

#: An English script, and the French it produced when somebody translated it
#: a line at a time. Every position holds the same number of sentences and the
#: same numerals, which is what makes it a translation and not a script.
ENGLISH = [
    "Sprezzature is an AI engine for Design. Colors makes sure yours can be read.",
    "Light grey on white reads perfectly well, at your desk, indoors.",
    "About one man in twelve does not separate red from green.",
    "The matrices come from a 2009 paper, measured on real observers.",
]
TRANSLATED = [
    "Sprezzature est un moteur d'IA pour le design. Colors vérifie que les vôtres se lisent.",
    "Du gris clair sur du blanc se lit très bien, chez vous, à l'intérieur.",
    "Environ un homme sur douze ne sépare pas le rouge du vert.",
    "Les matrices viennent d'un article de 2009, mesurées sur de vrais observateurs.",
]

#: The same material, composed in French instead: the setup and its turn are
#: two sentences rather than one, the paper arrives in the same breath as what
#: it proves, and the script runs to a different number of lines.
WRITTEN = [
    "Sprezzature est un moteur d'IA pour le design. Colors vérifie que vos couleurs se lisent.",
    "Du gris clair sur du blanc, ça se lit très bien.",
    "Chez vous, à l'intérieur.",
    "Et un homme sur douze ne distingue pas le rouge du vert : vos deux barres n'en font plus qu'une.",
    "Les matrices sortent d'un article de 2009, mesurées sur de vrais observateurs.",
]


def test_a_translated_cut_is_flagged() -> None:
    """The side the measure exists for."""
    report = calque.compare_cuts(ENGLISH, TRANSLATED, film="colors")
    assert report.suspected, (
        f"a line-for-line translation scored {report.score:.2f}, under the "
        f"{calque.CALQUE_SCORE} threshold. The measure has gone blind to the "
        f"thing it is for."
    )


def test_a_written_cut_is_not_flagged() -> None:
    """The side that matters more, because a false positive costs a rewrite.

    This is the check that was missing the first time a measure went into this
    suite: four separate measures in one day were calibrated on the failing
    case alone and reported the known-good case as broken.
    """
    report = calque.compare_cuts(ENGLISH, WRITTEN, film="colors")
    assert not report.suspected, (
        f"an independently written French cut scored {report.score:.2f}, at or "
        f"over the {calque.CALQUE_SCORE} threshold. A measure that cannot pass "
        f"good work will be switched off."
    )


def test_the_report_names_the_lines_that_correspond() -> None:
    """ "Rewrite the French" is not actionable; a list of positions is."""
    lines = calque.compare_cuts(ENGLISH, TRANSLATED, film="colors").report()
    assert lines, "a flagged pair reported nothing"
    assert "line(s) 1, 2, 3, 4" in lines[0], lines[0]
    assert "colors" in lines[0]


def test_a_clean_pair_reports_nothing() -> None:
    """Silence, not a reassurance nobody asked for."""
    assert calque.compare_cuts(ENGLISH, WRITTEN).report() == []


def test_a_differing_line_count_counts_against_the_score() -> None:
    """A cut with lines its sibling does not have is evidence on its own.

    Scored over the longer of the two, so adding a line cannot raise the
    score by shrinking the denominator.
    """
    short = calque.compare_cuts(ENGLISH, TRANSLATED).score
    longer = calque.compare_cuts(ENGLISH, [*TRANSLATED, "Une ligne de plus."]).score
    assert longer < short, f"{longer} should be under {short}"


def test_an_empty_cut_is_refused_rather_than_scored() -> None:
    """Zero would read as "beautifully written" about a cut that is not there."""
    with pytest.raises(ValueError, match="no narration"):
        calque.compare_cuts(ENGLISH, [], film="colors")


def test_a_spec_missing_a_language_is_refused() -> None:
    """A spec declaring one language, asked about two, has a gap."""
    spec = FilmSpec(
        name="colors",
        narration={"en": [Spoken(start=1.1, text=ENGLISH[0], duration=3.0)]},
    )
    with pytest.raises(KeyError, match="no fr narration"):
        calque.compare_spec(spec)


def test_a_spec_on_disk_reaches_the_measure() -> None:
    """The whole path, from a loaded spec to a verdict."""
    spec = FilmSpec(
        name="colors",
        narration={
            "en": [Spoken(start=float(i), text=t, duration=3.0) for i, t in enumerate(ENGLISH)],
            "fr": [Spoken(start=float(i), text=t, duration=3.0) for i, t in enumerate(TRANSLATED)],
        },
    )
    assert calque.compare_spec(spec).suspected
