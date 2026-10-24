# Contributing

## Getting set up

```bash
git clone https://github.com/warith-harchaoui/sprezzature-video
cd sprezzature-video
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

`sprezzature-video` depends on `sprezzature-audio` for the suite's single
WebVTT module and on `audio-helper` for measuring narration length. The
heavier optional work is behind extras: `[voice]` pulls the narration engines
(through `sprezzature-audio[narrate]` → `speaker-helper`), `[post]` pulls
`video-helper` for the ffmpeg primitives, `[local]` pulls Playwright.

Rendering is **not** a Python dependency. The default renderer is Hyperframes,
which arrives over `npx`; see [BOUNDARIES.md](BOUNDARIES.md) for why that line
is drawn where it is.

## The gates

The same three the rest of the suite runs, and CI runs all of them:

```bash
ruff check .
ruff format --check .
python -m mypy sprezzature_video
pytest -q
```

`pytest.ini_options` carries `--strict-markers`. That is deliberate across the
whole suite: without it, pytest warns about an unknown mark and then runs the
test anyway, so a typo in `@pytest.mark.renders` reads as a marked test and
behaves as an unmarked one.

## Tests, and what they are for here

Test files are named as sentences about the property they protect
(`test_a_film_cannot_claim_what_the_code_denies.py`), because the failure line
in CI should say what broke, not which file it lived in.

Two habits this repository asks for specifically:

**Sabotage the thing you are claiming to protect.** A guard that has never
failed is not known to work. When you add one, break the condition on purpose,
watch the test go red, and restore it. Several tests here exist because that
step found the guard was unreachable.

**Check which side of a new measure the known-good case lands on.** More than
one measurement written for this package flagged something correct on its first
run — a separator class that could never match, a staleness check that called
"Colour vision simulation" a retired skill. If a new check passes immediately
and quietly, confirm it can fail at all.

## Scope

This package owns planning, claim verification, the asset ledger, captions,
post-processing and the series. It does not own rendering, the voice engines,
or the ffmpeg primitives — those have homes, named in
[BOUNDARIES.md](BOUNDARIES.md). A patch that reimplements one of them here will
be asked to go there instead.

## Commits

Conventional-commit prefixes (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
The body should say what was wrong and why the fix is the right shape, not
restate the diff.
