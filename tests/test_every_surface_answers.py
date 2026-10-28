"""
The five surfaces, and the rule that they cannot disagree.

A library, two command lines, an HTTP API and a set of MCP tools are five ways
into one implementation — so the interesting tests are not "does the route
return 200" but "does the route return what the function returned". Where a
surface is allowed to differ, it is in wording and exit codes, never in the
finding.

The second thing pinned here is that every command **starts**. Three commands
shipped on PATH in 0.1.0 and died on import, because the entry points were
declared before the modules existed. `--help` answering in 0 is cheap and
catches exactly that.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from sprezzature_video.cli import main as cli_main

_MANIFEST_ROOT = Path(__file__).resolve().parent.parent


def _console_scripts() -> dict[str, str]:
    """
    ``[project.scripts]``, read with a regex rather than ``tomllib``.

    ``tomllib`` is standard library only from 3.11 and this package supports
    3.10, where the import alone fails -- in CI, while passing on every
    developer machine. sprezzature-cli-gui's own test says exactly this in a
    comment, and it was written there because it had already happened once.
    """
    text = (_MANIFEST_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"^\[project\.scripts\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if block is None:
        return {}
    return dict(re.findall(r'^([\w.-]+)\s*=\s*"([^"]+)"', block.group(1), re.M))


def _base_dependencies() -> str:
    """The ``dependencies = [...]`` block as text, comments stripped."""
    text = (_MANIFEST_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"^dependencies\s*=\s*\[(.*?)\]", text, re.M | re.S)
    return re.sub(r"#[^\n]*", "", block.group(1)) if block else ""


def _extras() -> set[str]:
    """The extras this package declares."""
    text = (_MANIFEST_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"^\[project\.optional-dependencies\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    return set(re.findall(r"^([\w.-]+)\s*=\s*\[", block.group(1), re.M)) if block else set()


def _run(args: list[str]) -> int:
    """
    Invoke the command line and return its exit code.

    Click signals through SystemExit rather than a return value, so the
    argparse-era `main(argv) -> int` calls became this when the second parser
    was removed on 2026-10-25.
    """
    return CliRunner().invoke(cli_main, args).exit_code


SPEC = """
name: demo
claims:
  - text: "167 kinds, every one hand-authored."
    value: 167
    source:
      path: catalog/figures.json
      method: json_len
"""


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    """A spec, and a catalogue of 167 entries for it to be right about."""
    (tmp_path / "film.yaml").write_text(SPEC)
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / "figures.json").write_text(json.dumps([{"k": i} for i in range(167)]))
    return tmp_path


# ---------------------------------------------------------------- the CLIs


@pytest.mark.parametrize("command", ["make-film", "sprezzature-video", "sprezzature-video-mcp"])
def test_every_command_can_start(command: str) -> None:
    """
    `--help` answers in 0, and the help names the command.

    A help screen announcing a module path tells the reader nothing they can
    type. Both halves matter: 0.1.0 shipped three commands that resolved on
    PATH and raised ModuleNotFoundError when run.
    """
    done = subprocess.run([command, "--help"], capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stderr
    assert command in done.stdout


def test_verify_exits_0_when_the_claim_holds(project: Path) -> None:
    assert _run(["verify", str(project / "film.yaml"), "--root", str(project)]) == 0


def test_verify_exits_1_when_the_code_disagrees(project: Path) -> None:
    """The exit code is the whole point: it is what makes this usable as a gate."""
    (project / "catalog" / "figures.json").write_text(json.dumps([{"k": i} for i in range(127)]))
    assert _run(["verify", str(project / "film.yaml"), "--root", str(project)]) == 1


def test_verify_refuses_a_spec_with_no_claims(tmp_path: Path) -> None:
    """
    An empty claim list must not pass.

    "0/0 claims hold" reads exactly like a film that checks out, which is the
    failure mode this package exists to prevent.
    """
    (tmp_path / "empty.yaml").write_text("name: empty\nclaims: []\n")
    assert _run(["verify", str(tmp_path / "empty.yaml"), "--root", str(tmp_path)]) == 1


def test_a_missing_spec_is_a_usage_error_not_a_crash(tmp_path: Path) -> None:
    """2, not 1: "you passed a bad path" is not "the film is wrong"."""
    assert _run(["verify", str(tmp_path / "absent.yaml")]) == 2


def test_scan_finds_an_undeclared_number(project: Path, tmp_path: Path) -> None:
    page = tmp_path / "index.html"
    page.write_text("<p>167 kinds, 960 tests</p>")
    assert _run(["scan", str(page), "--spec", str(project / "film.yaml")]) == 1


def test_scan_accepts_an_exempted_value(project: Path, tmp_path: Path) -> None:
    page = tmp_path / "index.html"
    page.write_text("<p>167 kinds — Sprezzature 2026</p>")
    args = ["scan", str(page), "--spec", str(project / "film.yaml"), "--ignore", "2026"]
    assert _run(args) == 0


#: A film in two languages, with its beats on the scene grid and a sentence
#: on each one. Enough for the two sub-commands that read a *script* rather
#: than a claim -- and the scene text matters: an empty magic scene is a
#: zero-word secret sauce, which the checker correctly calls a label.
VOICED = """
name: demo
pitch:
  problem: [0]
  solution: [1]
  magic: [2]
