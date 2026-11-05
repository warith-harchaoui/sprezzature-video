# sprezzature-video

[🇫🇷 LISEZMOI.md](https://github.com/warith-harchaoui/sprezzature-video/blob/main/LISEZMOI.md) · 🇬🇧 README.md

A film about a project makes **claims** about that project: how many chart
kinds, how many tests, how many packages. It burns them into pixels, where
nothing ever reads them again. Prose in a README gets re-read. A number in a
keyframe does not.

So this package is not a renderer. Its centre is a checker that holds a film's
assertions against the code they describe, in both directions. Rendering stays
outside the package, because which tool grabs the frames is the least
interesting decision here.

Part of the [sprezzature](https://sprezzature.ai/) suite.

---

## How it works

![Flow diagram. At the top, a film specification and the code it describes feed two lanes. The left lane checks the numbers: every declared claim against the place in the code that decides it, every number visible on screen against the declarations, and whether the film can be rendered again from a clone. The right lane checks the telling: the pitch in Kawasaki's order, and the mechanical half of the writing charter. Both meet in one outcome, the parts of a film a function can own, captions from measured audio, the poster baked as frame zero, and loudness levelled across a series.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-video/main/assets/how-it-works.svg)

## Why it exists

The five films that served on sprezzature.ai said **"127 chart kinds"**. The
catalogue had held 167 since September. The number was baked into ten
compositions and five rendered MP4s, so nothing short of a re-cut could correct
it, and nothing anywhere was watching. That is this package's whole subject.

## Install

```bash
pip install sprezzature-video
```

One install, every surface. FastAPI, uvicorn, the MCP server,
`sprezzature-audio`, `audio-helper`, `video-helper` and `os-helper` are base
dependencies. The only extra is `[dev]`, the test toolchain (pytest, ruff,
mypy, httpx and httpx2).

Python 3.10 to 3.13. The `poster` command and the `post` module also need the
`ffmpeg` binary on `PATH`, and so does `captions` when a narration line names
an audio file instead of a duration: it measures the file with ffprobe.

## Five surfaces

The same functions behind five doors.

| Surface | How to reach it |
|---|---|
| Library | `import sprezzature_video` |
| CLI (command-line interface) | `sprezzature-video` or `make-film`: two names for one Click group |
| HTTP API | `uvicorn sprezzature_video.api:app --port 8000` (HTTP routes only, no `/mcp`), or `sprezzature-video-mcp`, or `docker compose up` |
| MCP (Model Context Protocol) server | `sprezzature-video-mcp`, endpoint `/mcp` on the same FastAPI app; the bare `uvicorn` line above does not serve it |
| Skill | `sprezzature-video/SKILL.md`, kept in the [sprezzature](https://github.com/warith-harchaoui/sprezzature) hub |

### Command line

| Command | What it does | Exit 1 when |
|---|---|---|
| `verify SPEC [--root DIR]` | Checks each declared claim against the code. | a claim fails, or the spec declares none |
| `scan COMPOSITION [--spec SPEC] [--ignore 2026,...]` | Lists numbers in the visible text of an HTML composition that no claim accounts for. | a number is unaccounted for |
| `assets SPEC --tree DIR [--repo DIR] [--restore]` | Audits the asset tree. `--restore` first copies back absent tracked files, and nothing else. | an asset is not in hand |
| `captions SPEC --lang LANG [--out FILE] [--translated]` | Writes WebVTT from the spec's narration. `--translated` omits voice tags. | the language is not in the spec |
| `poster VIDEO --out FILE --at SECONDS` | Extracts one frame as JPEG through ffmpeg. | |
| `prose FILE [--lang en\|fr] [--strict]` | Checks each line of a text file against the writing charter. | `--strict` and a hard finding |
| `pitch SPEC --duration SECONDS [--voice LANG]` | Checks the problem, solution and secret sauce beats. | a finding |
| `calque SPEC [--from en] [--to fr]` | Reports a second-language cut that reads as a translation of the first. | the cut is suspected |

Exit 2 is a wrong call: a missing file, a missing required option, or, for
`poster`, no `ffmpeg` on `PATH`. Shell completion and the exit codes are
printed by `sprezzature-video --help`.

### HTTP and MCP

Each route declares an `operation_id`, and that name is the MCP tool name.

| Route | MCP tool | What it does |
|---|---|---|
| `GET /health` | `health` | Liveness probe: status, service name, version. |
| `GET /v1/methods` | `list_methods` | The five ways a claim's truth is read from the code. |
| `POST /v1/scan` | `scan_composition` | Numbers on screen that no claim accounts for. Pure: everything is in the request. |
| `POST /v1/verify` | `verify_claims` | Declared claims against files under a root **on the server**. 400 on an empty claim list. |
| `POST /v1/captions` | `build_captions` | WebVTT from narration lines. 400 when a line has neither audio nor duration. |

The asset audit, the poster, `prose`, `pitch` and `calque` have no route. They
are reached through the CLI or the library.

`sprezzature-video-mcp` binds `127.0.0.1:8000` by default. `--host` and
`--port` override it, as do `SPREZZATURE_VIDEO_HOST` and
`SPREZZATURE_VIDEO_PORT`.

The Docker image installs ffmpeg and runs `sprezzature-video-mcp` on
`0.0.0.0:8000`, so one container serves the HTTP routes and the MCP endpoint
`/mcp` on the same port. The compose file mounts `./work` on `/work`, which is where `/v1/verify` has to find the
repository it checks.

## The film spec

A film is a YAML file. Every section is optional.

```yaml
name: demo                     # defaults to the file's stem
claims:                        # what the film asserts, and where it is checked
  - text: "167 kinds, every one hand-authored."
    value: 167
    source: {path: sprezzature-figures/sprezzature_figures/catalog/figures.json, method: json_len}
assets:                        # what it renders from: tracked, derived or sole
  - {rel: figures/sankey.svg, provenance: tracked, source: web/img/figures/sankey.svg}
  - {rel: music/track.mp3, provenance: sole, why: "licensed track, one copy"}
narration:                     # per language: start, text, and audio or duration
  en:
    - {start: 0.0, text: "A film said 127.", audio: voice/en-01.wav}
scenes:                        # what each scene puts on screen, and when
  - {text: "A film said 127.", start: 0.0}
pitch:                         # beat name to scene indices
  problem: [0]
```

A claim's `method` is one of `json_len` (length of a top-level JSON array),
`json_key_len` (length of the value at `selector`), `regex_count` (matches of
`selector`, multiline), `line_count` (non-blank lines) and `literal` (the file
contains `selector` verbatim). A `regex_count` selector that matches nothing is
an error, not a count of zero. A missing source file fails the claim; it is
never skipped.

A `sole` asset without a `why` is refused at load time. An `audio` path is
resolved against the spec's own directory.

## What's here

| Module | What it owns |
|---|---|
| `claims` | A claim is a declared pair: the text on screen, and the place in the code that decides whether it is true. `verify_all` checks every declared claim still holds; `undeclared_numbers` checks every number *visible* on screen is a declared claim. Text inside `style`, `script`, `template`, `head`, `title` and `meta` is ignored. |
| `assets` | Can this film be rendered again from a clone? Three classes: `TRACKED` (a copy of a tracked file, proved equal to its source by content hash), `DERIVED` (output of a recipe, shown and never run), `SOLE` (exists in exactly one place). Divergence is reported, never silently repaired. |
| `captions` | WebVTT built from the narration script and the **measured** length of each audio file, neither transcribed nor typed. A caption is cut at 42 characters as many times as it takes. The file is written by `video_helper.subtitles`. |
| `post` | `poster` extracts a frame. `bake_poster` makes that still frame 0, because Slack, X and Discord regenerate their thumbnail from the first frame whatever a `poster=` attribute says. `normalize_loudness` and `measured_loudness` level a series to -16 LUFS (loudness units relative to full scale), true peak -1.5 dBTP. |
| `timeline` | `lay_out` places each narration line at the later of the scene it was written for and the moment the line in front of it stops. An overrun pushes and is reported; only a script too long for its film is a failure. |
| `pitch` | Checks the three beats of a pitch, from the scenes or from the narration. |
| `calque` | Whether a film's second language was written or only translated, measured by correspondence. |
| `charter` | The mechanical half of the writing charters, in English and French. |
| `spec` | Loads the YAML spec into a `FilmSpec`. |

### Both directions, and why the second one matters

```python
from sprezzature_video import Claim, ClaimSource, verify, undeclared_numbers

claim = Claim(
    text="167 kinds, every one hand-authored.",
    value=167,
    source=ClaimSource(
        path="sprezzature-figures/sprezzature_figures/catalog/figures.json",
        method="json_len",
    ),
)
verify(claim, root).ok  # does the code still agree?
undeclared_numbers(html, [claim])  # is anything on screen unaccounted for?
```

Checking only declared claims protects the numbers somebody remembered to
declare. It never protects the one typed into a keyframe at midnight and left
to go stale.

## Does the film explain anything?

Three checks that have nothing to do with rendering, and everything to do with
whether a viewer who never heard of your package can say what it is for.

### `pitch`: problem, solution, secret sauce

Guy KAWASAKI's order. State what goes wrong, then what you do about it, then
the one non-obvious thing that makes it possible. The third beat is the one
people get wrong: the underlying magic is an insight, in plain language, that
a competitor does not have. A feature list is not it, and neither is a demo.

The beats are declared in the spec by scene index, so the check runs against
the film that exists rather than a description of it that can drift:

```yaml
pitch:
  problem:  [0, 1]
  solution: [2, 3]
  magic:    [4, 5]
```

```bash
sprezzature-video pitch film.yaml --duration 60
# colors: the secret sauce is 5 words ('Ten packages. Five surfaces each.').
# That is a label, not the insight.
# colors: the secret sauce is 4 of its 5 words a feature list (...). Kawasaki's
# warning applies: the underlying magic is the one non-obvious thing that makes
# the solution possible, not an inventory of what ships.
```

It reports a missing beat, beats out of order, a problem that starts after the
first 22 % of the film, and a secret sauce that is too short (under six words),
written in brochure verbs (`supports`, `includes`), or half or more an
inventory. Whether the problem is the *right* problem stays a human question.

**`--voice` reads the narration instead of the screen.** A sixty-second film
puts one sentence a scene in front of a viewer and speaks eight, so the voice
is most of what they receive. A film can carry the three beats in its scene
list while saying something else out loud.

```bash
sprezzature-video pitch film.yaml --duration 60 --voice fr
```

A line takes the beat of the scene on screen when it starts. One declaration,
not two, so the voice cannot be filed under a beat the picture disagrees with.

### `calque`: two languages, or one and a rendering of it

A film shot in two languages is two films. The failure is quiet: every line is
grammatical, every fact is right, and the second cut sounds like a translation
because it is one. A reviewer reading a diff of two languages sees two columns
of unrelated words and cannot tell.

```bash
sprezzature-video calque film.yaml --from en --to fr
# demo: the fr cut reads as a rendering of the en one (score 0.88, at or above
# 0.75). 7 of 8 positions have the same sentence count and the same numerals
# in the same order: line(s) 1, 2, 3, 4, 5, 6, 8. Two cuts written separately
# distribute their material differently; these do not. Read them side by side
# before shipping both.
```

Meaning is never inspected. What is measured is correspondence: a translation
preserves the shape of what it translates, and two scripts composed separately
distribute their material differently. The threshold of 0.75 was calibrated
against both sides: eleven known-translated cuts scored 0.75 to 0.89 and the
same eleven rewritten scored 0.36 to 0.70. A suspicion, named line by line, not
a verdict.

### `prose`: the mechanical half of the writing charters

Em and en dashes, a comma followed by "and" or "et", sentences that open on a
negation, and a list of banned phrases. Both languages, each with its own
list: `mord` means nothing to the English checker and `truly` means nothing to
the French one.

```bash
sprezzature-video prose script.txt --lang fr --strict
```

Modals and reflex antithesis are **counted and never failed on**. A raw modal
count confuses the senses, and "a third party can demand this control" keeps
its modal because it states enforceability. The number tells you where to
read.

Judgement stays judgement. Whether a sentence earns its place is not a thing
a regular expression knows, and a green tick standing in for a reading would
be worse than no check at all.

More runs, with their output, are in [EXAMPLES.md](EXAMPLES.md). Agent routing
is in [TRIGGERS.md](TRIGGERS.md).

---

## Boundaries

Which package owns what, between this suite and
[ai-helpers](https://deraison.ai/ai-helpers), is written down in
[BOUNDARIES.md](BOUNDARIES.md). The short version: **ai-helpers owns the
primitive, sprezzature owns the opinion.** The narration audio is made by
`sprezzature-audio`; this package measures it and synthesizes nothing. Caption
files and ffmpeg primitives come from `video-helper`, durations from
`audio-helper`. Rendering is done by Hyperframes, outside this package.

## Status

0.4.2, alpha. The checker, the asset ledger, the captions, the
post-processing, the timeline layout, the pitch and calque checks, the prose
charter, the YAML spec loader and the five surfaces are written and tested:
125 tests. CI runs ruff, `ruff format --check`, mypy and pytest on Python 3.12,
and a floor job that installs and imports the package on 3.10.

There is no renderer module yet. Hyperframes is driven directly, and a
`renderers/` package returns in the commit that gives it a module.

## License

BSD-3-Clause.
