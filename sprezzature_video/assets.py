#!/usr/bin/env python3
"""
Can this film be rendered again from a clone? The asset ledger answers that,
per file, and refuses to guess.

A film renders from a tree of fonts, figures, narration, music and sound
effects. None of it belongs in git — a WAV and an MP3 do not delta-compress —
so the tree is gitignored, and the comfortable assumption is that everything
needed to rebuild it stays tracked. On the one real tree this was written
against, that was false, and the useful output is not a yes or no but a
**classification**:

``TRACKED``
    a copy of a file git does track. Restorable, and the copy is proved equal
    to its source rather than assumed — a copy that silently differs is worse
    than a missing one, because the film then quotes an image the project no
    longer ships.
``DERIVED``
    the output of a tool still on the machine: synthesized narration, colour
    vision simulations, a resized logo. Restorable by re-running the tool.
``SOLE``
    neither. It exists in exactly one place, and if that place is a single disk
    the film is one disk failure from unrenderable. Every ``SOLE`` entry carries
    a reason, because "missing" on its own tells nobody what to do.

The distinction is the whole point. A flat "9 files missing" sends someone
hunting; "these six are a `cp` away, these two re-run a script, and these nine
exist nowhere else" is a plan.

**Divergence is never silently repaired.** When a TRACKED copy differs from its
source, both exist and disagree, and only a human knows whether the film should
adopt the project's newer asset or the project should go back. The audit says
so and stops. That refusal is load-bearing: it caught six figures that had been
regenerated out from under four films.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Provenance(Enum):
    """Where an asset can be got again from. See the module docstring."""

    TRACKED = "tracked"
    DERIVED = "derived"
    SOLE = "sole"


class State(Enum):
    """What the audit found for one asset."""

    OK = "ok"
    MISSING = "missing"
    DIVERGED = "diverged"
    RESTORABLE = "restorable"
    NO_SOURCE = "no-source"


@dataclass(frozen=True)
class Asset:
    """
    One file the film renders from, and how it could be got again.

    Parameters
    ----------
    rel : str
        Path inside the asset tree, e.g. ``figures/sankey.svg``.
    provenance : Provenance
        Which of the three classes this belongs to.
    source : str
        For ``TRACKED``, the repo-relative path of the tracked original.
    recipe : str
        For ``DERIVED``, the command or script that regenerates it. Stored as
        text and shown in reports rather than executed here: this module
        audits, it does not run arbitrary commands.
    why : str
        For ``SOLE``, why it exists nowhere else. Required in practice — a
        ``SOLE`` entry without a reason is the thing that makes a tree
        unrebuildable six months later.
    """

    rel: str
    provenance: Provenance
    source: str = ""
    recipe: str = ""
    why: str = ""


@dataclass(frozen=True)
class AssetVerdict:
    """The audit's finding for one asset."""

    asset: Asset
    state: State
    detail: str

    @property
    def ok(self) -> bool:
        """True only for :attr:`State.OK`; everything else needs a decision."""
        return self.state is State.OK


def _digest(path: Path) -> str:
    """
    Content hash of *path*, through os-helper rather than a local hashlib call.

    os-helper is the suite's foundation for exactly this (files, hashing,
    config, timing), so hashing here would be a second implementation of a
    shared means. Imported lazily so that merely importing this module does not
    require the dependency — the audit is useful on a machine that has the tree
    but not the full toolchain.
    """
    import os_helper as oh

    return oh.hashfile(str(path))


