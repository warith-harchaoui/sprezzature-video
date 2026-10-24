#!/usr/bin/env python3
"""
make-film — check what a film says against the project it describes.

Five subcommands, each one half of a question a film cannot answer about
itself:

``verify``
    Do the film's declared claims still match the code?
``scan``
    Is every number visible in a composition a declared claim?
``assets``
    Could this film be rendered again from a clone?
``captions``
    WebVTT from the narration script and the measured audio.
``poster``
    A frame of a rendered film, for the idle image.

Exit codes are the point of ``verify``, ``scan`` and ``assets``: 0 when the
film is still honest, 1 when it is not. That is what makes them usable as a
gate rather than as a report somebody reads when they remember to.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sprezzature_video import assets as assets_mod
from sprezzature_video import captions as captions_mod
from sprezzature_video import claims as claims_mod
from sprezzature_video import spec as spec_mod


def build_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser.

    Returns
    -------
    argparse.ArgumentParser
        ``prog`` is the installed command name, not the module path: a help
        screen that announces ``__main__.py`` tells the reader nothing they can
        type.
    """
    parser = argparse.ArgumentParser(
        prog="make-film",
        description="Check what a film says against the project it describes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_verify = sub.add_parser("verify", help="Verify a film's declared claims against the code.")
    p_verify.add_argument("spec", help="Film spec (.yaml).")
    p_verify.add_argument("--root", default=".", help="Directory claim sources are relative to.")

    p_scan = sub.add_parser("scan", help="Find numbers on screen that no claim accounts for.")
    p_scan.add_argument("composition", help="The composition's index.html.")
    p_scan.add_argument("--spec", help="Film spec (.yaml) holding the declared claims.")
    p_scan.add_argument(
        "--ignore",
        default="",
        help="Comma-separated values that are on screen without being claims (a year, a version).",
    )

    p_assets = sub.add_parser("assets", help="Audit the asset tree a film renders from.")
    p_assets.add_argument("spec", help="Film spec (.yaml).")
    p_assets.add_argument("--tree", required=True, help="The asset tree.")
    p_assets.add_argument("--repo", default=".", help="Root that tracked sources are relative to.")
    p_assets.add_argument(
        "--restore",
        action="store_true",
        help="Copy back tracked assets that are simply absent. Never touches a divergence.",
    )

    p_cap = sub.add_parser("captions", help="Write WebVTT from the narration script.")
    p_cap.add_argument("spec", help="Film spec (.yaml).")
    p_cap.add_argument("--lang", required=True, help="Language key in the spec's narration map.")
    p_cap.add_argument("--out", help="Output .vtt. Default: stdout.")
    p_cap.add_argument(
        "--translated",
        action="store_true",
        help="Omit voice tags: W3C reserves them for the audio's own language.",
    )

    p_poster = sub.add_parser("poster", help="Extract a frame of a rendered film as JPEG.")
    p_poster.add_argument("video", help="The rendered film.")
    p_poster.add_argument("--out", required=True, help="Output .jpg.")
    p_poster.add_argument(
        "--at",
        type=float,
        required=True,
        help="Time of the frame in seconds. Not 0.0 on a film that fades in.",
    )

    return parser


def _verify(args: argparse.Namespace) -> int:
    film = spec_mod.load(args.spec)
    if not film.claims:
        # An empty claim list passing silently is the failure this package
        # exists to prevent: it reads exactly like a film that checks out.
        print(f"{args.spec}: no claims declared — nothing was checked", file=sys.stderr)
        return 1
    verdicts = claims_mod.verify_all(film.claims, args.root)
    for verdict in verdicts:
        mark = "ok  " if verdict.ok else "FAIL"
        print(f"{mark} {verdict.detail}")
    bad = [v for v in verdicts if not v.ok]
    print(f"\n{len(verdicts) - len(bad)}/{len(verdicts)} claims hold")
    return 1 if bad else 0


def _scan(args: argparse.Namespace) -> int:
    declared = spec_mod.load(args.spec).claims if args.spec else []
    ignore = frozenset(
        int(piece) for piece in (p.strip() for p in args.ignore.split(",")) if piece.isdigit()
    )
    html = Path(args.composition).read_text(encoding="utf-8")
    found = claims_mod.undeclared_numbers(html, declared, ignore=ignore)
    for item in found:
        print(f"UNDECLARED {item.written!r} in {item.context!r}")
    print(f"\n{len(found)} undeclared number(s) on screen")
    return 1 if found else 0


def _assets(args: argparse.Namespace) -> int:
    film = spec_mod.load(args.spec)
    if args.restore:
        for line in film.ledger.restore(args.tree, args.repo):
            print(line)
    verdicts = film.ledger.audit(args.tree, args.repo)
    lines = assets_mod.report(verdicts)
    for line in lines:
        print(line)
    held = sum(1 for v in verdicts if v.ok)
    print(f"\n{held}/{len(verdicts)} assets in hand")
    return 1 if held != len(verdicts) else 0


def _captions(args: argparse.Namespace) -> int:
    film = spec_mod.load(args.spec)
    if args.lang not in film.narration:
        known = ", ".join(sorted(film.narration)) or "none"
        print(f"no narration for {args.lang!r}; the spec has: {known}", file=sys.stderr)
        return 1
    body = captions_mod.write(film.narration[args.lang], translated=args.translated)
    if args.out:
        Path(args.out).write_text(body, encoding="utf-8")
        print(args.out)
    else:
        print(body)
    return 0


def _poster(args: argparse.Namespace) -> int:
    from sprezzature_video import post

    print(post.poster(args.video, args.out, at=args.at))
    return 0


def main(argv: list[str] | None = None) -> int:
    """
    Run the command line.

    Parameters
    ----------
    argv : list[str] or None
        Arguments, defaulting to ``sys.argv[1:]``.

    Returns
    -------
    int
        0 when the film is still honest, 1 when it is not, 2 on a usage or
        input error.
    """
    args = build_parser().parse_args(argv)
    handlers = {
        "verify": _verify,
        "scan": _scan,
        "assets": _assets,
        "captions": _captions,
        "poster": _poster,
    }
    try:
        return handlers[args.command](args)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        # A missing spec or a malformed one is the caller's problem to fix, and
        # a traceback buries the one line that says which. 2 keeps it distinct
        # from "the film is wrong", which is what 1 means here.
        print(f"make-film: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
