# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.4.5] — 2026-11-08

### Fixed

- **`scan` read nothing of a real document.** `<meta>` is a void element, the
  parser counted it as opened and never closed, and `</head>` then left the
  whole body suppressed. Every composition with a `<meta charset>` came back
  with no visible text, "0 undeclared number(s)" and exit 0; only head-less
  fragments, which is what the tests fed it, were read. `meta` is out of the
  suppressed set, and `<body>` now clears whatever an omitted `</head>` left
  open.
- **`scan` glued distinct numbers together.** "10, 20, 30" was one number,
  "Since 2026, 167 charts" was 2026167 and neither `--ignore` nor a claim
  could account for it, and two neighbouring elements were one number. One
  separator between groups now, a space only before exactly three digits, and
  each text node is read alone.
- **`scan` accounted for a number by substring.** A 16 on screen passed on a
  claim reading "167 kinds". Numbers are compared whole. A number shown twice
  now reports each place, not the first one twice.
- **`verify` raised instead of giving a verdict** on a selector that does not
  compile, a `json_key_len` over a scalar and a source path that became a
  directory: a traceback on the command line, a 500 over HTTP.
- **A wrong call exited 1**, the code for a film that fails its check. A spec
  that does not load, `pitch --voice` on an absent language, a caption line
  with no timing or a missing audio file, and a file ffmpeg refuses are exit 2
  with one line.
- `/v1/scan` and `/v1/verify` answer 400 instead of 500 on a claim whose
  `source` lacks `path` or `method`.
- The MCP server announced a sentence as its version: fastapi-mcp 0.4 passes
  the description into the `version` slot of `Server`. `serverInfo.version` is
  the package version again, and the description is in `instructions`.

### Docs

- EXAMPLES, README and LISEZMOI: the worked claim said 167 kinds against a
  catalogue that now holds 168, so the documented `verify` printed a failure.
  The sample output of `verify` and `assets` is the real one-line form.
- README and LISEZMOI list what exit 2 covers.

## [0.4.4] — 2026-11-07

### Fixed

- **`calque` on a spec without the asked cut is a usage error.** It died
  on a `KeyError` traceback with exit 1, the code that means "reads as a
  translation"; it now says which narration is missing and exits 2.

## [0.4.3] — 2026-11-05

### Docs

- README / LISEZMOI: `captions` needs ffprobe (from the `ffmpeg` install)
  when a narration line names an audio file rather than a duration; the
  measurement goes through `audio_helper.get_audio_duration`, which probes
  the file.
- README / LISEZMOI: the status section no longer pins a version or a test
  count, both wrong by the next release (it said 125 tests while the suite
  collected 127).
- `captions` no longer tells a reader to install a `voice` extra that was
  folded back into the base on 2026-11-01, and `normalize_loudness` no longer
  calls itself the one direct ffmpeg call.

## [0.4.2] — 2026-11-05

### Changed

- The front door `sprezzature-video` (and `make-film`) answers `-V` as well
  as `--version`, like the other bricks' commands; it was a usage error.
  `tests/test_the_front_door_answers_both_version_flags.py` holds both flags
  against the installed version, and the surface table in `TRIGGERS.md`
  names both.

## [0.4.1] — 2026-11-05

### Removed

- `playwright` is no longer a base dependency. Nothing in the package, its
  tests or its scripts imports it; it was declared for a renderer seam that
  does not exist.

### Fixed

- `poster` without `ffmpeg` on `PATH` printed a `FileNotFoundError`
  traceback, which read as a bug in this package. It now exits 2 with one
  line naming ffmpeg, before anything runs. Tested with `shutil.which`
  patched out, and checked to fail on the old code.

### Docs

- `api.py`, README / LISEZMOI and EXAMPLES: `uvicorn sprezzature_video.api:app`
  serves the HTTP routes only and answers 404 on `/mcp`; the routes and `/mcp`
  together need `sprezzature-video-mcp`. The exit-2 notes name the missing
  ffmpeg. Playwright is gone from the install lists (README, LISEZMOI,
  CONTRIBUTING).

