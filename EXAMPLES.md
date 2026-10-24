# Examples

Every example below runs against the same small film spec. It is deliberately
tiny: the interesting part is not the YAML, it is what happens when the project
moves underneath it.

```yaml
# film.yaml
name: demo
claims:
  - text: "167 kinds, every one hand-authored."
    value: 167
    source:
      path: sprezzature-figures/sprezzature_figures/catalog/figures.json
      method: json_len
  - text: "30 Laws of UX"
    value: "30 laws"
    source:
      path: sprezzature-ux-laws/references/laws-of-ux.md
      method: literal
      selector: "30 laws"
```

Two claims, two different ways of being true: one is a count read out of a JSON
array, the other a phrase that must appear verbatim in a reference file.

## Verify the claims

```bash
make-film verify film.yaml --root ~/
```

```
ok   matches
ok   matches

2/2 claims hold
```

Exit code 0. Now suppose the catalogue grows and nobody re-cuts the film — the
exact thing that happened to the five films on sprezzature.ai, which said "127"
while the catalogue held 167:

```
FAIL the film says 127 ('127 kinds, every one hand-authored.');
     sprezzature-figures/sprezzature_figures/catalog/figures.json says 167
ok   matches

1/2 claims hold
```

Exit code 1. The message names both numbers **and** the deciding file, because
whoever reads it has to find the frame to re-cut and the authority to trust.

A spec with no claims at all exits 1 too. "0/0 claims hold" reads exactly like
a film that checks out, and that is the failure this package exists to prevent.

## Scan for numbers nothing accounts for

`verify` protects the claims somebody remembered to declare. `scan` catches the
one typed into a keyframe at midnight:

```bash
make-film scan composition/index.html --spec film.yaml
```

```
UNDECLARED '960' in 'one implementation, five ways in · 960 tests · nothing has to leave'

1 undeclared number(s) on screen
```

Only *visible* text is read. A stylesheet carries hundreds of lengths and a
script hundreds of offsets; counting them would bury the one assertion that
matters. A year in a wordmark is a legitimate exception, and has to be said out
loud rather than guessed:

```bash
make-film scan composition/index.html --spec film.yaml --ignore 2026
```

## Audit the asset tree

Can this film be rendered again from a clone?

```bash
make-film assets film.yaml --tree _assets --repo .
```

```
diverged (1):
  figures/bar-grouped.svg  differs from web/img/figures/bar-grouped.svg;
                           the film and the project no longer show the same
                           file. Decide, do not guess.
missing (1):
  music/track.mp3  licensed track; the whole beat grid is measured off this file

11/13 assets in hand
```

Three classes, and the distinction is the point. A file one `cp` away is not
the same problem as a file that exists nowhere else. **A divergence is never
silently repaired** — when a copy and its source disagree, only a human knows
which one is right, and that refusal is what caught six figures that had been
regenerated out from under four films.

`--restore` copies back the tracked assets that are simply absent, and touches
nothing else.

## Build captions

```bash
make-film captions film.yaml --lang en --out film.en.vtt
make-film captions film.yaml --lang fr --out film.fr.vtt --translated
```

The text is the narration script the voice was synthesized from, so it is exact
where a transcriber would only be close. The **durations are measured** from
the audio, not typed: the script this generalises hard-coded them, and the day
two stale lines were re-synthesized they moved by 43 and 64 milliseconds with
nothing to notice.

`--translated` omits voice tags, because W3C reserves `<v Name>` for the track
in the audio's own language.

## Take a poster frame

```bash
make-film poster out/film.mp4 --out out/film.jpg --at 7.6
```

Not `--at 0.0` on a film that fades in: that is a frame of empty paper. Pick
the moment the film's strongest line is fully on screen.

## Over HTTP

The same operations, same answers — one implementation underneath:

```bash
pip install 'sprezzature-video[api]'
uvicorn sprezzature_video.api:app --port 8000

curl -s -X POST localhost:8000/v1/scan \
  -H 'content-type: application/json' \
  -d '{"html": "<p>167 kinds, 960 tests</p>", "claims": []}'
```

`/v1/scan` and `/v1/captions` are pure. `/v1/verify` reads files under a root
**on the server**, because a claim is only meaningful against the repository it
describes.

## As a gate

The exit codes are the point. In a pre-commit hook or a CI step:

```bash
make-film verify film.yaml --root . || exit 1
make-film scan composition/index.html --spec film.yaml || exit 1
```

A film is the one artefact that makes claims about the code from outside the
code. Nothing else in a repository re-reads it.
