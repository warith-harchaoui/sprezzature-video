# Landscape

[🇫🇷 PAYSAGE.md](https://github.com/warith-harchaoui/sprezzature-video/blob/main/PAYSAGE.md) · 🇬🇧 LANDSCAPE.md

Every tool below can produce a project video. Only one of them checks whether
the video is still **telling the truth about the project** six weeks later.
That is the distinction this page is about, and it is not a flattering one in
every direction: on motion, this package is the weakest in the table.

## The honest table

| Tool | Licence | Renders | Claims checked against source | Asset rebuild audit | Motion breadth |
|---|---|---|---|---|---|
| **sprezzature-video** | BSD-3 | delegates | **yes** — declared claims verified both ways | **yes** — tracked / derived / sole, divergence refused | narrow; it owns none of it |
| [Remotion](https://remotion.dev) | source-available, paid for companies | React → MP4 | no | assets live in the repo | very broad |
| [Revideo](https://re.video) | MIT | headless, library-first | no | assets live in the repo | broad |
| [Motion Canvas](https://motioncanvas.io) | MIT | browser, editor-driven | no | assets live in the repo | broad |
| [Hyperframes](https://hyperframes.heygen.com/) | Apache-2.0 | HTML → MP4 | no | registry can refetch | very broad |
| [brag](https://github.com/latent-spaces/brag) | MIT | via Hyperframes | no | inherits Hyperframes | broad |
| [Manim](https://www.manim.community/) | MIT | Python → MP4 | no | assets live in the repo | broad, maths-shaped |
| [Descript](https://descript.com) | proprietary, hosted | hosted | no | your media lives there | broad |

`sprezzature-video` **delegates rendering on purpose**. Hyperframes is the
default and Playwright and ffmpeg are not excluded. Frame-grabbing is the most
commoditised step in the chain and the least opinionated; the judgement lives
in the storyboard and in whether the claims survive contact with the code.

## The map

![Positioning map](assets/sprezzature_video.png)

```sh
standpoint assets/landscape.csv --outdir assets
```

Produced with [`standpoint`](https://github.com/warith-harchaoui/standpoint).
The geometry is correlation PCA and is deterministic: the same table gives the
same map every run, whatever model named the axes.

Worth recording: the first table handed to `standpoint` was **refused**.
*"criteria with identical columns (they measure the same thing here)"* — rating
claim-checking and asset-auditing as all-or-nothing had made two columns into
one, which adds no information and silently double-weights a single idea. The
ratings above are the corrected ones: asset-rebuild auditability is genuinely a
spectrum, and a tool with a refetchable asset registry is not in the same place
as one that just hopes the files are still there.

## What the shape actually says

The two axes explain 86% of the variance between these tools, and the second
one is the interesting half:

- **Nimble ↔ Robust** is loaded by self-hosting (0.51), code-first (0.48) and
  open licence (0.48). It separates the hosted editor from everything a
  developer runs themselves. Nothing surprising lives here.
- **Versatile ↔ Precise** is loaded by claims-checking (**+0.60**) against
  motion breadth (**−0.54**). The axis is, almost literally, *does it verify
  what it says* versus *can it animate anything*.

So the map puts `sprezzature-video` alone at the top right, and the renderers
cluster together at the bottom right. That is not this package beating them. It
is this package **not being in their contest**: they compete on what can be
drawn, and nobody in that cluster is trying to check a number against a
catalogue, because that is not what a renderer is for.

The practical reading: if you want a film that can say anything, pick one of
the renderers. If you want a film whose claims you can still trust after the
project moves, you currently have to add this layer yourself — or use this one.

## When to pick something else

- **You need real motion design** — particle systems, 3D, character animation.
  Remotion, Revideo and Hyperframes are all better at this than anything here,
  and this package is happy to drive them.
- **Your video makes no factual claims.** A mood piece, a title sequence, a
  showreel. The whole apparatus here is overhead with nothing to protect.
- **You want to edit by hand, in a timeline.** Descript, Premiere, Resolve. A
  declarative spec is the wrong shape for that work.
- **You are already deep in React.** Remotion will cost you less, provided the
  licence fits — note it is source-available, not open source, which matters if
  you are assembling a BSD-licensed stack.

## See also

- [BOUNDARIES.md](BOUNDARIES.md) — which package owns what, between this suite
  and ai-helpers.
- [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures)
  and [sprezzature-maps](https://github.com/warith-harchaoui/sprezzature-maps) —
  what appears *inside* the frame.
- [sprezzature-audio](https://github.com/warith-harchaoui/sprezzature-audio) —
  the voice and the captions.
