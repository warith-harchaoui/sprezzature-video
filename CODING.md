# Coding standards

The same standards as the other nine sprezzature packages, stated for this one
rather than copied from a sibling — a copied file carries the sibling's history
as if it were ours, and every comment in those files records a defect that
happened *there*.

## Language

Python 3.10+. Full type annotations on every public function and class.

## Style

- `ruff check` with zero warnings; `ruff format` applied.
- Line length 100 (`[tool.ruff]` in `pyproject.toml`).
- Imports: standard library, third party, then local, each group separated by a
  blank line.

## Docstrings

NumPy style on all public functions and classes: a short summary line, then
Parameters, Returns, Raises and Examples as needed. A `Raises` section is not
optional when the function can fail — in this package several failures are the
*point* (a claim whose source has moved, a narration file that is absent), and
a caller who does not know they can happen will write a guard that goes quiet.

## Comments

Roughly a quarter to a third of lines. Each should explain *why* the code does
something non-obvious, never restate what the code already says. No
commented-out code.

Specific to this package: when a comment records a defect, name the defect.
"Both forms are listed" says nothing; "the class first held only U+00A0 and so
could never match, because `visible_text` collapses runs of `\s`" tells the
next reader why they must not tidy it.

## Lazy imports

The heavier dependencies — `audio_helper`, `video_helper`, `sprezzature_audio`
— are imported **inside** the functions that use them, not at module top level.
Two reasons, both real: the audit is useful on a machine that has a film's
asset tree but not the full toolchain, and `import audio_helper` costs over a
second that a caller who only wants `claims` should not pay.

## What this package does not do

It does not render, synthesize speech, or call ffmpeg for anything
`video-helper` already covers. Those belong to packages named in
[BOUNDARIES.md](BOUNDARIES.md). The one deliberate exception is loudness
normalisation, which has no primitive upstream yet; it is marked as such in
`post.py` and should become a call outward if one lands.

## Tests

Named as sentences about the property they protect. Two habits:

1. **Sabotage what you claim to protect.** Break the condition on purpose,
   watch the test fail, restore it. A guard that has never failed is not known
   to work.
2. **Check where a new measure puts the known-good case.** A check that passes
   immediately and quietly may be unable to fail at all.
