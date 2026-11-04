#!/usr/bin/env python3
"""
sprezzature-video: the MCP (Model Context Protocol) surface.

Module summary
--------------
Exposes the same operations as the HTTP surface as MCP tools, so an agent can
ask whether a film still tells the truth without being told how to shell out.
This is a thin wrapper: ``fastapi_mcp`` mounts an MCP endpoint onto the very
same FastAPI app, so the tools and the routes cannot drift apart — there is
only one implementation underneath.

Why an agent wants this specifically
------------------------------------
An agent writing or revising a project video is exactly the caller most likely
to restate a number from memory. ``verify_claims`` and ``scan_composition``
give it a way to check instead of recall, against the repository rather than
against its own context.

fastapi-mcp is a base dependency, so there is no extra to install::

    pip install sprezzature-video

Then serve it::

    sprezzature-video-mcp --host 127.0.0.1 --port 8000

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import sys

try:
    from fastapi_mcp import FastApiMCP
except ImportError:  # pragma: no cover - dependency guard

    def main(argv: list[str] | None = None) -> int:
        """
        Entry point when fastapi-mcp cannot be imported.

        Takes the same ``argv`` as the real entry point and ignores it: the two
        variants are reached through the same console script, so a caller that
        passes arguments must not get a ``TypeError`` from the branch that
        happens to be missing a dependency.

        fastapi-mcp is a base dependency, so reaching this branch means a
        broken install. It says so with a one-line fix and stops, rather than
        printing a stack trace.
        """
        print(
            "sprezzature-video MCP surface could not import fastapi-mcp, which is a "
            "base dependency since 2026-11-01 -- a broken install rather than "
            "a missing extra. Reinstall with: "
            "pip install 'sprezzature-video'",
            file=sys.stderr,
        )
        sys.exit(1)

else:
    # Reuse the exact same FastAPI app -- MCP is a thin wrapper on top.
    from sprezzature_video.api import app

    # FastApiMCP mounts an MCP endpoint on the existing FastAPI app; the
    # wrapped instance is kept at module scope so downstream code (tests, ASGI
    # runners) can reach both the FastAPI app and the MCP handler.
    mcp = FastApiMCP(
        app,
        name="sprezzature-video",
        description=(
            "Sprezzature video MCP tools: verify a film's declared claims against "
            "the code it describes, find numbers on screen that no claim accounts "
            "for, and build WebVTT captions from a narration script."
        ),
        include_tags=["meta", "actions"],
    )
    # Newer fastapi-mcp releases split mount() into transport-specific
    # mount_http() (recommended) and mount_sse(); fall back to the legacy
    # mount() on older versions so a range of fastapi-mcp versions still work.
    if hasattr(mcp, "mount_http"):
        mcp.mount_http()
    else:  # pragma: no cover - legacy fastapi-mcp
        mcp.mount()

    import click

    @click.command(
        name="sprezzature-video-mcp",
        context_settings={"help_option_names": ["-h", "--help"]},
        epilog=(
            "Defaults come from SPREZZATURE_VIDEO_HOST and SPREZZATURE_VIDEO_PORT "
            "when those are set.\n\n"
            "The host defaults to 127.0.0.1: pass --host 0.0.0.0 to accept "
            "connections from outside this machine."
        ),
    )
    @click.option(
        "--host",
        envvar="SPREZZATURE_VIDEO_HOST",
        default="127.0.0.1",
        show_default=True,
        help="Interface to bind.",
    )
    @click.option(
        "--port",
        envvar="SPREZZATURE_VIDEO_PORT",
        type=int,
        default=8000,
        show_default=True,
        help="Port to bind.",
    )
    def _serve(host: str, port: int) -> None:
        """
        Serve the sprezzature-video MCP tools over HTTP.

        Every tool is a route on the same FastAPI app, with the MCP endpoint
        mounted beside them.
        """
        import uvicorn

        uvicorn.run(app, host=host, port=port, workers=1)

    def main(argv: list[str] | None = None) -> int:
        """
        Entry point for the ``sprezzature-video-mcp`` console script.

        Serves the FastAPI app — which carries both the HTTP routes and the MCP
        endpoint — with ``uvicorn``, in single-worker mode. Meant for local or
        container use; behind a real load balancer, run ``uvicorn`` directly.

        Arguments are parsed before anything is bound, so ``--help`` answers
        instead of starting a server and hanging. The parser is click, like
        every other command of the suite since 2026-11-04; a usage error exits
        2 and ``--help`` exits 0, as the argparse parser it replaced did.

        Parameters
        ----------
        argv : list of str or None, optional
            Arguments to parse. ``None`` reads ``sys.argv``.

        Returns
        -------
        int
            0 once the server has stopped.
        """
        try:
            _serve.main(args=argv, prog_name="sprezzature-video-mcp", standalone_mode=False)
        except click.exceptions.UsageError as exc:
            exc.show()
            raise SystemExit(2) from None
        except click.exceptions.Abort:
            raise SystemExit(130) from None
        except click.exceptions.Exit as exc:
            raise SystemExit(exc.exit_code) from None
        return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
