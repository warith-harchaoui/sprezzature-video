#!/usr/bin/env python3
"""
sprezzature-video — the command line.

``make-film`` and ``sprezzature-video`` are two spellings of this one group,
both declared in ``[project.scripts]`` and both landing here. They were two
implementations once — an argparse primary and a Click twin — on the reasoning
that argparse is always installed; the suite settled that on 2026-10-25 by
making Click a base dependency in all ten packages, and this header went on
describing the arrangement it replaced.

Everything is delegated to the library, so a sub-command can differ from the
function behind it in wording and never in behaviour.

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


@main.command()
@click.argument("text_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--lang", default="en", type=click.Choice(["en", "fr"]), help="Which charter to apply."
)
@click.option("--strict", is_flag=True, help="Exit 1 on any hard finding, for a pre-commit hook.")
def prose(text_file: str, lang: str, strict: bool) -> None:
    """Check writing against the charter: one line per line of text.

    The mechanical half only. Whether a sentence earns its place stays a
    human question, and a checker that pretended otherwise would let a green
    tick stand in for a reading.
    """
    from sprezzature_video import charter

    lines = [
        (f"line {n}", line.strip())
        for n, line in enumerate(Path(text_file).read_text(encoding="utf-8").splitlines(), 1)
        if line.strip()
    ]
    result = charter.measure(lines, lang)
    for finding in result["findings"]:
        click.echo(str(finding))
    click.echo(f"\n{len(result['findings'])} hard finding(s) over {result['lines']} line(s)")
    click.echo(
        f"{result['antithesis']} reflex antithesis, {result['modals']} modal(s): "
        f"places to read, not verdicts"
    )
    if strict and result["findings"]:
        raise SystemExit(1)


@main.command()
@click.argument("spec_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--duration", type=float, required=True, help="The film's length in seconds.")
@click.option(
    "--voice",
    "lang",
    default="",
    help="Read the narration of this language instead of the text on screen.",
)
def pitch(spec_path: str, duration: float, lang: str) -> None:
    """Check a film explains itself: problem, then solution, then secret sauce.

    Guy KAWASAKI's order. The third beat is the one people get wrong: the
    underlying magic is the single non-obvious thing that makes the solution
    possible, in plain language. A feature list is not it.

    Without ``--voice`` this reads the words on screen: one sentence a scene.
    With it, the narration of that language, which over a sixty-second film is
    eight times as many words and is most of what a viewer actually receives.
    A film can carry the three beats in its scene list and say something else
    out loud, and only the second reading sees that.
    """
    from sprezzature_video import pitch as pitch_mod
    from sprezzature_video import spec as spec_mod

    film = spec_mod.load(spec_path)
    scenes = getattr(film, "scenes", []) or []
    if lang:
        report = pitch_mod.from_narration(film, lang, duration)
    else:
        report = pitch_mod.from_spec(
            film,
            scene_text=lambda i: scenes[i].get("text", "") if i < len(scenes) else "",
            scene_start=lambda i: scenes[i].get("start", 0.0) if i < len(scenes) else 0.0,
            duration=duration,
        )
    for finding in report.findings:
        click.echo(finding)
    if report.ok:
        order = " then ".join(f"{n} at {report.beats[n].start:.1f}s" for n in pitch_mod.BEATS)
        click.echo(f"problem, solution, secret sauce: {order}")
    raise SystemExit(0 if report.ok else 1)


@main.command()
@click.argument("spec_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--from", "first", default="en", help="The language that was written first.")
@click.option("--to", "second", default="fr", help="The language to judge against it.")
def calque(spec_path: str, first: str, second: str) -> None:
    """Report a second-language cut that reads as a translation of the first.

    A film shot in two languages is two films, and the failure is quiet: every
    line is grammatical, every fact is right, and the second cut sounds like a
    translation because it is one. A reviewer reading a diff of two languages
    sees two columns of unrelated words and cannot tell.

    What is measured is correspondence, never meaning: the share of positions
    where the two cuts hold the same number of sentences and the same numerals
    in the same order. Two scripts written separately do not line up that way.

    A suspicion, not a verdict — it names the positions so the two cuts can be
    read side by side.
    """
    from sprezzature_video import calque as calque_mod
    from sprezzature_video import spec as spec_mod

    film = spec_mod.load(spec_path)
    report = calque_mod.compare_spec(film, languages=(first, second))
    for line in report.report():
        click.echo(line)
    if not report.suspected:
        click.echo(
            f"{film.name}: the {second} cut scores {report.score:.2f} against "
            f"the {first} one, under {calque_mod.CALQUE_SCORE:.2f} — written "
            f"rather than rendered"
        )
    raise SystemExit(1 if report.suspected else 0)


if __name__ == "__main__":
    main()
