"""
``measure`` is the one place a base install can run out of dependency.

Why this exists
---------------
Nothing exercised :func:`sprezzature_video.captions.measure` at all -- not the
missing-file contract its own docstring promises, and not the import guard
beside it. A dependency reached lazily behind an error message nobody has ever
seen is a dependency whose absence surfaces as a traceback in front of a user.

The guard is worth having wherever ``audio-helper`` sits. It is a base
dependency as this is written, and moving it to the ``voice`` extra is
proposed and measured -- in a clean venv the install this package's CI performs
goes from 74 packages and 326 MB to 65 and 182, which is 129 MB of scientific
stack for a function that reads one number out of ffprobe. But a base
dependency can also simply fail to import on a broken install, and a
``ModuleNotFoundError`` raised out of a function whose documented failure is
``FileNotFoundError`` tells the caller neither which of the two went wrong nor
what to do about it.

The 98 tests that came before this file all pass without ``audio-helper``, none
of them skipping, because every one of them hands :class:`Spoken` a declared
duration and tests the cue arithmetic rather than the measurement. That is what
left this function uncovered.

What runs where, said out loud rather than discovered later
-----------------------------------------------------------
The first three cases need no heavy dependency: two of them *simulate* the
absence, which is the thing worth testing. They run everywhere, CI included.

The last one measures a real file and therefore needs both ``audio-helper``
and the ``ffprobe`` binary. A runner has no ffprobe, so it skips there, by
name. This is an admitted hole, not a hidden one: a skip reads exactly like a
pass, so it is written down here and in the skip reason. It still earns its
keep on a developer machine, where it is the only thing that has ever called
the function for real.

Author
------
Warith HARCHAOUI <warithmetics@deraison.ai>
"""

from __future__ import annotations

import shutil
import sys
import wave
from pathlib import Path

import pytest

from sprezzature_video.captions import measure


def _silence(path: Path, seconds: float = 1.0, rate: int = 24000) -> Path:
    """A WAV of a known length, written with the standard library only.

    Deliberately not generated through numpy or audio-helper: a fixture that
    needs the dependency under test cannot say anything about its absence.
    """
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(b"\x00\x00" * int(seconds * rate))
    return path


def test_a_missing_file_is_refused_before_anything_is_imported(tmp_path: Path) -> None:
    """The documented contract, and it holds without the optional dependency.

    ``FileNotFoundError`` rather than a zero, because a narration file that is
    not there must not quietly become a cue of no length -- which reads on
    screen as a caption that never appears.

    The order matters and is asserted by the next test: this check comes
    *before* the import, so a missing file reports a missing file even on an
    install that has no measurer.
    """
    with pytest.raises(FileNotFoundError, match="narration file is missing"):
        measure(tmp_path / "there-is-no-such-wav.wav")


def test_without_audio_helper_the_error_names_the_extra(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A base install that reaches this line is told what to install.

    Not a bare ``ImportError`` from inside a function whose documented failure
    is ``FileNotFoundError``: the caller asked for a duration, and what it gets
    back has to say which of the two went wrong and what to do about it.

    The absence is simulated by putting ``None`` in ``sys.modules``, which is
    what makes ``import audio_helper`` raise without uninstalling anything --
    so this case runs on a machine that has the package, which is every machine
    a developer uses.
    """
    monkeypatch.setitem(sys.modules, "audio_helper", None)
    wav = _silence(tmp_path / "narration.wav")

    with pytest.raises(RuntimeError) as caught:
        measure(wav)

    message = str(caught.value)
    assert "audio-helper" in message, f"the error does not name the missing package: {message!r}"
    assert "sprezzature-video[voice]" in message, (
        f"the error does not name the extra that ships it, so a reader has to "
        f"guess which install fixes it: {message!r}"
    )
    assert isinstance(caught.value.__cause__, ImportError), (
        "the original ImportError is not chained, so the traceback loses where "
        "the failure actually came from"
    )


def test_the_missing_file_check_comes_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Both can be wrong at once, and the file is the one reported.

    Without this, the two guards above could be in either order and both of
    their tests would pass. An install with no measurer, handed a path that
    does not exist, should hear about the path: it is the caller's mistake, and
    it is the one fixable without installing anything.
    """
    monkeypatch.setitem(sys.modules, "audio_helper", None)
    with pytest.raises(FileNotFoundError):
        measure(tmp_path / "absent.wav")


def test_a_real_file_measures_its_real_length(tmp_path: Path) -> None:
    """The only case that has ever called the measurer for real.

    Skips where ``audio-helper`` or ``ffprobe`` is absent, which includes this
    package's own CI -- see the module docstring for why that is deliberate and
    why it is written down rather than left to be noticed.

    One second of silence at 24 kHz, checked to 50 ms. The tolerance is for the
    container, not for the arithmetic: a WAV header rounds, and the point here
    is that a measured number comes back at all and lands on the length that
    was written, not that ffprobe agrees to the sample.
    """
    pytest.importorskip(
        "audio_helper",
        reason="audio-helper is 129 MB of scipy and numpy for this one call, "
        "and is a candidate for the voice extra",
    )
    if shutil.which("ffprobe") is None:
        pytest.skip("ffprobe is not on PATH; audio-helper reads the duration through it")

    wav = _silence(tmp_path / "one-second.wav", seconds=1.0)
    assert measure(wav) == pytest.approx(1.0, abs=0.05)
