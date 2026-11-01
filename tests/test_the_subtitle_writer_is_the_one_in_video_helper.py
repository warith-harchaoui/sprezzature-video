"""
``write`` is the migrated line, and nothing was calling it.

Why this exists
---------------
On 2026-10-31 the timed-text writer moved from ``sprezzature_audio`` to
``video_helper.subtitles``. The whole migration is one import, and it is
*lazy* -- it sits inside :func:`sprezzature_video.captions.write` so the
splitting rules can be read and tested without the dependency present.

That laziness is right, and it is also why the move shipped untested. Before
this file, no test in this package mentioned ``write`` at all: the suite's 102
tests exercised ``to_cues``, ``split_line`` and ``split_to_fit``, which is the
arithmetic, and never the one function that renders a document. A moved import
that no test executes is a moved import whose first reader is a user, and
``write`` is reached from two surfaces -- ``cli.py`` and the HTTP API -- so the
traceback would have surfaced in a terminal or as a 500.

The migration itself was verified byte for byte before being committed: for the
same cues, both writers returned identical documents under ``voices=True`` and
under ``voices=False``. This file is that verification made permanent and run by
CI, where ``video-helper>=2.9.0`` is a base dependency and therefore present.

What this file found
--------------------
``translated`` cannot change the output. ``write`` builds every ``Cue`` with
``start``, ``end`` and ``text`` and never a ``speaker``, so ``voices=`` has
nothing to suppress: ``write(lines, translated=True)`` and
``write(lines, translated=False)`` are the same string. The flag is not broken
-- the writer honours it, which the last test proves by handing it a cue that
does carry a speaker -- the *model* is silent. ``Spoken`` has no speaker field,
the film spec has no such key, and ``speaker=`` appears nowhere in the package.
The 22 caption tracks shipped on the site agree: none carries a ``<v >`` tag.

The flag is kept rather than deleted, and the tests below say why out loud: the
contract it states is the correct one (W3C reserves ``<v Name>`` for the
same-language captions track), and the day a film has two narrators it is
needed at all three surfaces again. What was wrong was that its inertness was
invisible. It is asserted here instead.

Author
------
Warith HARCHAOUI <warithmetics@deraison.ai>
"""

from __future__ import annotations

import re

import pytest

from sprezzature_video.captions import Spoken, to_cues, write

#: Three lines, one of which is long enough to be recut. Durations are declared
#: rather than measured so this file needs neither audio-helper nor ffprobe --
#: see ``test_a_measurement_says_what_it_needs`` for the measuring path.
LINES = [
    Spoken(start=0.0, text="Une carte de situation montre où.", duration=2.6),
    Spoken(
        start=3.0,
        text="Un choroplèthe montre combien, et nomme sa méthode.",
        duration=4.1,
    ),
    Spoken(start=8.0, text="Court.", duration=0.8),
]

_TIMESTAMP = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})$")


def test_the_lazy_import_resolves_at_all() -> None:
    """The migration, executed.

    This is the assertion the move needed and did not have. It fails with an
    ``ImportError`` if ``video_helper.subtitles`` stops exporting ``Cue`` or
    ``write_vtt`` under the floor this package declares -- which is exactly how
    a dependency bump would break ``write`` without touching a line of it.
    """
    body = write(LINES, translated=False)
    assert body.startswith("WEBVTT"), f"what came back is not a WebVTT document: {body[:40]!r}"


def test_every_cue_the_document_carries_is_well_formed() -> None:
    """A rendered document, read back cue by cue.

    Checks the shape the writer is responsible for rather than the splitting,
    which is tested elsewhere: a timestamp line per cue, milliseconds to three
    digits, and time moving forward. A writer that emitted ``0:0:0.0`` or ran
    the clock backwards would still start with ``WEBVTT``.
    """
    body = write(LINES, translated=False)
    stamps = [line for line in body.splitlines() if "-->" in line]
    assert len(stamps) == len(to_cues(LINES)), (
        f"{len(stamps)} timestamp lines for {len(to_cues(LINES))} cues"
    )

    previous_end = -1.0
    for stamp in stamps:
        matched = _TIMESTAMP.match(stamp)
        assert matched, f"not a WebVTT timestamp line: {stamp!r}"
        numbers = [int(group) for group in matched.groups()]
        start = numbers[0] * 3600 + numbers[1] * 60 + numbers[2] + numbers[3] / 1000
        end = numbers[4] * 3600 + numbers[5] * 60 + numbers[6] + numbers[7] / 1000
        assert end > start, f"a cue that ends before it starts: {stamp!r}"
        assert start >= previous_end, f"cues out of order at {stamp!r}"
        previous_end = end


def test_translated_provably_changes_nothing_today() -> None:
    """The flag is inert, and that is written down rather than discovered.

    Not a wish: ``write`` never gives a ``Cue`` a ``speaker``, so ``voices=``
    has nothing to act on. Both surfaces that pass this flag -- ``--translated``
    on the CLI and ``translated`` in the API request body -- promise to omit
    voice tags from a document that has never had one.

    This test is the one that will fail the day someone adds a speaker to
    ``Spoken``, and that failure is the point: it says "the flag is live now,
    go update this file and the two surface descriptions" instead of letting a
    behaviour change arrive silently.
    """
    assert write(LINES, translated=True) == write(LINES, translated=False), (
        "translated now changes the output -- which means a speaker reached a "
        "Cue. That is the intended end state: delete this assertion, and check "
        "that the CLI help and the API field description are true again."
    )


def test_the_writer_itself_does_honour_voices() -> None:
    """So the finding above lands on the model, not on the dependency.

    Without this, the previous test is ambiguous: a writer that ignored
    ``voices=`` entirely would satisfy it too, and the conclusion would have
    been aimed at ``video-helper`` instead of at ``Spoken``. Handing it a cue
    that does carry a speaker separates the two.
    """
    subtitles = pytest.importorskip(
        "video_helper.subtitles",
        reason="video-helper is a base dependency; a skip here means a broken install",
    )
    spoken = [subtitles.Cue(start=0.0, end=2.0, text="Bonjour.", speaker="Narratrice")]

    assert "<v Narratrice>" in subtitles.write_vtt(spoken, voices=True), (
        "the writer drops a voice tag it was asked to emit"
    )
    assert "<v " not in subtitles.write_vtt(spoken, voices=False), (
        "the writer emits a voice tag it was asked to omit"
    )
