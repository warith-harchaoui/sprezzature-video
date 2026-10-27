"""
The pitch order and the writing charter, checked on their own failures.

Both modules were written after watching this suite's own first set of films
back and finding them unwatchable for two separate reasons. The cases below
are those films, not invented examples: a test built from a hypothetical
failure proves the regular expression compiles and nothing else.

Author
------
Warith HARCHAOUI <warithmetics@deraison.ai>
"""

from __future__ import annotations

import pytest

from sprezzature_video import charter, pitch

# --- the charter ----------------------------------------------------------

@pytest.mark.parametrize("text, rule", [
    # Every one of these shipped in a rendered film.
    ("WCAG 1.4.2 — it talks over the reader", "em or en dash"),
    ("Each one names the element, the line, and the rule it broke.",
     "comma followed by and/et"),
    ("Nobody says “that violates Hick’s Law”.", "opens on a negation"),
    ("No charting library underneath", "opens on a negation"),
    ("None of this was invented here", "opens on a negation"),
])
def test_the_charter_catches_what_shipped(text: str, rule: str) -> None:
    """Each line below was on screen before anybody measured."""
    rules = [f.rule for f in charter.check_line(text, "en")]
    assert rule in rules, f"{text!r} should trip {rule!r}, got {rules}"


def test_a_negation_inside_a_sentence_is_left_alone() -> None:
    """The fault is the first word a reader meets, not the word anywhere.

    Without this the check would be useless: half of good prose says what a
    thing is and then what it is not.
    """
    fine = "Lightness is the one channel nothing takes away."
    assert not charter.check_line(fine, "en")


def test_quotation_marks_do_not_hide_the_opening_word() -> None:
    """A line that opens on a quoted negation opens on a negation."""
    rules = [f.rule for f in charter.check_line('"Nobody reads this page."', "en")]
    assert "opens on a negation" in rules


def test_the_french_list_is_not_the_english_one_translated() -> None:
    """Each charter bans what its own language actually does.

    `mordre` is banned in French and has no English counterpart on the
    English list; `truly` is banned in English and means nothing to the
    French one. A single shared list would have missed both.
    """
    assert any(charter.check_line("une règle qui mord vraiment", "fr"))
    assert not charter.check_line("a rule that applies", "en")
    assert any(charter.check_line("this is truly the cornerstone", "en"))


def test_modals_are_counted_and_never_failed_on() -> None:
    """Both charters say a raw modal count confuses the senses.

    "A third party can demand this control" states enforceability and keeps
    its modal. So the number is reported and the caller decides.
    """
    result = charter.measure(
        [("x", "A third party can demand this control.")], "en"
    )
    assert result["modals"] == 1
    assert result["findings"] == []


def test_an_unknown_language_is_refused_rather_than_guessed() -> None:
    with pytest.raises(ValueError, match="no charter for"):
        charter.check_line("algo", "es")


# --- the pitch ------------------------------------------------------------

def _beat(name: str, text: str, start: float) -> pitch.Beat:
    return pitch.Beat(name=name, scenes=(0,), text=text, start=start)


def test_a_film_with_no_problem_beat_is_reported() -> None:
    """The first figures film opened on a specification.

    "167 chart kinds, every one hand-authored" delivered to somebody with no
    reason to want one.
    """
    report = pitch.check("figures", {
        "solution": _beat("solution", "Each generator writes the SVG itself.", 6.0),
        "magic": _beat("magic", "The vector is the deliverable, never an export.", 30.0),
    }, duration=60.0)
    assert not report.ok
    assert "no problem beat" in report.findings[0]


def test_a_feature_list_is_not_a_secret_sauce() -> None:
    """The suite film ended on three facts and no insight.

    Kawasaki's own warning: the underlying magic is the one non-obvious thing
    that makes the solution possible. A viewer cannot repeat an inventory to
    a colleague, which is the test.
    """
    report = pitch.check("sprezzature", {
        "problem": _beat("problem", "Most design decisions are already made.", 0.0),
        "solution": _beat("solution", "Here they are as code.", 20.0),
        "magic": _beat("magic", "Ten packages. Five surfaces each.", 45.0),
    }, duration=60.0)
    assert not report.ok
    assert any("feature list" in f for f in report.findings)


def test_the_insight_that_passes() -> None:
    """The sentence the colors package had and never said out loud."""
    report = pitch.check("colors", {
        "problem": _beat("problem", "Light grey on white reads fine. To you.", 0.0),
        "solution": _beat("solution", "It renders the chart as that eye sees it.", 18.0),
        "magic": _beat(
            "magic",
            "Hue goes. Saturation goes. Lightness holds, so every tool "
            "works on lightness.",
            40.0,
        ),
    }, duration=60.0)
    assert report.ok, report.findings


def test_a_problem_that_arrives_late_is_measured_not_judged() -> None:
    """Until the problem lands, the viewer watches a solution to nothing."""
    report = pitch.check("late", {
        "problem": _beat("problem", "Here is what goes wrong.", 30.0),
        "solution": _beat("solution", "And here is the fix.", 40.0),
        "magic": _beat("magic", "The mechanism nobody else has, explained.", 50.0),
    }, duration=60.0)
    assert not report.ok
    assert "13.2s" in report.findings[0], report.findings


def test_beats_out_of_order_are_caught() -> None:
    """A mechanism explained before its problem reads as showing off."""
    report = pitch.check("backwards", {
        "magic": _beat("magic", "The mechanism nobody else has, explained here.", 2.0),
        "problem": _beat("problem", "Here is what goes wrong for you.", 20.0),
        "solution": _beat("solution", "And here is the fix for it.", 40.0),
    }, duration=60.0)
    assert not report.ok
    assert any("out of order" in f for f in report.findings)
