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

__version__ = "0.1.0"

__all__ = [
    "Asset",
    "AssetLedger",
    "AssetVerdict",
    "Claim",
    "ClaimReport",
    "ClaimSource",
    "UndeclaredNumber",
    "Provenance",
    "Spoken",
    "State",
    "Verdict",
    "__version__",
    "as_claim",
    "numbers_in",
    "measure",
    "read_actual",
    "split_line",
    "to_cues",
    "undeclared_numbers",
    "verify",
    "verify_all",
    "visible_text",
]
