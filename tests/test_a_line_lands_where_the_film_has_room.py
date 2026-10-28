"""
Laying a script on a timeline: what gives, and the one thing that does not.

The behaviour under test replaced a refusal. The narrator this generalises
checked each line against the start of the next one and, when a line overran,
printed the overrun and left the previous track in place. Correct — and the
reason fourteen cuts out of twenty-two carried a voice older than their script
for days, because the build neither broke nor advanced.

So the cases below are the three states that mattered in practice: a line that
fits, a line that overruns and pushes, and a script that genuinely does not
fit in its film. Only the third is a failure.

Author
------
Warith HARCHAOUI <warithmetics@deraison.ai>
"""

from __future__ import annotations

import pytest

from sprezzature_video import timeline


def test_a_script_that_fits_is_left_exactly_where_it_was_written() -> None:
    """The common case must be the identity, or every film drifts a little."""
    out = timeline.lay_out([1.0, 10.0, 20.0], [3.0, 4.0, 5.0], duration=60.0)
    assert out.starts == [1.0, 10.0, 20.0]
    assert out.fits
    assert out.report() == []


def test_an_overrunning_line_pushes_the_next_one_and_nothing_else() -> None:
    """Local damage, locally absorbed.

    The line after the overrun moves; the one after *that* is back on its own
    mark, because it had room. A layout that shifted the whole tail would
    push a film off its last scene to fix a problem in its second.
    """
    out = timeline.lay_out([1.0, 5.0, 20.0], [6.0, 3.0, 2.0], duration=60.0)
    assert out.starts[0] == 1.0
    assert out.starts[1] == pytest.approx(7.0 + timeline.DEFAULT_GAP_S)
    assert out.starts[2] == 20.0, "a line with room was moved"
    assert out.fits


def test_a_pushed_line_is_reported_rather_than_hidden() -> None:
    """A voice arriving after the picture it describes is worth a word."""
    out = timeline.lay_out(
        [1.0, 5.0], [8.0, 2.0], duration=60.0, texts=["long one", "the next"]
    )
    assert [line.index for line in out.drifted] == [1]
    assert "line 2 starts at" in out.report()[0]
    assert "'the next'" in out.report()[0]


def test_drift_under_the_notice_threshold_is_not_reported() -> None:
    """Below a frame or two nobody can tell, and a report nobody can act on
    is a report that trains its reader to skip the next one."""
    out = timeline.lay_out([1.0, 5.0], [3.9, 2.0], duration=60.0)
    assert 0 < out.lines[1].drift < timeline.DRIFT_NOTE_S
    assert out.report() == []


def test_a_script_too_long_for_its_film_is_the_one_hard_failure() -> None:
    """No layout absorbs this: the words have to go."""
    out = timeline.lay_out([1.0, 30.0], [20.0, 40.0], duration=60.0)
    assert not out.fits
    assert out.overflow == pytest.approx(10.0)
    assert "past the film's 60s" in out.report()[0]


def test_the_overflow_is_quoted_in_characters_of_this_track() -> None:
    """Measured on what was spoken, not on a subtitle convention.

    "about forty characters" is useful; seventeen characters a second is a
    fact about a reader rather than about the engine that just spoke.
    """
    out = timeline.lay_out(
        [0.0], [70.0], duration=60.0, texts=["x" * 700]
    )  # 10 characters a second
    assert "about 100 characters" in out.report()[0], out.report()[0]


def test_mismatched_inputs_are_refused_rather_than_zipped_short() -> None:
    """A silently shortened layout drops the end of a film."""
    with pytest.raises(ValueError, match="every line needs both"):
        timeline.lay_out([1.0, 5.0], [3.0], duration=60.0)
    with pytest.raises(ValueError, match="text"):
        timeline.lay_out([1.0], [3.0], duration=60.0, texts=["a", "b"])


def test_a_script_out_of_film_order_is_refused() -> None:
    """Sorting it here would hide a caller that built its grid backwards."""
    with pytest.raises(ValueError, match="run backwards"):
        timeline.lay_out([10.0, 2.0], [1.0, 1.0], duration=60.0)


def test_an_empty_script_has_no_end_and_does_not_divide_by_zero() -> None:
    """The degenerate case a film reaches the day its narration is deleted."""
    out = timeline.lay_out([], [], duration=60.0)
    assert out.end == 0.0
    assert out.fits
    assert out.report() == []
