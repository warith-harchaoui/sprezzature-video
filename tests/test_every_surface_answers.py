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
import subprocess
import sys
from pathlib import Path

import pytest

from sprezzature_video import cli

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
    assert cli.main(["verify", str(project / "film.yaml"), "--root", str(project)]) == 0


def test_verify_exits_1_when_the_code_disagrees(project: Path) -> None:
    """The exit code is the whole point: it is what makes this usable as a gate."""
    (project / "catalog" / "figures.json").write_text(json.dumps([{"k": i} for i in range(127)]))
    assert cli.main(["verify", str(project / "film.yaml"), "--root", str(project)]) == 1


def test_verify_refuses_a_spec_with_no_claims(tmp_path: Path) -> None:
    """
    An empty claim list must not pass.

    "0/0 claims hold" reads exactly like a film that checks out, which is the
    failure mode this package exists to prevent.
    """
    (tmp_path / "empty.yaml").write_text("name: empty\nclaims: []\n")
    assert cli.main(["verify", str(tmp_path / "empty.yaml"), "--root", str(tmp_path)]) == 1


def test_a_missing_spec_is_a_usage_error_not_a_crash(tmp_path: Path) -> None:
    """2, not 1: "you passed a bad path" is not "the film is wrong"."""
    assert cli.main(["verify", str(tmp_path / "absent.yaml")]) == 2


def test_scan_finds_an_undeclared_number(project: Path, tmp_path: Path) -> None:
    page = tmp_path / "index.html"
    page.write_text("<p>167 kinds, 960 tests</p>")
    assert cli.main(["scan", str(page), "--spec", str(project / "film.yaml")]) == 1


def test_scan_accepts_an_exempted_value(project: Path, tmp_path: Path) -> None:
    page = tmp_path / "index.html"
    page.write_text("<p>167 kinds — Sprezzature 2026</p>")
    args = ["scan", str(page), "--spec", str(project / "film.yaml"), "--ignore", "2026"]
    assert cli.main(args) == 0


def test_the_click_twin_agrees_with_argparse(project: Path) -> None:
    """
    Same question, same verdict, through the other door.

    The two CLIs delegate to one implementation, so a difference between them
    could only be wording — and this is what would catch it if one ever grew
    its own logic.
    """
    spec, root = str(project / "film.yaml"), str(project)
    argparse_code = cli.main(["verify", spec, "--root", root])
    click_run = subprocess.run(
        [sys.executable, "-m", "sprezzature_video.cli_click", "verify", spec, "--root", root],
        capture_output=True,
        text=True,
        check=False,
    )
    assert click_run.returncode == argparse_code == 0


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
