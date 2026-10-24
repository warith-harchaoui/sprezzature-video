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

Early. The checker, the asset ledger, the captions and the post-processing are
written and tested; the renderer seam, the YAML spec loader and the five
surfaces (argparse CLI, Click CLI, HTTP API, MCP, skill) are not here yet.

## License

BSD-3-Clause.
