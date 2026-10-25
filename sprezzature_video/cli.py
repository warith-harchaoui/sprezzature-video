#!/usr/bin/env python3
"""
sprezzature-video — the Click twin of ``make-film``.

Same five operations as the argparse entry point, same exit codes, reached
through a different door. Both exist on purpose across this suite: argparse is
always installed, so the primary command never depends on an extra, while Click
gives composable sub-commands and shell completion to anyone who has it.

The two must not drift. Everything they do is delegated to the same library
functions, so a difference between them can only be in wording, never in
behaviour.

Install the extra::

    pip install 'sprezzature-video[cli]'

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from sprezzature_video import assets as assets_mod
from sprezzature_video import captions as captions_mod
from sprezzature_video import claims as claims_mod
from sprezzature_video import spec as spec_mod

#: Shown under the command list. Completion is click's, and worth saying out
#: loud: nobody discovers it by guessing.
_EPILOG = """\
Shell completion:

  \b
  eval "$(_SPREZZATURE_VIDEO_COMPLETE=bash_source sprezzature-video)"   # bash
  eval "$(_SPREZZATURE_VIDEO_COMPLETE=zsh_source sprezzature-video)"    # zsh

Exit codes: 0 the film is still honest, 1 it is not, 2 the call was wrong.
"""


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog=_EPILOG,
)
@click.version_option(package_name="sprezzature-video")
def main() -> None:
    """Check what a film says against the project it describes."""


@main.command()
@click.argument("spec_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--root", default=".", help="Directory claim sources are relative to.")
def verify(spec_path: str, root: str) -> None:
    """Verify a film's declared claims against the code."""
    film = spec_mod.load(spec_path)
    if not film.claims:
        # Silence here would read exactly like a film that checks out.
        raise click.ClickException(f"{spec_path}: no claims declared — nothing was checked")
    verdicts = claims_mod.verify_all(film.claims, root)
    for verdict in verdicts:
        click.echo(("ok   " if verdict.ok else "FAIL ") + verdict.detail)
    bad = [v for v in verdicts if not v.ok]
    click.echo(f"\n{len(verdicts) - len(bad)}/{len(verdicts)} claims hold")
    if bad:
        sys.exit(1)


@main.command()
@click.argument("composition", type=click.Path(exists=True, dir_okay=False))
@click.option("--spec", "spec_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--ignore", default="", help="Comma-separated non-claim values on screen.")
def scan(composition: str, spec_path: str | None, ignore: str) -> None:
    """Find numbers on screen that no claim accounts for."""
    declared = spec_mod.load(spec_path).claims if spec_path else []
    skip = frozenset(int(p) for p in (piece.strip() for piece in ignore.split(",")) if p.isdigit())
    html = Path(composition).read_text(encoding="utf-8")
    found = claims_mod.undeclared_numbers(html, declared, ignore=skip)
    for item in found:
        click.echo(f"UNDECLARED {item.written!r} in {item.context!r}")
    click.echo(f"\n{len(found)} undeclared number(s) on screen")
    if found:
        sys.exit(1)


@main.command()
@click.argument("spec_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--tree", required=True, type=click.Path(), help="The asset tree.")
@click.option("--repo", default=".", help="Root that tracked sources are relative to.")
@click.option("--restore", is_flag=True, help="Copy back absent tracked assets only.")
def assets(spec_path: str, tree: str, repo: str, restore: bool) -> None:
    """Audit the asset tree a film renders from."""
    film = spec_mod.load(spec_path)
    if restore:
        for line in film.ledger.restore(tree, repo):
            click.echo(line)
    verdicts = film.ledger.audit(tree, repo)
    for line in assets_mod.report(verdicts):
        click.echo(line)
    held = sum(1 for v in verdicts if v.ok)
    click.echo(f"\n{held}/{len(verdicts)} assets in hand")
    if held != len(verdicts):
        sys.exit(1)


@main.command()
@click.argument("spec_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--lang", required=True, help="Language key in the spec's narration map.")
@click.option("--out", type=click.Path(), help="Output .vtt. Default: stdout.")
@click.option("--translated", is_flag=True, help="Omit voice tags on a translated track.")
def captions(spec_path: str, lang: str, out: str | None, translated: bool) -> None:
    """Write WebVTT from the narration script and the measured audio."""
    film = spec_mod.load(spec_path)
    if lang not in film.narration:
        known = ", ".join(sorted(film.narration)) or "none"
        raise click.ClickException(f"no narration for {lang!r}; the spec has: {known}")
    body = captions_mod.write(film.narration[lang], translated=translated)
    if out:
        Path(out).write_text(body, encoding="utf-8")
        click.echo(out)
    else:
        click.echo(body)


@main.command()
@click.argument("video", type=click.Path(exists=True, dir_okay=False))
@click.option("--out", required=True, type=click.Path(), help="Output .jpg.")
@click.option("--at", type=float, required=True, help="Frame time in seconds.")
def poster(video: str, out: str, at: float) -> None:
    """Extract a frame of a rendered film as JPEG."""
    from sprezzature_video import post

    click.echo(str(post.poster(video, out, at=at)))


if __name__ == "__main__":
    main()
