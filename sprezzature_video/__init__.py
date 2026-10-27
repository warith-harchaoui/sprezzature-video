"""
sprezzature-video — project launch films, with the claims checked.

The package is organised around the one thing a film has that a README does
not: assertions burned into pixels, where nothing reads them again. So the
entry point is not a renderer. It is :mod:`sprezzature_video.claims`, and the
renderer sits behind a seam (:mod:`sprezzature_video.renderers`) precisely
because which tool draws the frames is the least interesting decision here.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from sprezzature_video.assets import (
    Asset,
    AssetLedger,
    AssetVerdict,
    Provenance,
    State,
)
from sprezzature_video.captions import Spoken, measure, split_line, to_cues

# `measure_prose`, not `measure`: `captions.measure` already owns that name
# in this namespace, and exporting both replaced the captions one silently.
# The symptom was an unrelated caption test failing with a TypeError about
# a PosixPath, which is the shape a shadowed function always takes.
from sprezzature_video.charter import Finding, check_line
from sprezzature_video.charter import measure as measure_prose
from sprezzature_video.claims import (
    Claim,
    ClaimReport,
    ClaimSource,
    UndeclaredNumber,
    Verdict,
    as_claim,
    numbers_in,
    read_actual,
    undeclared_numbers,
    verify,
    verify_all,
    visible_text,
)
from sprezzature_video.pitch import Beat, PitchReport
from sprezzature_video.pitch import check as check_pitch
from sprezzature_video.spec import FilmSpec, load

__version__ = "0.2.0"

__all__ = [
    "Asset",
    "Beat",
    "Finding",
    "PitchReport",
    "AssetLedger",
    "AssetVerdict",
    "Claim",
    "FilmSpec",
    "ClaimReport",
    "ClaimSource",
    "UndeclaredNumber",
    "Provenance",
    "Spoken",
    "State",
    "Verdict",
    "__version__",
    "as_claim",
    "check_line",
    "check_pitch",
    "measure",
    "measure_prose",
    "load",
    "numbers_in",
    "read_actual",
    "split_line",
    "to_cues",
    "undeclared_numbers",
    "verify",
    "verify_all",
    "visible_text",
]
