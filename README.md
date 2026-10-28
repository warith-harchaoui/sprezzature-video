# sprezzature-video

[🇫🇷 LISEZMOI.md](https://github.com/warith-harchaoui/sprezzature-video/blob/main/LISEZMOI.md) · 🇬🇧 README.md

A film about a project makes **claims** about that project — how many chart
kinds, how many tests, how many packages — and burns them into pixels, where
nothing ever reads them again. Prose in a README gets re-read. A number in a
keyframe does not.

So this package is not a renderer. Its centre is a checker that holds a film's
assertions against the code they describe, in both directions, and the renderer
sits behind a seam because which tool grabs the frames is the least interesting
decision here.

Part of the [sprezzature](https://sprezzature.ai/) suite.

---

## How it works

![Flow diagram. At the top, a film specification and the code it describes feed two lanes. The left lane checks the numbers: every declared claim against the place in the code that decides it, every number visible on screen against the declarations, and whether the film can be rendered again from a clone. The right lane checks the telling: the pitch in Kawasaki's order, and the mechanical half of the writing charter. Both meet in one outcome, the parts of a film a function can own, captions from measured audio, the poster baked as frame zero, and loudness levelled across a series.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-video/main/assets/how-it-works.svg)

## Why it exists

The five films that served on sprezzature.ai said **"127 chart kinds"**. The
catalogue had held 167 since September. The number was baked into ten
compositions and five rendered MP4s, so nothing short of a re-cut could correct
it — and nothing, anywhere, was watching. That is this package's whole subject.

## What's here

| Module | What it owns |
|---|---|
| `claims` | A claim is a declared pair: the text on screen, and the place in the code that decides whether it is true. `verify_all` checks every declared claim still holds; `undeclared_numbers` checks every number *visible* on screen is a declared claim. |
| `assets` | Can this film be rendered again from a clone? Three classes: `TRACKED` (a copy of a tracked file, proved equal to its source), `DERIVED` (output of a tool still on the machine), `SOLE` (exists in exactly one place). Divergence is reported, never silently repaired. |
| `captions` | WebVTT built from the narration script and the **measured** length of each audio file — not transcribed, and not typed. |
| `post` | The poster baked as frame 0, because Slack, X and Discord regenerate their thumbnail server-side from the first frame whatever a `poster=` attribute says. Plus loudness normalisation across a series. |

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
declare — never the one typed into a keyframe at midnight and left to go stale.

## Does the film explain anything?

Two checks that have nothing to do with rendering, and everything to do with
whether a viewer who never heard of your package can say what it is for.

### `pitch`: problem, solution, secret sauce

Guy KAWASAKI's order. State what goes wrong, then what you do about it, then
the one non-obvious thing that makes it possible. The third beat is the one
people get wrong: the underlying magic is an insight, in plain language, that
a competitor does not have. A feature list is not it, and neither is a demo.

```bash
sprezzature-video pitch film.yaml --duration 60
# colors: the secret sauce reads as a feature list ('Ten packages. Five
# surfaces each.'). Kawasaki's warning applies: the underlying magic is the
# one non-obvious thing that makes the solution possible, not an inventory
# of what ships.
```

Declared in the spec by scene index, so the check runs against the film that
exists rather than a description of it that can drift:

```yaml
pitch:
  problem:  [0, 1]
  solution: [2, 3]
  magic:    [4, 5]
```

It catches three things: no problem beat at all, a problem that arrives after
the viewer's patience has run out, and a secret sauce that is an inventory.
Whether the problem is the *right* problem stays a human question.

### `prose`: the mechanical half of the writing charters

Em dashes, comma-plus-and, sentences that open on a negation, the named
machine tics. Both languages, each with its own list: `mordre` means nothing
to the English checker and `truly` means nothing to the French one.

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

---

## Install

```bash
pip install sprezzature-video                    # the checker and the ledger
pip install 'sprezzature-video[voice,post]'      # plus narration and ffmpeg work
```

## Boundaries

Which package owns what, between this suite and
[ai-helpers](https://deraison.ai/ai-helpers), is written down in
[BOUNDARIES.md](BOUNDARIES.md). The short version: **ai-helpers owns the
primitive, sprezzature owns the opinion.** Voice arrives through
`sprezzature-audio[narrate]`, ffmpeg through `video-helper`, and rendering
through Hyperframes behind a seam.

## Status

0.2.0. The checker, the asset ledger, the captions, the post-processing, the
YAML spec loader and all five surfaces are written and tested — 46 tests, with
CI on 3.10/3.11/3.12. The renderer seam is still out of band: Hyperframes is
driven directly, and `renderers/` returns in the commit that gives it a
module.

## License

BSD-3-Clause.