- README / LISEZMOI: the status still said 0.3.0 and 118 tests; it is 0.4.0
  and 125 with the poster test above. `[dev]` also carries httpx2, now
  named with httpx (CONTRIBUTING too).
- LISEZMOI / PAYSAGE: non-breaking spaces before `:` `;` `?` `!` and inside
  guillemets, outside code.
- LANDSCAPE / PAYSAGE: "the highest return of the eight" counted the ideas
  before Claude Motion joined them; there are nine. The package does not
  drive a renderer, so it no longer says it is happy to.
- `pyproject.toml` description: "one spec drives landscape, portrait and
  square on a single time grid" described a renderer this package does not
  have.
- `mypy.ini` and the CI header: a three-version matrix, an `[api]` extra, a
  renderer seam needing playwright and a `scripts/` check, none of which
  exist any more.

## [0.4.0] - 2026-11-04: three surface defects, click everywhere

### Changed

- `sprezzature-video-mcp` parses its arguments with click instead of argparse.
  `--host`, `--port`, their defaults, `SPREZZATURE_VIDEO_HOST` and
  `SPREZZATURE_VIDEO_PORT` are unchanged; a usage error still exits 2.
  `main(argv)` returns an `int` now. No module of the package imports argparse.
- The Docker image and the compose service run `sprezzature-video-mcp` on
  `0.0.0.0:8000` instead of `uvicorn sprezzature_video.api:app`. The bare app
  never imported `sprezzature_video.mcp`, so the container answered 404 on
  `/mcp`; one container now serves `/v1/...`, `/health` and `/mcp`.
- A guard test runs every console script with `--help` and expects exit 0 and
  a click usage line, and fails if any module of the package imports argparse.

### Fixed

- `/health` and the OpenAPI document reported version 0.2.0 throughout 0.3.0:
  the FastAPI app carried a literal. It reads `__version__` now.
- `pitch` labelled every finding "film", because `from_spec` read a `key`
  attribute `FilmSpec` does not have. Findings carry the spec's `name` now.
- `scan --spec` had no help string.
- Stale comments in the Dockerfile, the CI workflow, `pyproject.toml` and
  `.githooks/pre-push` still described the extras and a three-version matrix.

Each of the three code fixes has a regression test in
`test_every_surface_answers.py`, checked to fail on the old code.

### Docs

The documentation was checked against the code and corrected where it had
drifted.

- README / LISEZMOI: the install section listed a second `pip install` line
  for "narration and ffmpeg work", which is the same command since the extras
  were folded in; it is one line now. The status said 94 tests and CI on
  3.10/3.11/3.12: the suite collected 115 tests (118 with the fixes above),
  and CI runs on 3.12 with a 3.10 install-and-import floor job. The `pitch` example showed a message the
  code does not print; it shows the real one. Added what was missing: the five
  surfaces, the eight commands with their exit codes, the five routes with
  their MCP tool names, the film spec format, the claim methods, and the
  `pitch`, `charter` and `spec` modules. LISEZMOI gained the `prose` section
  it lacked and French typography.
- TRIGGERS: captions were said to be written by `sprezzature-audio`'s VTT
  module; they are written by `video_helper.subtitles`. Added a table of every
  tool and the request it answers, a table of what to call on every surface,
  and the `pitch`, `calque`, `prose`, `poster` and `list_methods` tools, which
  were absent.
- EXAMPLES: the asset report listed `diverged` before `missing`; the code
  prints `missing` first. Added the narration section captions need, the MCP
  surface, Docker compose, and the pitch, calque and prose commands.
