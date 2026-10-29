# Landscape

[🇫🇷 PAYSAGE.md](https://github.com/warith-harchaoui/sprezzature-video/blob/main/PAYSAGE.md) · 🇬🇧 LANDSCAPE.md

`sprezzature-video` is the film checker of the [sprezzature](https://sprezzature.ai/)
suite, a set of Python packages for building publication-quality web content.
It is the only package of the ten that does not make something you look at. It
checks something somebody already made, against the code that film describes.

## The problem, before any comparison

A film about a project makes claims about that project: how many chart kinds,
how many rules, how many tests. Then it burns those claims into pixels at
thirty frames a second, and nothing reads them again.

A sentence in a README gets re-read. Somebody opens the file, somebody greps
it, somebody copies a line out of it into a slide. A number inside a key frame
is no longer text. It is a picture of a number, and the only thing that would
notice it had gone wrong is a person watching the film with the repository open
beside them.

That is not a hypothetical. The five films serving on sprezzature.ai said
**"127 chart kinds"** for months after the catalogue had grown to 167. The
figure was baked into ten compositions and five rendered MP4 files, so nothing
short of a re-cut could correct it, and nothing anywhere was watching. The
whole package exists because of that one number.

So this is not a renderer. Its centre is a checker that holds a film's
assertions against the code they describe, in both directions: `verify` checks
the claims somebody declared, `scan` reads the composition and reports every
number on screen that no claim accounts for. Beside the checker sits an asset
ledger that answers one question per file, "could this film be rendered again
from a clone", and a caption writer that builds WebVTT from the narration
script and the measured length of each audio file rather than from a
transcription. The renderer stays behind a seam, because which tool grabs the
frames is the least interesting decision in the chain.

## How it fits in the ecosystem

```
sprezzature suite
├── sprezzature-video     ← this package (the film checker)
├── sprezzature-figures     (the charts that appear inside the frame)
├── sprezzature-maps        (the map plates that appear inside the frame)
├── sprezzature-colors      (the palette the film is cut in)
├── sprezzature-audio       (the narration voice, and the WebVTT writer)
├── sprezzature-publish     (the page the film is served from)
└── video-helper            (the ffmpeg primitives, from ai-helpers)
```

What comes before: a storyboard, the figures and map plates from
`sprezzature-figures` and `sprezzature-maps`, and a narration script. What
comes after: a renderer, by default [HyperFrames](https://github.com/heygen-com/hyperframes),
then the page `sprezzature-publish` builds around the finished file. The sister
package doing the neighbouring work is `sprezzature-audio`: it owns the voice
and the single WebVTT writer the suite shares, while this package owns where
each spoken line lands on a film's time grid.

## When to choose it

- **Your film states a count that is going to move.** A catalogue, a test
  suite, a package list. A declared claim names the file that decides it, so a
  growing catalogue fails the check instead of quietly ageing the film.
- **The project changed and a film already shipped.** This is the silent
  trigger, and the one worth remembering. Nothing re-reads a rendered MP4, so
  the film is wrong the moment the catalogue grows, and stays wrong until
  somebody looks.
- **You are about to re-render and the asset tree is gitignored.** Fonts,
  figures, narration, music. The ledger says which files are one copy away,
  which re-run a script, and which exist in exactly one place on one disk. A
  render that dies halfway through is a worse way to learn that.
- **A film is cut in two languages.** `calque` measures whether the second cut
  was written or merely translated, by correspondence rather than by meaning,
  and names the lines that match position for position.

## When to pick something else

- **You need real motion design.** Particle systems, three dimensions,
  character animation, anything where the frame is the work.
  [Remotion](https://www.remotion.dev/), [Motion Canvas](https://motioncanvas.io/)
  and HyperFrames are far better at this than anything here, and this package
  is happy to drive them. It owns none of that breadth and does not want to.
- **Your film asserts nothing.** A mood piece, a title sequence, a showreel.
  There is no claim to protect, and the whole apparatus is overhead.
- **You want to record a screen and share a link.** [Loom](https://www.loom.com/)
  and [Screen Studio](https://screen.studio/) do that in one gesture, with
  nothing to install in a build and nothing to declare. A spec file is the
  wrong shape for a two minute walkthrough.
- **You want a presenter on screen reading your script.**
  [Synthesia](https://www.synthesia.io/) produces a convincing avatar from text
  in minutes, with voice cloning and about thirty languages. Nothing here draws
  a face.
- **Your claims live in code examples rather than in frames.** Python's
  `doctest`, [Sybil](https://sybil.readthedocs.io/) and `cargo test --doc`
  already run your documentation as a test, they are mature, and they are
  better at that job than a video package will ever be.
- **Your real question is "can I rebuild this artefact".** [DVC](https://dvc.org/)
  and Nix answer it for a whole project, with remote storage, lock files and a
  decade of operational experience behind them. The ledger here answers it for
  one film's asset tree and nothing else.

## Ideas worth stealing

Studying a competitor and bringing nothing back is wasted reading. Eight
things found while writing this page, best value first, two of them refused
with the reason.

**[Chromatic](https://www.chromatic.com/) and [Percy](https://percy.io/): an
accepted baseline is recorded, not re-argued.** A reviewer approves a visual
change once and the tool stops asking. Here, `assets.audit` reports
`DIVERGED` with "decide, do not guess", which is the right refusal and has no
memory: the same divergence is re-reported on every run until people learn to
scroll past it, and a guard everybody scrolls past has stopped running. The
fix is an `accepted:` block in the film spec holding the digest somebody
approved and the one line saying why, consulted by `AssetLedger.audit` before
it emits `State.DIVERGED`. Half a day, and the highest return of the eight,
because it protects a check that already exists from going quietly ignored.

**[Nix](https://nixos.org/) and [Make](https://www.gnu.org/software/make/):
"I cannot find your input" is a different failure from "your output is
stale".** Both refuse with a message naming the missing file and neither
counts it as work done. `verify` does not make that distinction, and the
omission turns the package against itself. The claim paths in a film spec are
relative to the directory holding the clones, which the spec documents. Run
from one level down, the suite's own `films.yaml` prints nine lines of
`FAIL could not verify: claim source is missing` and concludes
**`1/10 claims hold`**, with exit code 1. Run from the right place the same
file gives `10/10`. The trouble is that `1/10 claims hold` is the exact
sentence a massively stale film produces, so somebody reading it in continuous
integration goes and corrects numbers that were right. A measure that does not
know which way it is wrong is the defect class this package exists to catch,
pointed back at it. The fix is to count `FileNotFoundError` separately from a
value mismatch, report it on its own line, and refuse outright when *every*
source is missing, because that is one wrong root and not ten claims dying on
the same day. Half a day: `Verdict` already carries `detail`, so it needs a
state rather than a rewrite. Resolving paths against the spec file instead of
the working directory is the tempting second half and should wait, because the
sibling layout is a property of the checkout and not of the document.

**[Sybil](https://sybil.readthedocs.io/en/latest/integration.html) and
[pytest-codeblocks](https://pytest-codeblock.readthedocs.io/en/latest/): the
documentation check is collected by the test runner, not by a command somebody
remembers.** Sybil registers a `conftest.py` collector, so a stale example in
`README.md` fails the ordinary `pytest` run with no second command anywhere.
This package has five surfaces and none of them is that: `sprezzature-video
verify film.yaml` has to be wired into a workflow file by hand, which is the
failure mode this suite keeps finding. A `pytest11` entry point in
`pyproject.toml` plus a small plugin that collects every `*.film.yaml` under
the working directory as a test item would make `pytest` enough. One day, no
new dependency.

**[Playwright](https://playwright.dev/docs/test-snapshots): `--update-snapshots`
turns a report into a diff you commit.** A failing visual test is one flag away
from an updated baseline, so keeping the baselines honest is cheap enough that
people do it. The analogue here is `scan`, which prints undeclared numbers and
leaves the reader to hand-type a claim block per finding. A
`--write-claims` flag emitting a stub into the spec, with `method:` left
deliberately invalid so the check keeps failing until a human names the
deciding file, would make declaring a claim a thirty second chore. Half a day,
and the invalid-by-default stub is the part that must not be skipped.

**[DVC](https://dvc.org/doc/command-reference/repro): `dvc.lock` records the
hash of every input and output of the run that produced an artefact.** That is
how a reviewer six months later knows which version of the data a result came
from. `AssetLedger.audit` compares a copy to its source *today*, and cannot say
which side moved. Writing `film.lock.yaml` at render time, one digest per
asset, turns `DIVERGED` from "these differ" into "the project regenerated this
figure after the film shipped" or "somebody edited the copy", which are
opposite problems with opposite fixes. One day, and it pairs naturally with the
`accepted:` block above.

**[shields.io](https://shields.io/): the number is never baked, so it can never
go stale.** A badge is fetched on every page load and is always current. Half of
that is takeable and half is refused. Takeable: a `data-claim="figures.count"`
attribute on the element carrying a number, read by `_VisibleText.handle_starttag`,
which already exists and currently discards attributes. That removes the
`--ignore` list, where today every exempt value lives on a command line far from
the frame it belongs to. Refused: substituting the live value into the
composition at render time, which would make this package own the composition
format and break the renderer seam that is the whole architecture. Half a day
for the attribute.

**[WhisperX](https://github.com/m-bain/whisperX): forced alignment against a
known transcript, which is exactly the situation here.** The script is on disk,
the audio was synthesized from it, so word-level timings are available for the
asking and `split_line` would break a caption at a measured pause instead of at
a guessed comma. Refused as written: WhisperX brings torch, and this package
installs in seconds today. If it is ever done it belongs in
`sprezzature-audio`, which already carries a whisper.cpp build and already owns
the WebVTT writer, and it arrives here as a measured duration list like
everything else.

**[Nix](https://nixos.org/): pin the whole build environment and the output
stops depending on the machine.** Refused, and the reason is specific rather
than ideological. The suite's narration goes through a sampling voice engine:
the same French sentence measured 7.520, 6.760 and 6.640 seconds on three runs
of `speaker-helper` 0.13. A pinned environment cannot make that deterministic,
so the pin would buy the appearance of reproducibility and not the thing. The
`timeline` module is the answer that was built instead, and it absorbs the
variation rather than pretending it is absent.

## How the domain divides

There is almost no frontal competitor, and saying so plainly is more useful
than inventing one. The table below therefore holds two families that normally
never meet, because the work this package does is the overlap between them.

**The first family makes a film.** Inside it the real split is who writes the
motion. Code-first frameworks (Remotion, Motion Canvas, Revideo, HyperFrames,
Manim) put the composition in a text file a reviewer can diff, render
deterministically, and run in a build. Timeline editors (After Effects,
Descript) put it in a document a person drags around, which buys craft and
costs reproducibility. Recorders (Loom, Screen Studio) make the human the
source, so there is no composition at all. Hosted generators (Veed, Pictory,
Synthesia) take a script and return a finished file, with the whole pipeline on
somebody else's machine. Not one of them, at any price, reads the project the
film is about.

**The second family keeps an assertion true**, and it is almost never pointed
at a video. Tested documentation is the mature form: `doctest`, Sybil,
`pytest-codeblocks` and `cargo test --doc` run the examples inside your prose,
so a stale example fails the build. Badge services take the other route by
never baking the number at all, which is why nobody has ever seen a stale
badge. Visual snapshot tools (Playwright's `toHaveScreenshot`, Percy,
Chromatic) compare a rendering against a stored baseline, and the distinction
matters here: they catch an artefact that *changed*, and the failure this
package exists for is an artefact that did **not** change while the world
around it did. Asset registries (DVC, Git LFS, Make, Nix) answer the rebuild
question, each at a different grain: content hashes, pointer files, file
timestamps, a whole pinned environment.

**Captions are a third and smaller split**, and it is a clean one. Everything
listed here except this package starts from the audio: WhisperX and its
relatives, Rev, Otter, YouTube's automatic track. That is automatic speech
recognition (ASR), and ASR guesses at words somebody already knows, because the
narration was synthesized from a script sitting on disk. Starting from the
script makes the text exact by construction and leaves only the timing to
compute, and the timing here is measured from the audio file rather than typed.
Forced alignment sits between the two and is the honest comparison; a hosted
transcription service is a different product entirely.

## The table

Every tool is rated 1 to 5 on each criterion, higher is better (⭐ weak to
⭐⭐⭐⭐⭐ strongest). The scores are a considered judgement, not a benchmark,
and each column is oriented so that more stars mean stronger on that trait: for
cost, more stars mean cheaper or more open; for install weight, more stars mean
lighter. A ⭐ means the tool does not do what the column measures, which on a
capability scale is a one. The machine-readable source is
[`assets/landscape.csv`](assets/landscape.csv): 29 tools across 14 criteria.

| Tool | Produces a finished film | Motion and animation breadth | Visual quality of the result | Checks declared claims against the code | Catches undeclared drift | Captions faithful to the script | Rebuildable from a clean clone | Deterministic output | Local and offline | Free or open | Usable in continuous integration | Runs with no human in the loop | Light to install | Maturity and ecosystem |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| sprezzature-video | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Remotion | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Motion Canvas | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Revideo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| HyperFrames | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Manim | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| After Effects | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| ffmpeg | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Descript | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Screen Studio | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Loom | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Veed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Pictory | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Synthesia | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| doctest | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Sybil | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| pytest-codeblocks | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| cargo test --doc | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Playwright snapshots | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Percy | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Chromatic | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| shields.io | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| DVC | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Git LFS | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Make | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Nix | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| WhisperX | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Rev | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| YouTube auto-captions | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## The map

![Positioning map of 29 tools on two axes derived from a principal component analysis. sprezzature-video sits alone in the top right corner, at coordinates 3.46 and 3.42, with nothing else near it. Along the top edge at the same height but far to the left are the code-first renderers: HyperFrames, Manim, Revideo, Remotion and Motion Canvas. The far left is held by After Effects, Descript and Screen Studio. The bottom edge holds the hosted services: Rev at the very bottom, then YouTube auto-captions, Loom, Pictory, Synthesia and Veed. Between this package and the renderers sit the tested-documentation tools, doctest, cargo test --doc, Sybil and pytest-codeblocks, and the asset registries, Nix, DVC, Make and Git LFS. The horizontal axis opposes making the picture to checking the fact; the vertical axis opposes a tool you run and can rebuild from to a tool that is already there and costs nothing to start.](assets/landscape.svg)

The source is [`assets/landscape.csv`](assets/landscape.csv), the star table
above and nothing added, and the map is regenerated with:

```sh
python scripts/landscape_to_csv.py ~/sprezzature-video/LANDSCAPE.md   # from ~/sprezzature
standpoint assets/landscape.csv --outdir assets --stem landscape --check
```

The geometry is ordinary correlation principal component analysis (PCA) and is
**deterministic**: the same table gives the same map every run. The four words
at the edges come from a local model, and they are vaguer than the loadings
behind them, so the loadings are the control. `standpoint` puts the first row
top right and orients everything else around it; that is a convention of the
drawing, not a claim about quality.

**Horizontal, named "Artistry ↔ Reliability".** Visual quality of the result
(−0.445), produces a finished film (−0.432) and motion breadth (−0.388) pull
left; checks declared claims against the code (+0.302), runs with no human in
the loop (+0.274), usable in continuous integration (+0.269) and free or open
(+0.264) pull right. The axis opposes *making the picture* to *checking the
fact*, which is the division this whole page is about, and it is the axis this
package sits at the far right of by construction.

**Vertical, named "Simplicity ↔ Autonomy".** Local and offline (+0.411),
rebuildable from a clean clone (+0.385) and deterministic output (+0.381) load
together at the top, with free or open (+0.270) and usable in continuous
integration (+0.269) behind them; light to install (−0.362) and maturity and
ecosystem (−0.167) pull down. The top pole is one coherent thing, *a tool you
run yourself and can rebuild from*, and the bottom is its opposite, *a tool
already standing that costs nothing to start*. Rev, YouTube's automatic
captions and the hosted video generators sit along the bottom edge; Nix, DVC
and the renderers sit along the top.

**Two axes carry 61.2 % of the table** (38.9 % and 22.3 %). The 38.8 % left
over is in the table and not on this page, and one part of it matters more
than the rest: *catches undeclared drift* is the weakest-loaded criterion on
both axes (+0.173 and +0.110), and it is the criterion that separates this
package from everything else here. The map is a first orientation; the column
that justifies the package barely moves it.

Two readings worth having. HyperFrames sits at exactly the same height as this
package (3.42) and at the opposite end of the horizontal axis, which is the map
noticing that the renderer behind the seam shares every reproducibility trait
and none of the checking ones. And this package is alone in its corner, which
is not a win: the renderers cluster together because they are in a contest with
each other, and nobody in that cluster is trying to check a number against a
catalogue, because that is not what a renderer is for.

`--check` reports the leader top right and the axis labels visible, and marks
the figure **not readable**: eight label pairs risk overlapping, among them
Remotion with Motion Canvas, Sybil with pytest-codeblocks and Percy with
Chromatic. Those are tools whose ratings genuinely sit on top of each other,
so the overlap is the table being honest rather than the figure being wrong.
The interactive SVG separates them on hover; the PNG does not.

## Sources

- [Remotion](https://www.remotion.dev/), [Motion Canvas](https://motioncanvas.io/)
  and [Revideo](https://re.video/) compared for 2026:
  [rendercomp](https://rendercomp.com/blog/best-programmatic-video-tools-2026/).
- [HyperFrames](https://github.com/heygen-com/hyperframes), open-sourced under
  Apache 2.0 in May 2026, and
  [a review that places it against Remotion](https://kompozy.io/reviews/heygen-hyperframes).
- [Sybil's test-runner integration](https://sybil.readthedocs.io/en/latest/integration.html)
  and [pytest-codeblocks](https://pytest-codeblock.readthedocs.io/en/latest/):
  the two ways a Python project runs its own prose as a test.
- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots)
  and [Chromatic on visual testing](https://www.chromatic.com/blog/how-to-visual-test-ui-using-playwright/),
  for what a stored baseline does and does not catch.
- [DVC](https://dvc.org/doc/command-reference/repro) for the rebuild question
  answered at project scale, and for `dvc.lock`.
- [WhisperX](https://github.com/m-bain/whisperX) for forced alignment, and the
  measured gap between aligned and native Whisper timestamps in
  [Whisper Has an Internal Word Aligner](https://arxiv.org/pdf/2509.09987).
- [Best AI video makers tested for 2026](https://pictory.ai/blog/best-ai-video-maker-2026),
  for the hosted end of the first family.

## See also

- [BOUNDARIES.md](BOUNDARIES.md): which package owns what, between this suite
  and ai-helpers.
- [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures)
  and [sprezzature-maps](https://github.com/warith-harchaoui/sprezzature-maps):
  what appears inside the frame.
- [sprezzature-audio](https://github.com/warith-harchaoui/sprezzature-audio):
  the voice, and the single WebVTT writer the suite shares.
