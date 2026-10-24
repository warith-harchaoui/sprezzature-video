"""
A film's on-screen assertions, checked against the code they describe.

These tests exist because of a specific, shipped defect: the five films on
sprezzature.ai say "127 chart kinds" while the catalogue holds 167, and has
since September. The number is burned into ten compositions and five MP4s. No
test, linter or review step looked at it, because a film is the only artefact
in the suite that makes claims about the code from outside the code.

The first test is that exact case, kept as a regression. The rest are the ways
a guard like this goes quiet instead of failing -- which, in this repository,
is the failure mode that actually happens.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sprezzature_video import (
    Claim,
    ClaimSource,
    as_claim,
    numbers_in,
    undeclared_numbers,
    verify,
    visible_text,
)


@pytest.fixture()
def catalogue(tmp_path: Path) -> Path:
    """A project root holding a 167-entry catalogue, like figures' real one."""
    root = tmp_path
    target = root / "pkg" / "catalog" / "figures.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps([{"kind": f"k{i}"} for i in range(167)]))
    return root


def _kinds_claim(value: int) -> Claim:
    return Claim(
        text=f"{value} kinds, every one hand-authored.",
        value=value,
        source=ClaimSource(path="pkg/catalog/figures.json", method="json_len"),
    )


def test_the_shipped_127_is_caught(catalogue: Path) -> None:
    """The real defect: a film claiming 127 against a catalogue of 167."""
    verdict = verify(_kinds_claim(127), catalogue)
    assert not verdict.ok
    # The message has to name both numbers AND the deciding file, because the
    # person reading it has to find the frame to re-cut and the authority to
    # trust. A bare "mismatch" sends them hunting.
    assert "127" in verdict.detail
    assert "167" in verdict.detail
    assert "figures.json" in verdict.detail


def test_a_true_claim_passes(catalogue: Path) -> None:
    """The same claim, corrected, must pass -- or the guard is just noise."""
    assert verify(_kinds_claim(167), catalogue).ok


def test_a_missing_source_fails_rather_than_skips(tmp_path: Path) -> None:
    """
    A claim whose deciding file has moved is unverified, and unverified must
    never read as verified.

    This is the shape of defect the suite keeps finding: a guard whose input
    disappears and which then reports success. Pinned here deliberately.
    """
    verdict = verify(_kinds_claim(167), tmp_path)
    assert not verdict.ok
    assert "could not verify" in verdict.detail


def test_a_malformed_source_fails_rather_than_raises(tmp_path: Path) -> None:
    """Unparseable JSON is a failed claim, not a crashed test run."""
    target = tmp_path / "pkg" / "catalog" / "figures.json"
    target.parent.mkdir(parents=True)
    target.write_text("{not json")
    verdict = verify(_kinds_claim(167), tmp_path)
    assert not verdict.ok


def test_a_json_object_is_refused_by_json_len(tmp_path: Path) -> None:
    """
    ``json_len`` means "length of an array". Handed an object it must refuse,
    not return the key count -- which would be a plausible wrong number, the
    worst kind.
    """
    target = tmp_path / "pkg" / "catalog" / "figures.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"a": 1, "b": 2}))
    verdict = verify(_kinds_claim(2), tmp_path)
    assert not verdict.ok


def test_only_visible_text_is_read() -> None:
    """
    Stylesheet and script numbers are not claims.

    Counting them would bury the four or five real assertions under several
    hundred lengths, offsets and hex digits -- and a report nobody can read is
    a report nobody runs.
    """
    html = """
    <head><title>127</title></head>
    <style>.hook { width: 1200px; letter-spacing: 0.02em }</style>
    <script>const BEAT = 4.0;</script>
    <p>167 kinds</p>
    """
    assert visible_text(html) == "167 kinds"


