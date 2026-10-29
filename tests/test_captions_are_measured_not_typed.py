"""
Caption timing comes from the audio, and caption text never splits into a
fragment.

The script this generalises hard-coded its durations, with a comment warning
that regenerating a voice line would desync the subtitles. It did: correcting
two stale sentences moved them by 43 and 64 milliseconds. These tests pin the
behaviour that makes that impossible -- a duration is read, or the call fails.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sprezzature_video import Spoken, measure, split_line, split_to_fit, to_cues
from sprezzature_video.captions import LINE_LIMIT


def test_a_missing_narration_file_raises(tmp_path: Path) -> None:
    """
    Silence must not become a zero-length cue.

    A cue of zero length is never painted, so the caption simply never appears
    -- a failure a viewer sees and no test would.
    """
    with pytest.raises(FileNotFoundError):
        measure(tmp_path / "absent.wav")


def test_a_line_without_audio_or_duration_is_refused() -> None:
    """Neither measured nor declared means the timing is unknown. Say so."""
    with pytest.raises(ValueError, match="no audio and no duration"):
        to_cues([Spoken(start=0.0, text="A line with no timing at all.")])


def test_a_declared_duration_is_honoured() -> None:
    """A translated track rides the original language's timing, with no audio."""
    [(start, end, text)] = to_cues([Spoken(0.9, "Une phrase.", duration=3.0)])
    assert (start, end) == (0.9, 3.9)
    assert text == "Une phrase."


def test_a_long_line_splits_after_punctuation() -> None:
    """Punctuation stays on the left, so neither half reads as a fragment."""
    head, tail = split_line("A command line is a wall. This builds the door.")
    assert head == "A command line is a wall."
    assert tail == "This builds the door."


def test_a_long_line_splits_before_a_connector() -> None:
    """A connector word moves right: "... and" alone is not a caption."""
    head, tail = split_line("The simulator renders those eyes and the loop looks through them.")
    assert not head.endswith("and")
    assert tail.startswith("and")


def test_a_split_divides_time_in_proportion() -> None:
    """
    The second half must not still be on screen after the voice moved on, so
    the pivot follows the halves' lengths rather than splitting evenly.

    The line has to exceed LINE_LIMIT or nothing splits -- the first version of
    this test used a 46-character line and unpacked two cues from one.
    """
    text = "The simulator renders those eyes, and the loop looks through them."
    assert len(text) > LINE_LIMIT
    (a_start, a_end, a_text), (b_start, b_end, b_text) = to_cues([Spoken(0.0, text, duration=10.0)])

    assert a_start == 0.0 and b_end == 10.0
    # No gap and no overlap: a caption is on screen for the whole line.
    assert a_end == b_start
    # Computed from the halves' lengths, not hard-coded to dur/2.
    expected = 10.0 * len(a_text) / (len(a_text) + len(b_text))
    assert a_end == pytest.approx(expected)
    assert a_text and b_text


def test_a_short_line_is_left_whole() -> None:
    """Splitting what already fits would make two captions where one reads."""
    assert len(to_cues([Spoken(0.0, "Nine skills, one loop.", duration=2.0)])) == 1


def test_a_french_colon_is_a_break_point() -> None:
    """
    French sets a space before the colon, and uses it where English would use
    a dash or a full stop.

    Without a rule for it the splitter fell through to the middle word, and a
    caption in the suite's own film read "ce qu'aucune référence / ne peut :"
    — a break inside the clause, with the colon orphaned at the end of a line.
    """
    head, tail = split_line(
        "Puis un modèle fait ce qu'aucune référence ne peut : il regarde ce que vous avez fait."
    )
    assert head.endswith(":")
    assert tail.startswith("il regarde")


def test_an_english_colon_is_a_break_point_too() -> None:
    """The unspaced form, which is how English writes it."""
    head, tail = split_line(
        "The rule is the same in both directions: make the thing, then audit it."
    )
    assert head.endswith(":")
    assert tail.startswith("make the thing")


def test_the_budget_is_the_one_the_suite_audits() -> None:
    """
    42, because that is the number the rest of the suite already uses.

    ``sprezzature-audio``'s ``audit_captions`` takes its thresholds from the
    Netflix Timed Text Style Guide and names the source above them, and the
    suite's ``audio`` film puts "Forty-two to a line" on screen as a declared
    claim. This module used 58 until 2026-10-29, inherited from the script it
    generalises, where it had no source: every caption it wrote between 43 and
    58 characters satisfied its own rule and failed the audit that judges it.

    Pinned as a literal rather than imported from the sibling, because the
    sibling is not installed in this package's CI and a guard that skips reads
    exactly like a guard that passed.
    """
    assert LINE_LIMIT == 42


def test_a_caption_is_broken_up_until_it_fits() -> None:
    """
    One cut is not a budget.

    ``split_line`` cuts once, so a long line halved into two pieces that were
    both still over the limit, and the limit read as satisfied because the
    function that applied it had returned. On the eleven films' narration that
    left 41 % of the cues over budget and the longest at 117 characters.
    """
    text = (
        "A film asserts things at thirty frames a second and burns them into pixels, "
        "where nothing ever reads them again, and prose in a README gets re-read "
        "while a number in a keyframe does not."
    )
    assert len(text) > 3 * LINE_LIMIT

    pieces = split_to_fit(text)
    assert len(pieces) > 2, "a single cut cannot hold a line this long to the budget"
    assert all(len(piece) <= LINE_LIMIT for piece in pieces)
    # Nothing added and nothing dropped: the words are the script's.
    assert " ".join(pieces).split() == text.split()


def test_a_line_with_no_break_is_emitted_whole_rather_than_looped_on() -> None:
    """
    A piece that cannot be cut goes out over budget, and says so by being long.

    The alternative is a recursion with no floor, or a truncation nobody asked
    for. The audit in ``sprezzature-audio`` names an over-wide line; silence
    and a hang both name nothing.
    """
    unbreakable = "x" * (LINE_LIMIT * 3)
    assert split_to_fit(unbreakable) == [unbreakable]


def test_every_piece_of_a_split_line_gets_time_and_the_last_one_ends_on_the_line() -> None:
    """
    The cues tile the line: no gap, no overlap, and the last ends exactly on it.

    Accumulating per-piece shares leaves a float residue at the end, and a cue
    that stops a millisecond early is a caption that flickers.
    """
    text = (
        "Twenty accessibility rules, each decidable by reading the HTML text, "
        "so no browser opens and no page renders and nothing runs."
    )
    cues = to_cues([Spoken(0.0, text, duration=12.0)])
    assert len(cues) > 2

    assert cues[0][0] == 0.0
    assert cues[-1][1] == pytest.approx(12.0)
    for (_, end), (start, _) in zip(
        [(a, b) for a, b, _ in cues[:-1]], [(a, b) for a, b, _ in cues[1:]], strict=True
    ):
        assert end == pytest.approx(start)
    # Each piece holds the screen in proportion to how much of it there is.
    total = sum(len(text_) for _, _, text_ in cues)
    for start, end, piece in cues[:-1]:
        assert end - start == pytest.approx(12.0 * len(piece) / total)
