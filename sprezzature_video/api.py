#!/usr/bin/env python3
"""
sprezzature-video: the FastAPI HTTP surface.

Module summary
--------------
Exposes the claim checker, the undeclared-number scan and the caption builder
over HTTP, so a CI job, an editor plugin or a build step in any language can
ask whether a film still tells the truth without shelling out to Python. Every
route calls the same library functions the command line calls, so the HTTP
answer and the terminal answer cannot disagree.

What ships here
---------------
- ``GET  /health``: a liveness probe.
- ``GET  /v1/methods``: the ways a claim's truth can be read out of the code.
- ``POST /v1/scan``: given a composition's HTML and the declared claims,
  return the numbers on screen that no claim accounts for.
- ``POST /v1/captions``: given narration lines, return a WebVTT document.
- ``POST /v1/verify``: given declared claims and a server-side root, check
  each one against the code.

What this can and cannot tell you
---------------------------------
``/v1/scan`` and ``/v1/captions`` are pure: everything they need arrives in the
request body. ``/v1/verify`` is not, and the difference matters — it reads
files under a root **on the server**, because a claim is only meaningful
against the repository it describes. Point it at a checkout the server can
see, or run the CLI where the code is.

Nothing here renders. Rendering needs a browser and tens of seconds; it lives
behind the renderer seam, not behind an HTTP request.

Install the extra to get the runtime dependencies::

    pip install 'sprezzature-video[api]'

Then run the app with any ASGI server::

    uvicorn sprezzature_video.api:app --host 0.0.0.0 --port 8000

Usage example
-------------
>>> # curl -X POST localhost:8000/v1/scan \\
>>> #      -H 'content-type: application/json' \\
>>> #      -d '{"html": "<p>167 kinds, 960 tests</p>", "claims": []}'
>>> # Full OpenAPI docs at http://localhost:8000/docs

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import RedirectResponse
except ImportError as exc:  # pragma: no cover - dependency guard
    raise ImportError(
        "The FastAPI HTTP surface requires the [api] extra. "
        "Install with: pip install 'sprezzature-video[api]'"
    ) from exc

from pydantic import BaseModel, Field

from sprezzature_video import captions as captions_mod
from sprezzature_video import claims as claims_mod

app = FastAPI(
    title="sprezzature-video",
    version="0.2.0",
    description=(
        "Check what a film says against the project it describes: verify declared "
        "claims, find numbers on screen that no claim accounts for, and build "
        "WebVTT from a narration script."
    ),
)


class ClaimIn(BaseModel):
    """One declared claim, in the shape the YAML spec uses."""

    text: str = Field(..., description="The assertion exactly as it appears on screen.")
    value: int | str = Field(..., description="The asserted value: a count, or a quoted phrase.")
    source: dict[str, str] = Field(
        ...,
        description="Where its truth is read: path, method, and optionally selector.",
    )


class ScanIn(BaseModel):
    """A composition's markup and the claims that should account for its numbers."""

    html: str = Field(..., description="The composition's HTML.")
    claims: list[ClaimIn] = Field(default_factory=list, description="The declared claims.")
    ignore: list[int] = Field(
        default_factory=list,
        description="Values legitimately on screen without being claims (a year, a version).",
    )


class VerifyIn(BaseModel):
    """Claims to check, and the server-side root their sources are relative to."""

    claims: list[ClaimIn] = Field(..., description="The declared claims.")
    root: str = Field(..., description="Directory on the SERVER that claim paths resolve against.")


class LineIn(BaseModel):
    """One narration line. Either ``audio`` or ``duration`` must be given."""

    start: float = Field(..., description="Start time in the film, in seconds.")
    text: str = Field(..., description="The line, as it was given to the voice.")
    audio: str | None = Field(None, description="Server-side path to the synthesized file.")
    duration: float | None = Field(None, description="Length in seconds, when there is no audio.")


class CaptionsIn(BaseModel):
    """Narration lines for one language of one film."""

    lines: list[LineIn] = Field(..., description="The narration lines, in order.")
    translated: bool = Field(
        False,
        description="True for a track in a different language from the audio: voice tags are omitted.",
    )


@app.get(
    "/health",
    tags=["meta"],
    operation_id="health",
    summary="Check that this film-checking server is up",
)
def health() -> dict[str, str]:
    """Liveness probe. Returns the package name and version."""
    return {"status": "ok", "service": "sprezzature-video", "version": app.version}


@app.get(
    "/v1/methods",
    tags=["meta"],
    operation_id="list_methods",
    summary="List the ways a claim's truth can be read from the code",
)
def list_methods() -> dict[str, Any]:
    """Describe each claim-source method and what it reads."""
    return {
        "methods": {
            "json_len": "length of a top-level JSON array",
            "json_key_len": "length of the value at `selector` in a JSON object",
            "regex_count": "number of matches of `selector` in the file",
            "line_count": "number of non-blank lines",
            "literal": "the file contains `selector` verbatim",
        }
    }


@app.post(
    "/v1/scan",
    tags=["actions"],
    operation_id="scan_composition",
    summary="Find numbers on screen that no claim accounts for",
)
def scan_composition(body: ScanIn) -> dict[str, Any]:
    """
    Read a composition's visible text and report unaccounted numbers.

    Pure: everything needed is in the request. Stylesheet and script contents
    are excluded, because a keyframe percentage is not a claim about a project.
    """
    declared = [claims_mod.as_claim(c.model_dump()) for c in body.claims]
    found = claims_mod.undeclared_numbers(body.html, declared, ignore=frozenset(body.ignore))
    return {
        "undeclared": [{"written": u.written, "context": u.context} for u in found],
        "count": len(found),
        "ok": not found,
    }


@app.post(
    "/v1/verify",
    tags=["actions"],
    operation_id="verify_claims",
    summary="Verify declared claims against the code on this server",
)
def verify_claims(body: VerifyIn) -> dict[str, Any]:
    """
    Check each claim against files under *root*, on this server.

    Raises
    ------
    HTTPException
        400 when no claims are supplied. An empty list would otherwise return
        "all claims hold", which reads exactly like a film that checks out.
    """
    if not body.claims:
        raise HTTPException(status_code=400, detail="no claims supplied — nothing would be checked")
    declared = [claims_mod.as_claim(c.model_dump()) for c in body.claims]
    verdicts = claims_mod.verify_all(declared, body.root)
    return {
        "verdicts": [
            {"text": v.claim.text, "ok": v.ok, "actual": v.actual, "detail": v.detail}
            for v in verdicts
        ],
        "held": sum(1 for v in verdicts if v.ok),
        "total": len(verdicts),
        "ok": all(v.ok for v in verdicts),
    }


@app.post(
    "/v1/captions",
    tags=["actions"],
    operation_id="build_captions",
    summary="Build a WebVTT track from narration lines",
)
def build_captions(body: CaptionsIn) -> dict[str, str]:
    """
    Return a WebVTT document for one language of one film.

    Raises
    ------
    HTTPException
        400 when a line has neither audio nor an explicit duration: its timing
        is unknown, and a zero-length cue is never painted.
    """
    from pathlib import Path

    lines = [
        captions_mod.Spoken(
            start=line.start,
            text=line.text,
            audio=Path(line.audio) if line.audio else None,
            duration=line.duration,
        )
        for line in body.lines
    ]
    try:
        return {"vtt": captions_mod.write(lines, translated=body.translated)}
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/docs-redirect", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    """Send a bare visitor to the interactive documentation."""
    return RedirectResponse(url="/docs")