@dataclass
class AssetLedger:
    """
    The declared asset tree of a film, and the audit over it.

    Parameters
    ----------
    assets : list[Asset]
        Every file the film needs, each classified.
    """

    assets: list[Asset] = field(default_factory=list)

    def audit(self, tree: Path | str, repo: Path | str) -> list[AssetVerdict]:
        """
        Check the tree, without writing anything.

        Parameters
        ----------
        tree : Path or str
            The asset tree the film renders from.
        repo : Path or str
            Root that ``Asset.source`` paths are relative to.

        Returns
        -------
        list[AssetVerdict]
            One verdict per declared asset, in declaration order.
        """
        tree, repo = Path(tree), Path(repo)
        out: list[AssetVerdict] = []

        for asset in self.assets:
            here = tree / asset.rel

            if asset.provenance is Provenance.TRACKED:
                src = repo / asset.source
                if not src.exists():
                    # The source is gone, so this asset is no longer restorable
                    # whatever its copy says. Reported as its own state because
                    # the fix is different: find where the original went.
                    out.append(
                        AssetVerdict(asset, State.NO_SOURCE, f"{asset.source} is not in the repo")
                    )
                elif not here.exists():
                    out.append(AssetVerdict(asset, State.RESTORABLE, f"copy from {asset.source}"))
                elif _digest(here) == _digest(src):
                    out.append(AssetVerdict(asset, State.OK, "matches its tracked source"))
                else:
                    out.append(
                        AssetVerdict(
                            asset,
                            State.DIVERGED,
                            f"differs from {asset.source}; the film and the project no "
                            "longer show the same file. Decide, do not guess.",
                        )
                    )
                continue

            if asset.provenance is Provenance.DERIVED:
                if here.exists():
                    out.append(AssetVerdict(asset, State.OK, "present"))
                else:
                    out.append(AssetVerdict(asset, State.RESTORABLE, f"regenerate: {asset.recipe}"))
                continue

            # SOLE. There is nothing to compare against and nothing to re-run,
            # so presence is the only question -- and absence is terminal.
            if here.exists():
                out.append(AssetVerdict(asset, State.OK, "present (sole copy)"))
            else:
                out.append(AssetVerdict(asset, State.MISSING, asset.why or "exists nowhere else"))

        return out

    def restore(self, tree: Path | str, repo: Path | str) -> list[str]:
        """
        Copy back the TRACKED assets that are simply absent, and nothing else.

        Deliberately narrow. Divergence is left alone — see the module
        docstring — and DERIVED assets are not regenerated here because that
        means running a tool, which belongs to the caller holding the recipe.

        Parameters
        ----------
        tree : Path or str
            Destination asset tree.
        repo : Path or str
            Root that ``Asset.source`` paths are relative to.

        Returns
        -------
        list[str]
            One line per file restored.

        Raises
        ------
        OSError
            If a copy does not match its source afterwards. Proved, not
            assumed: a silently bad copy is the failure this class exists to
            make impossible.
        """
        import os_helper as oh

        tree, repo = Path(tree), Path(repo)
        done: list[str] = []
        for verdict in self.audit(tree, repo):
            if verdict.state is not State.RESTORABLE:
                continue
            asset = verdict.asset
            if asset.provenance is not Provenance.TRACKED:
                continue
            dest, src = tree / asset.rel, repo / asset.source
            oh.make_directory(str(dest.parent))
            oh.copyfile(str(src), str(dest))
            if _digest(dest) != _digest(src):
                raise OSError(f"copy of {asset.rel} does not match {asset.source}")
            done.append(f"restored {asset.rel} <- {asset.source}")
        return done


def report(verdicts: list[AssetVerdict]) -> list[str]:
    """
    Render verdicts as lines, grouped so the cheap fixes read as cheap.

    Parameters
    ----------
    verdicts : list[AssetVerdict]
        Output of :meth:`AssetLedger.audit`.

    Returns
    -------
    list[str]
        Report lines. Empty when everything is :attr:`State.OK`.
    """
    order = [State.MISSING, State.DIVERGED, State.NO_SOURCE, State.RESTORABLE]
    lines: list[str] = []
    for state in order:
        group = [v for v in verdicts if v.state is state]
        if not group:
            continue
        lines.append(f"{state.value} ({len(group)}):")
        lines += [f"  {v.asset.rel}  {v.detail}" for v in group]
    return lines
