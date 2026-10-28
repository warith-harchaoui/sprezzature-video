# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.3.0] - 2026-10-28

Three things a film has that nobody was reading: where its lines land, what it
says out loud, and whether its second language was written or only translated.

### Added
- `timeline` — `lay_out` places each narration line at the later of the scene
  it was written for and the moment the line in front of it stops. A requested
  start is a preference; an overrun pushes the next line and is *reported*
  rather than refused. The one hard failure left is a script too long for its
  film, measured in seconds and quoted in characters of the track that was
  actually spoken. Written because `speaker-helper` 0.13 sent offline
  narration to chatterbox, which samples: the same French sentence measured
  7.520, 6.760 and 6.640 seconds on three runs, so a hand-typed grid is wrong
  for the next run at random. The refusal it replaces is what left fourteen
  cuts out of twenty-two carrying a voice older than their script for days —
  the build neither broke nor advanced.
- `calque` — whether a film's second language reads as a rendering of its
  first. Meaning is never inspected; *correspondence* is: the share of
  positions where the two cuts hold the same number of sentences and the same
  numerals in the same order. Two scripts composed separately distribute their
  material differently. The threshold is calibrated against both sides — a set
  of eleven known-translated cuts scored 0.75 to 0.89, the same eleven
  rewritten scored 0.36 to 0.70 — and it caught two of the "rewritten" ones at
  0.91 and 0.80, correctly. Reachable as `sprezzature-video calque`.
- `pitch.from_narration` — Kawasaki's three beats read in the **voice** rather
  than in the frame. A sixty-second film puts one sentence a scene on screen
  and speaks eight, so most of what a viewer receives was going unchecked. A
  line takes the beat of the scene on screen when it starts, so there is one
  declaration and not two. Reachable as `sprezzature-video pitch --voice <lang>`.

### Fixed
- `regex_count` called `re.findall` with no flags, so a selector anchored on
  `^` matched only at the start of the file and returned 0. That arrives at
  `verify` as "the film says 20, the code says 0" — the exact sentence a
  genuinely stale claim produces — and sends a reader to re-cut a frame that
  was right. Now `re.MULTILINE`, and a selector matching nothing raises
  instead of reporting a count of zero.
- The feature-list check knew no teens and no compound tens, so "Seventeen
  characters a second. Forty-two to a line." — the most inventory-shaped
  sentence in the suite's own films — went through untouched. The count
  vocabulary now holds one through nineteen, the tens and their compounds, in
  both languages.
- A magic beat is now reported as a feature list by **share** rather than by
  presence: an inventory has to cover half the beat. A beat that quotes its
  published numbers and then says the thing worth saying about them is not an
  inventory, and reporting it as one teaches a reader to ignore the check.
  Brochure verbs (`supports`, `includes`, `propose`) stay an immediate finding,
  because that is a register and not a proportion.
- `cli` opened by describing itself as "the Click twin" of an argparse entry
  point that stopped existing on 2026-10-25, when Click became a base
  dependency across the suite.

## [0.2.0] - 2026-10-24

### Added
- `claims` — a claim is a declared pair (the text on screen, the place in the
  code that decides whether it is true), checked in both directions:
  `verify_all` for declared claims, `undeclared_numbers` for every number
  visible on screen that no claim accounts for.
- `assets` — the three-class provenance ledger (`TRACKED` / `DERIVED` /
  `SOLE`) that answers whether a film can be rendered again from a clone.
  A divergence between a copy and its tracked source is reported and
  **never silently repaired**.
- `captions` — WebVTT from the narration script and the **measured** length of
  each audio file, written through the suite's single VTT module.
- `post` — poster baked as frame 0 (feeds regenerate thumbnails from the first
  frame server-side), and loudness normalisation across a series.
- `BOUNDARIES.md` — which package owns what between this suite and ai-helpers.
- `LANDSCAPE.md` / `PAYSAGE.md` — the competitive position, with the
  positioning map produced by `standpoint`.

- `spec` — a film as a reviewable YAML file: its claims, its assets and its
  narration. The three things that go stale, out of a generator and into a
  file a reviewer can diff.
- **The five surfaces.** `make-film` (argparse), `sprezzature-video` (Click),
  a FastAPI HTTP API, MCP tools mounted on that same app, and a skill. Plus a
  Dockerfile and a compose file, and `TRIGGERS.md` for routing.

### Fixed
- `[project.scripts]` named `cli`, `cli_click` and `mcp` before those modules
  existed, so 0.1.0 put three commands on PATH that died with
  `ModuleNotFoundError`. They return here with their modules.
- `packages` declared `sprezzature_video.renderers` and a `scripts` package as
  empty directories, which git does not carry — the first CI run failed with
  "package directory does not exist".
- `os-helper` was imported by name but only inherited transitively.

### Notes
- mypy runs at `python_version = 3.12`, not 3.10: numpy >= 2.3 writes its stubs
  with PEP 695 `type` statements that mypy only accepts from 3.12, and numpy
  arrives through pydantic's type graph as soon as `api.py` is checked. The
  3.10 floor is covered by the CI matrix actually running on 3.10.
- The renderer seam is still not here. Hyperframes is driven out of band; the
  `renderers/` package returns in the commit that gives it a module.