scenes:
  - {text: "Light grey on white reads fine. To whoever picked it.", start: 5.0}
  - {text: "It redraws the chart the way that eye sees it.", start: 20.0}
  - {text: "Hue goes, saturation goes, and lightness is what holds.", start: 40.0}
narration:
  en:
    - {start: 6.0,  text: "Light grey on white reads fine. At your desk, indoors.", duration: 4.0}
    - {start: 21.0, text: "So it redraws the picture the way that eye sees it.", duration: 4.0}
    - {start: 41.0, text: "MAGIC_EN", duration: 4.0}
  fr:
    - {start: 6.0,  text: "Du gris clair sur du blanc se lit tres bien. Chez vous, a l_interieur.", duration: 4.0}
    - {start: 21.0, text: "Il redessine donc l'image telle que cet oeil-la la voit.", duration: 4.0}
    - {start: 41.0, text: "MAGIC_FR", duration: 4.0}
"""

#: The same magic line in both languages, one sentence each. With three lines
#: the score can only be 0, 1/3, 2/3 or 1, so a fixture standing for "this was
#: translated" has to correspond at *every* position -- which is why the first
#: French line is two sentences like its English, not one.
_RENDERED = {
    "MAGIC_EN": "Hue goes, saturation goes, and lightness is what nothing removes.",
    "MAGIC_FR": "La teinte s_en va, la saturation s_en va, et rien ne retire la clarte.",
}

#: The French magic beat composed instead: three short sentences where the
#: English runs one long one, so the last position stops corresponding.
_COMPOSED = {
    "MAGIC_EN": "Hue goes, saturation goes, and lightness is what nothing removes.",
    "MAGIC_FR": "La teinte s_en va. La saturation aussi. La clarte, rien ne la retire.",
}


def _spec(tmp_path: Path, name: str, magic: dict[str, str]) -> Path:
    doc = tmp_path / f"{name}.yaml"
    body = VOICED
    for key, line in magic.items():
        body = body.replace(key, line)
    doc.write_text(body)
    return doc


def test_the_pitch_can_be_read_in_the_voice_from_the_command_line(tmp_path: Path) -> None:
    """The library grew a second reading; the command line has to reach it.

    This package exists because of tools nothing calls. `from_narration` would
    have been the next one: a function, a test, and no door.
    """
    doc = _spec(tmp_path, "film", _COMPOSED)
    assert _run(["pitch", str(doc), "--duration", "60"]) == 0
    assert _run(["pitch", str(doc), "--duration", "60", "--voice", "en"]) == 0
    assert _run(["pitch", str(doc), "--duration", "60", "--voice", "fr"]) == 0


def test_an_unknown_language_is_a_failure_and_not_a_pass(tmp_path: Path) -> None:
    """Asked about a cut that is not there, it must not answer "fine"."""
    doc = _spec(tmp_path, "film", _COMPOSED)
    assert _run(["pitch", str(doc), "--duration", "60", "--voice", "de"]) != 0
    assert _run(["calque", str(doc), "--to", "de"]) != 0


def test_calque_exits_1_on_a_translated_cut_and_0_on_a_written_one(tmp_path: Path) -> None:
    """Both directions, because a measure that cannot pass is switched off."""
    assert _run(["calque", str(_spec(tmp_path, "rendered", _RENDERED))]) == 1, (
        "a line-for-line French cut passed"
    )
    assert _run(["calque", str(_spec(tmp_path, "composed", _COMPOSED))]) == 0, (
        "a written French cut was flagged"
    )


def test_the_two_spellings_are_one_callable() -> None:
    """
    ``make-film`` and ``sprezzature-video`` must resolve to the same target.

    This replaces a test that ran both parsers and compared their exit codes.
    Two names that each had their own implementation is how a pair drifts; two
    names pointing at one function cannot.
    """
    scripts = _console_scripts()
    assert scripts["make-film"] == scripts["sprezzature-video"]
    assert scripts["make-film"] == "sprezzature_video.cli:main"


def test_no_second_parser_grows_back() -> None:
    """A second front door would re-introduce the duplicate command list."""
    pkg = _MANIFEST_ROOT / "sprezzature_video"
    assert not (pkg / "cli_click.py").exists()
    assert "import argparse" not in (pkg / "cli.py").read_text(encoding="utf-8")


# ----------------------------------------------------------------- the API


@pytest.fixture()
def client():  # type: ignore[no-untyped-def]
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from sprezzature_video.api import app

    return fastapi_testclient.TestClient(app)


def test_health_answers(client) -> None:  # type: ignore[no-untyped-def]
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["service"] == "sprezzature-video"


def test_scan_route_matches_the_library(client) -> None:  # type: ignore[no-untyped-def]
    """The HTTP finding and the library finding are the same finding."""
    from sprezzature_video import Claim, ClaimSource, undeclared_numbers

    html = "<p>167 kinds, 960 tests</p>"
    claim = {
        "text": "167 kinds",
        "value": 167,
        "source": {"path": "catalog/figures.json", "method": "json_len"},
    }
    body = client.post("/v1/scan", json={"html": html, "claims": [claim]}).json()

    direct = undeclared_numbers(
        html,
        [Claim("167 kinds", 167, ClaimSource("catalog/figures.json", "json_len"))],
    )
    assert [u["written"] for u in body["undeclared"]] == [d.written for d in direct] == ["960"]
    assert body["ok"] is False


def test_verify_route_refuses_an_empty_claim_list(client) -> None:  # type: ignore[no-untyped-def]
    """400, not "all claims hold" — the same refusal the CLI makes."""
    assert client.post("/v1/verify", json={"claims": [], "root": "."}).status_code == 400


def test_captions_route_refuses_an_untimed_line(client) -> None:  # type: ignore[no-untyped-def]
    """A line with neither audio nor duration has unknown timing."""
    body = {"lines": [{"start": 0.0, "text": "No timing at all."}], "translated": False}
    assert client.post("/v1/captions", json=body).status_code == 400


def test_every_route_declares_its_own_summary(client) -> None:  # type: ignore[no-untyped-def]
    """
    FastAPI invents a summary from the function name when none is given, so a
    route called `scan_composition` silently documents itself as "Scan
    Composition". That string is what an MCP host shows an agent choosing a
    tool, so it has to be written, not generated.
    """
    schema = client.get("/openapi.json").json()
    for path, methods in schema["paths"].items():
        for verb, spec in methods.items():
            summary = spec.get("summary", "")
            assert summary, f"{verb.upper()} {path} has no summary"
            # A generated summary is the title-cased operation id.
            generated = spec.get("operationId", "").replace("_", " ").title()
            assert summary != generated, f"{verb.upper()} {path} has a generated summary"


# ----------------------------------------------------------------- the MCP


def test_the_mcp_fallback_takes_the_same_arguments() -> None:
    """
    Both branches of the dependency guard are reached through one console
    script, so a caller passing argv must not get a TypeError from whichever
    branch happens to be missing its dependency.
    """
    import inspect

    from sprezzature_video import mcp as mcp_mod

    params = list(inspect.signature(mcp_mod.main).parameters)
    assert params == ["argv"]


def test_mcp_mounts_on_the_same_app() -> None:
    """MCP is a wrapper, not a second implementation."""
    pytest.importorskip("fastapi_mcp")
    from sprezzature_video import mcp as mcp_mod  # noqa: F401
    from sprezzature_video.api import app

    paths = {getattr(route, "path", "") for route in app.routes}
    assert "/v1/scan" in paths
    assert any("mcp" in path for path in paths)
