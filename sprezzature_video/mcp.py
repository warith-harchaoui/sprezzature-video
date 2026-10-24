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

Install the extras::

    pip install 'sprezzature-video[api,mcp]'

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

    def main(argv: list[str] | None = None) -> None:
        """
        Entry point when the MCP extra is not installed.

        Takes the same ``argv`` as the real entry point and ignores it: the two
        variants are reached through the same console script, so a caller that
        passes arguments must not get a ``TypeError`` from the branch that
        happens to be missing a dependency.

        Says which extra is missing and stops. Reaching an MCP command without
        the ``[mcp]`` extra needs a one-line fix, not a stack trace.
        """
        print(
            "sprezzature-video MCP surface requires fastapi-mcp. "
            "Install with: pip install 'sprezzature-video[api,mcp]'",
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

    def main(argv: list[str] | None = None) -> None:
        """
        Entry point for the ``sprezzature-video-mcp`` console script.

        Serves the FastAPI app — which carries both the HTTP routes and the MCP
        endpoint — with ``uvicorn``, in single-worker mode. Meant for local or
        container use; behind a real load balancer, run ``uvicorn`` directly.

        Arguments are parsed before anything is bound, so ``--help`` answers
        instead of starting a server and hanging.

        Parameters
        ----------
        argv : list of str or None, optional
            Arguments to parse. ``None`` reads ``sys.argv``.
        """
        import argparse
        import os

        parser = argparse.ArgumentParser(
            prog="sprezzature-video-mcp",
            description=(
                "Serve the sprezzature-video MCP tools over HTTP. Every tool is a "
                "route on the same FastAPI app, with the MCP endpoint mounted "
                "beside them."
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=(
                "Defaults come from SPREZZATURE_VIDEO_HOST and "
                "SPREZZATURE_VIDEO_PORT when those are set.\n"
                "The host defaults to 127.0.0.1: pass --host 0.0.0.0 to accept "
                "connections from outside this machine."
            ),
        )
        parser.add_argument(
            "--host",
            default=os.environ.get("SPREZZATURE_VIDEO_HOST", "127.0.0.1"),
            help="Interface to bind (default: %(default)s).",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=int(os.environ.get("SPREZZATURE_VIDEO_PORT", "8000")),
            help="Port to bind (default: %(default)s).",
        )
        args = parser.parse_args(argv)

        import uvicorn

        uvicorn.run(app, host=args.host, port=args.port, workers=1)


if __name__ == "__main__":  # pragma: no cover
    main()
