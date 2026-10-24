# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
