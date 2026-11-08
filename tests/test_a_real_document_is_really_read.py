"""
A composition is a whole HTML document, and every path out says what happened.

Two groups of defects found together, because they share a shape: the tool
answered, and the answer said something other than what was true.

The first group is ``scan``. Its tests fed it fragments, and fragments have no
``<head>``. A real composition opens with ``<meta charset>``, a void element
that the parser counted as opened and never closed, so ``</head>`` left the
whole body suppressed: no visible text, "0 undeclared number(s)", exit 0, on
every real film.

The second group is the exit codes. 1 means the film is lying; 2 means the call
was wrong. An uncaught exception also leaves Python with 1, so a broken spec
read to a gate as a verdict on a film nobody had looked at.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from sprezzature_video.claims import (
    Claim,
    ClaimSource,
    numbers_in,
    undeclared_numbers,
    verify,
    visible_text,
)
from sprezzature_video.cli import main as cli_main

_DOCUMENT = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=1920">
  <title>Film 2026</title>
  <style>.a{width:512px}</style>
</head>
<body>
  <p>127 chart kinds</p>
</body>
</html>
"""


def _claim(text: str, value: int) -> Claim:
    return Claim(text=text, value=value, source=ClaimSource(path="x.json", method="json_len"))


def test_the_body_of_a_real_document_is_visible() -> None:
    """Void ``meta`` tags in the head must not swallow the body."""
    assert visible_text(_DOCUMENT) == "127 chart kinds"


def test_scan_reports_a_number_in_a_real_document() -> None:
    """The end-to-end form of the defect: this returned an empty list."""
    assert [u.written for u in undeclared_numbers(_DOCUMENT, [])] == ["127"]


def test_a_head_left_unclosed_does_not_hide_the_body() -> None:
    """``</head>`` is optional in HTML, and the body is still the body."""
    assert visible_text("<head><title>x</title><body><p>7 kinds</p>") == "7 kinds"


def test_a_spoken_list_is_several_numbers() -> None:
    """A comma and a space separate items; they do not group digits."""
    assert numbers_in("10, 20, 30") == ["10", "20", "30"]


def test_a_decimal_and_a_grouped_thousand_stay_whole() -> None:
    """The separators that are real still join."""
    assert numbers_in("1,000 tests at 3.5 s, 12 000 lines") == ["1,000", "3.5", "12 000"]


def test_a_year_beside_a_claim_can_be_accounted_for() -> None:
    """Glued together, neither ``ignore`` nor the claim could reach them."""
    html = "<p>Since 2026, 167 charts</p>"
    assert undeclared_numbers(html, [_claim("167 charts", 167)], ignore=frozenset({2026})) == []


def test_neighbouring_elements_hold_separate_numbers() -> None:
    """Two boxes in a stat row are two numbers."""
    found = undeclared_numbers("<b>127</b><b>168</b>", [])
    assert [u.written for u in found] == ["127", "168"]


def test_a_number_inside_a_longer_one_is_not_accounted_for() -> None:
    """A claim about 167 says nothing about a 16 on screen."""
    found = undeclared_numbers("<p>16 tests</p>", [_claim("167 kinds", 167)])
    assert [u.written for u in found] == ["16"]


def test_a_number_shown_twice_is_placed_twice() -> None:
    """Each report points at its own scene, not twice at the first."""
    html = f"<p>first scene 960 {'x' * 90}</p><p>second scene 960</p>"
    contexts = [u.context for u in undeclared_numbers(html, [])]
    assert "first scene" in contexts[0]
    assert "second scene" in contexts[1]


@pytest.mark.parametrize(
    ("method", "selector", "content"),
    [
        ("regex_count", "(unclosed", "text"),
        ("json_key_len", "n", '{"n": 3}'),
    ],
)
def test_a_source_that_cannot_be_read_is_a_verdict(
    tmp_path: Path, method: str, selector: str, content: str
) -> None:
    """A bad selector and a count over a scalar fail the claim, and do not raise."""
    (tmp_path / "x.txt").write_text(content, encoding="utf-8")
    claim = Claim("3 things", 3, ClaimSource(path="x.txt", method=method, selector=selector))  # type: ignore[arg-type]
    assert verify(claim, tmp_path).ok is False


