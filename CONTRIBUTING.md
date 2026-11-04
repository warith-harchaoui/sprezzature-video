# Contributing

## Getting set up

```bash
git clone https://github.com/warith-harchaoui/sprezzature-video
cd sprezzature-video
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

`[dev]` adds the test toolchain: pytest, ruff, mypy and httpx. Everything else
is a base dependency, and there is no other extra. `video-helper` provides the
WebVTT writer (`video_helper.subtitles`) and the ffmpeg primitives,
`audio-helper` measures narration length, `os-helper` hashes and copies asset
files, and `sprezzature-audio` brings the narration engines through
`speaker-helper`. FastAPI, uvicorn, fastapi-mcp and Playwright are in the base
too. The `poster` command and the `post` module need the `ffmpeg` binary.

Rendering is **not** a Python dependency. The default renderer is Hyperframes,
which arrives over `npx`; see [BOUNDARIES.md](BOUNDARIES.md) for why that line
is drawn where it is.

## The gates

Lint, format, types and tests. CI runs all four, on Python 3.12, with ruff
pinned to 0.15.21. A separate floor job installs and imports the package on
Python 3.10.

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

`.githooks/pre-push` runs the same gates before a push. Enable it once per
clone with `git config core.hooksPath .githooks`.

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
