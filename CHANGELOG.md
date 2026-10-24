# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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

### Notes
- Not yet released to PyPI. The renderer seam, the YAML spec loader and the
  five surfaces (argparse CLI, Click CLI, HTTP API, MCP, skill) are not here
  yet; `[project.scripts]` is declared ahead of them and will not resolve until
  those modules exist.