- BOUNDARIES: the WebVTT writer is in `video-helper` since 2026-10-31, not in
  `sprezzature-audio`; the `narrate` extra it quoted no longer exists; the
  `StopIteration` from `video_helper.video_duration` was fixed in video-helper
  2.8.0; `post.poster` and `post.measured_loudness` call ffmpeg directly too,
  so `normalize_loudness` is not the only one.
- CONTRIBUTING: the `[voice]`, `[post]` and `[local]` extras no longer exist,
  and the "three" gates were four.
- CODING: `sprezzature_audio` is imported nowhere in this package; the
  direct-ffmpeg exception covers three functions, not one.
- LANDSCAPE / PAYSAGE: the WebVTT writer moved to `video-helper`; the WhisperX
  refusal rested on torch being absent, and torch now arrives through
  `sprezzature-audio`.
- Docstrings: `__init__` named a `sprezzature_video.renderers` module that does
  not exist; `mcp` still spoke of an MCP extra; `post` called loudness the
  single direct ffmpeg call.

### Changed — one `pip install`

**Everything this package does now installs with it.** 6 extras became
**one**, and it is not a feature: `[dev]` is the test toolchain.

  The voice (`sprezzature-audio`), the post-production helper, the headless
  browser for local rendering, and both surfaces.

Measured across the suite before touching anything: **59 extras over eleven
repositories**, and **six bricks whose base was a single dependency** — so
`pip install <brick>` installed almost nothing and did almost nothing, and
choosing the right extra was a thing a reader had to know *before* the package
could do its job. Here the base goes from **4** to **11**
dependencies.

All eleven unions were dry-run resolved in a clean venv before any manifest was
edited, so this is a measured feasibility and not an optimistic one.

### Fixed — the places that encoded the extras

Install lines, error messages, docstrings, the `Dockerfile`, the CI workflow and
the README/LISEZMOI install sections all named extras that no longer exist. pip
treats an unknown extra as a **warning and exits 0**, so none of these would
have failed loudly: they would have quietly installed nothing.

The hub's `test_no_document_promises_an_extra_that_does_not_exist` found the
cross-repository ones — a document in one brick naming another brick's extra —
which no per-repository pass would have caught.

### Changed

- **Captions are written by `video_helper.subtitles` now**, not by
  `sprezzature-audio`. The suite's single timed-text module moved to the
  package that burns subtitles into frames and converts between the formats,
  and this package follows it: the writer is the same writer, verified
  identical on real tracks before anything was rewired, so no caption file
  changes by a byte.

  The consequence worth noting is the dependency, not the import:
  `sprezzature-audio` leaves the **base** install, because a subtitle format
  was the only thing the base used it for. The voice still comes from there
  through the `voice` extra, where it belongs, and `video-helper` takes its
  place in the base with a floor of 2.9.0.

  SubRip also comes free with the move. A film's captions can now reach the
  platforms that refuse WebVTT, which is most of them, through
  `video_helper.vtt2srt`.

### Changed
- `captions` breaks a caption at **42 characters instead of 58**, and breaks it
  as many times as it takes instead of once. 42 is the Netflix Timed Text Style
  Guide figure `sprezzature-audio` already audits against and the suite's own
  `audio` film puts on screen as a declared claim; 58 was inherited verbatim
  from the 707-line script this module generalises, where it had no source.
  Every caption written between 43 and 58 characters satisfied this package's
  rule and failed the audit that judges it.
  One cut was the larger half of the defect: `split_line` cuts once, so a
  158-character line halved into two 79-character captions and the limit read
  as satisfied because the function that applied it had returned. Measured on
  the eleven films' 218 narration lines, cutting once at 58 left 41 % of the
  cues over the 42-character budget with the longest at 117; cutting at 42
  until the pieces fit gives 558 cues, none over budget, the longest exactly
  42. `split_to_fit` is the new public function; `split_line` is unchanged and
  still cuts once.
  A piece with no break left is emitted whole rather than truncated or recursed
  on forever, because an over-wide line is something the audit names and a hang
  is not.

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
