"""
The asset ledger's three classes, and the refusal at the centre of it.

The behaviour worth protecting is not "finds missing files". It is that the
audit distinguishes a file one ``cp`` away from a file that exists nowhere
else, and that it **never silently repairs a divergence** -- because when a
copy and its source disagree, only a human knows which one is right. That
refusal caught six figures that had been regenerated out from under four films.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sprezzature_video import Asset, AssetLedger, Provenance, State


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    src = tmp_path / "repo" / "web" / "img" / "chart.svg"
    src.parent.mkdir(parents=True)
    src.write_text("<svg>original</svg>")
    return tmp_path / "repo"


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    out = tmp_path / "_assets"
    out.mkdir()
    return out


def _tracked() -> Asset:
    return Asset("figures/chart.svg", Provenance.TRACKED, source="web/img/chart.svg")


def test_a_matching_copy_is_ok(repo: Path, tree: Path) -> None:
    (tree / "figures").mkdir()
    (tree / "figures" / "chart.svg").write_text("<svg>original</svg>")
    [verdict] = AssetLedger([_tracked()]).audit(tree, repo)
    assert verdict.state is State.OK


def test_an_absent_copy_is_restorable_not_missing(repo: Path, tree: Path) -> None:
    """A file still tracked upstream is a copy away; that is not "missing"."""
    [verdict] = AssetLedger([_tracked()]).audit(tree, repo)
    assert verdict.state is State.RESTORABLE


def test_a_diverged_copy_is_never_silently_repaired(repo: Path, tree: Path) -> None:
    """
    The refusal. Both files exist and disagree, so the audit reports and stops.

    ``restore`` must leave it alone too: overwriting would quietly decide that
    the project's newer asset wins, which is sometimes exactly backwards.
    """
    (tree / "figures").mkdir()
    (tree / "figures" / "chart.svg").write_text("<svg>the film's older copy</svg>")
    ledger = AssetLedger([_tracked()])

    [verdict] = ledger.audit(tree, repo)
    assert verdict.state is State.DIVERGED
    assert "Decide, do not guess" in verdict.detail

    assert ledger.restore(tree, repo) == []
    assert (tree / "figures" / "chart.svg").read_text() == "<svg>the film's older copy</svg>"


def test_a_vanished_source_is_its_own_state(tmp_path: Path, tree: Path) -> None:
    """
    "The original moved" needs a different fix from "the copy is absent", so it
    must not collapse into RESTORABLE -- which would promise a copy that cannot
    happen.
    """
    empty_repo = tmp_path / "repo"
    empty_repo.mkdir()
    [verdict] = AssetLedger([_tracked()]).audit(tree, empty_repo)
    assert verdict.state is State.NO_SOURCE


def test_restore_proves_the_copy(repo: Path, tree: Path) -> None:
    """A copy is verified against its source, not assumed to have worked."""
    ledger = AssetLedger([_tracked()])
    assert len(ledger.restore(tree, repo)) == 1
    assert (tree / "figures" / "chart.svg").read_text() == "<svg>original</svg>"
    assert ledger.audit(tree, repo)[0].state is State.OK


def test_a_sole_asset_missing_reports_its_reason(tree: Path, repo: Path) -> None:
    """
    "missing" on its own tells nobody what to do. A SOLE entry carries why it
    exists nowhere else, and the audit has to surface that.
    """
    asset = Asset(
        "music/track.mp3",
        Provenance.SOLE,
        why="licensed track; the whole beat grid is measured off this file",
    )
    [verdict] = AssetLedger([asset]).audit(tree, repo)
    assert verdict.state is State.MISSING
    assert "licensed track" in verdict.detail


def test_a_derived_asset_offers_its_recipe(tree: Path, repo: Path) -> None:
    """DERIVED is restorable by re-running a tool, so the tool must be named."""
    asset = Asset(
        "vo-global-1.wav",
        Provenance.DERIVED,
        recipe="hyperframes tts ... --voice af_heart --speed 0.95",
    )
    [verdict] = AssetLedger([asset]).audit(tree, repo)
    assert verdict.state is State.RESTORABLE
    assert "af_heart" in verdict.detail