def test_nested_templates_do_not_re_enable_collection() -> None:
    """
    The suppression state must be a counter, not a boolean.

    ``<template>`` genuinely nests, so with a boolean the inner ``</template>``
    here would switch collection back on and ``c`` would be read as on-screen
    text. ``<style>`` cannot demonstrate this -- see the next test for why.
    """
    html = "<template>a<template>b</template>c</template><p>7 kinds</p>"
    assert visible_text(html) == "7 kinds"


def test_a_cdata_block_ends_at_its_first_close_as_a_browser_does() -> None:
    """
    ``<style>`` and ``<script>`` are CDATA: an inner ``<style>`` is not an
    element, and the first ``</style>`` ends the block.

    So the trailing ``.c{width:9px}`` below really is visible text -- a browser
    paints it on the page too. This test pins the browser-matching behaviour
    rather than a tidier-looking rule that would be wrong: a composition that
    leaks CSS onto the screen has a bug the extractor should surface, not hide.
    """
    html = "<style>.a{}<style>.b{}</style>.c{width:9px}</style><p>7 kinds</p>"
    assert visible_text(html) == ".c{width:9px} 7 kinds"


def test_a_plain_stylesheet_is_fully_suppressed() -> None:
    """The ordinary case, so the test above cannot be mistaken for the rule."""
    assert visible_text("<style>.c{width:9px}</style><p>7 kinds</p>") == "7 kinds"


def test_a_spaced_thousand_is_one_number() -> None:
    """
    "1 000" is one number, whichever space it uses.

    The separator class first held only U+00A0, the French thousands
    separator, and so could never fire: ``visible_text`` collapses runs of
    ``\\s``, Python counts U+00A0 as whitespace, and the text always arrived
    spaced with U+0020. Both forms are pinned so the branch stays reachable.
    """
    assert numbers_in("1 000 tests") == ["1 000"]
    assert numbers_in("1\u00a0000 tests") == ["1\u00a0000"]  # U+00A0, French
    assert numbers_in("1\u202f000 tests") == ["1\u202f000"]  # U+202F, narrow


def test_two_separate_numbers_stay_separate() -> None:
    """The permissive separator must not glue distinct assertions together."""
    assert numbers_in("20 rules 30 laws") == ["20", "30"]


def test_an_undeclared_number_on_screen_is_reported() -> None:
    """
    The other direction, and the half that makes this worth having.

    Checking only declared claims protects the numbers someone thought to
    declare -- never the one typed into a keyframe and left to go stale.
    """
    html = "<p>167 kinds, 960 tests</p>"
    claims = [_kinds_claim(167)]
    found = undeclared_numbers(html, claims)
    assert [u.written for u in found] == ["960"]
    # Context, so the scene can be found without opening every composition.
    assert "kinds" in found[0].context


def test_an_exempted_number_is_not_reported() -> None:
    """A year in a wordmark is on screen without being a claim about the code."""
    html = "<p>167 kinds — Sprezzature 2026</p>"
    found = undeclared_numbers(html, [_kinds_claim(167)], ignore=frozenset({2026}))
    assert found == []


def test_a_half_written_claim_refuses_to_load() -> None:
    """
    A claim missing its source must raise, not load as a claim that passes.

    Defaulting here would mean a typo in a spec silently removes an assertion
    from the guard while leaving it on screen.
    """
    with pytest.raises(KeyError):
        as_claim({"text": "167 kinds", "value": 167})


def test_literal_claims_check_wording_not_counts(tmp_path: Path) -> None:
    """Not every claim is a number: a quoted phrase must still be traceable."""
    page = tmp_path / "web" / "loop.html"
    page.parent.mkdir(parents=True)
    page.write_text("<h1>You can't proofread a chart.</h1>")
    claim = Claim(
        text="You can't proofread a chart.",
        value="You can't proofread a chart.",
        source=ClaimSource(
            path="web/loop.html",
            method="literal",
            selector="You can't proofread a chart.",
        ),
    )
    assert verify(claim, tmp_path).ok
