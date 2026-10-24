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
    "Claim",
    "ClaimReport",
    "ClaimSource",
    "UndeclaredNumber",
    "Verdict",
    "__version__",
    "as_claim",
    "numbers_in",
    "read_actual",
    "undeclared_numbers",
    "verify",
    "verify_all",
    "visible_text",
]