def test_a_source_that_became_a_directory_is_a_verdict(tmp_path: Path) -> None:
    """``read_text`` on a directory raises an OSError that is not FileNotFoundError."""
    (tmp_path / "x").mkdir()
    claim = Claim("3 lines", 3, ClaimSource(path="x", method="line_count"))
    assert verify(claim, tmp_path).ok is False


@pytest.mark.parametrize(
    "content",
    [
        "claims: [unterminated\n",
        "- a\n- list\n",
        "assets:\n  - {rel: m.mp3, provenance: sole}\n",
        "assets:\n  - {rel: m.mp3, provenance: bought}\n",
        "claims:\n  - {text: only}\n",
        "narration:\n  en:\n    - {text: no start}\n",
    ],
)
def test_a_spec_that_will_not_load_is_a_wrong_call(tmp_path: Path, content: str) -> None:
    """Exit 2 and one line. A traceback exits 1, which reads as a verdict."""
    spec = tmp_path / "film.yaml"
    spec.write_text(content, encoding="utf-8")
    result = CliRunner().invoke(cli_main, ["verify", str(spec)])
    assert result.exit_code == 2
    assert isinstance(result.exception, SystemExit)
    assert "not a usable film spec" in result.output


def test_pitch_on_a_cut_the_spec_lacks_is_a_wrong_call(tmp_path: Path) -> None:
    """The twin of ``calque``, which 0.4.4 fixed alone."""
    spec = tmp_path / "film.yaml"
    spec.write_text("name: demo\n", encoding="utf-8")
    result = CliRunner().invoke(cli_main, ["pitch", str(spec), "--duration", "60", "--voice", "fr"])
    assert result.exit_code == 2
    assert "no fr narration" in result.output


@pytest.mark.parametrize(
    "line",
    [
        "{start: 0.0, text: no timing at all}",
        "{start: 0.0, text: gone, audio: voice/absent.wav}",
    ],
)
def test_captions_that_cannot_be_timed_are_a_wrong_call(tmp_path: Path, line: str) -> None:
    """The refusals the route answers with a 400 are exit 2 here, not a traceback."""
    spec = tmp_path / "film.yaml"
    spec.write_text(f"narration:\n  en:\n    - {line}\n", encoding="utf-8")
    result = CliRunner().invoke(cli_main, ["captions", str(spec), "--lang", "en"])
    assert result.exit_code == 2
    assert isinstance(result.exception, SystemExit)


def test_poster_on_a_file_ffmpeg_refuses_is_a_wrong_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No ffmpeg needed: the refusal is what is under test, so it is staged."""
    from sprezzature_video import post

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise subprocess.CalledProcessError(1, "ffmpeg")

    monkeypatch.setattr(post, "_ffmpeg", lambda: "ffmpeg")
    monkeypatch.setattr(post.subprocess, "run", refuse)
    not_a_film = tmp_path / "film.mp4"
    not_a_film.write_text("text", encoding="utf-8")
    result = CliRunner().invoke(
        cli_main, ["poster", str(not_a_film), "--out", str(tmp_path / "p.jpg"), "--at", "1"]
    )
    assert result.exit_code == 2
    assert "could not take a frame" in result.output


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/v1/scan", {"html": "<p>1</p>", "claims": [{"text": "t", "value": 1, "source": {}}]}),
        (
            "/v1/verify",
            {"root": ".", "claims": [{"text": "t", "value": 1, "source": {"path": "x"}}]},
        ),
    ],
)
def test_a_claim_without_its_source_is_a_400(path: str, body: dict[str, object]) -> None:
    """The caller's mistake, said as such: this was a 500."""
    from fastapi.testclient import TestClient

    from sprezzature_video.api import app

    response = TestClient(app).post(path, json=body)
    assert response.status_code == 400
    assert "lacks" in response.json()["detail"]
