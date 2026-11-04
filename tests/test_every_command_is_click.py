"""
Every command of the package is click, and nothing in the package imports argparse.

The suite settled on click alone: the front-door group was converted on
2026-10-25, and ``sprezzature-video-mcp`` still built an argparse parser inside
its ``main`` until 2026-11-04. ``test_every_surface_answers`` checked
``cli.py`` only, so the second parser sat one file away from the guard.

This one reads ``[project.scripts]`` rather than a list typed here, so a new
console script is covered the day it is declared, and it walks every module of
the package rather than naming one.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_PACKAGE = _ROOT / "sprezzature_video"


def _console_scripts() -> dict[str, str]:
    """``[project.scripts]``, by regex: ``tomllib`` does not exist on 3.10."""
    text = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"^\[project\.scripts\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    return dict(re.findall(r'^([\w.-]+)\s*=\s*"([^"]+)"', block.group(1), re.M)) if block else {}


def test_the_manifest_declares_commands() -> None:
    """A regex that matched nothing would make the next test pass on zero cases."""
    assert len(_console_scripts()) >= 3


@pytest.mark.parametrize("name", sorted(_console_scripts()))
def test_every_console_script_answers_help_like_click(name: str) -> None:
    """
    ``--help`` exits 0 with click's ``Usage:`` line, not argparse's ``usage:``.

    The entry point is called through the interpreter running the tests rather
    than looked up on PATH, so a stale editable install cannot answer for the
    code in this checkout.
    """
    module, func = _console_scripts()[name].split(":")
    code = f"import sys; from {module} import {func} as f; sys.argv[0] = {name!r}; f(['--help'])"
    done = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False, cwd=_ROOT
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith("Usage: "), done.stdout[:200]


def test_no_module_of_the_package_imports_argparse() -> None:
    """Parsed, not grepped: a docstring that names argparse is not an import."""
    offenders = []
    for path in sorted(_PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any(n == "argparse" or n.startswith("argparse.") for n in names):
                offenders.append(f"{path.relative_to(_ROOT)}:{node.lineno}")
    assert not offenders, offenders


def test_the_container_serves_mcp_beside_the_routes() -> None:
    """
    The image runs the MCP server, not the bare app.

    ``uvicorn sprezzature_video.api:app`` serves ``/v1/...`` and answers 404 on
    ``/mcp``: the endpoint is mounted when ``sprezzature_video.mcp`` is imported,
    and the bare app never imports it.
    """
    for name in ("Dockerfile", "docker-compose.yml"):
        text = (_ROOT / name).read_text(encoding="utf-8")
        assert '"sprezzature-video-mcp", "--host", "0.0.0.0"' in text, name
