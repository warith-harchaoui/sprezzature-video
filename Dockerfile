FROM python:3.11-slim

WORKDIR /app

COPY . .

# ffmpeg, because the poster command shells out to it. The library half of
# this package needs nothing; the image is built to serve and to post-process,
# and an image whose own CMD works while half its commands die on a missing
# binary is worse than one that refuses to build.
RUN apt-get update \
    && apt-get install --no-install-recommends -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# The API, the MCP endpoint mounted beside it, and the command line. fastapi,
# uvicorn and fastapi-mcp are base dependencies since 2026-11-01, so the plain
# install is the whole surface and there is no extra to ask for.
RUN pip install --no-cache-dir "."

EXPOSE 8000

# Serve what the image was built for. A CMD of `--help` is a container that
# starts, prints and exits, which looks like it works and does nothing.
#
# `sprezzature-video-mcp` rather than `uvicorn sprezzature_video.api:app`: the
# MCP endpoint is mounted on the FastAPI app when `sprezzature_video.mcp` is
# imported, so the bare app served /v1/... and /health and answered 404 on
# /mcp. This one process serves both on the same port.
#
# Override with the command line:
#
#   docker run --rm -v "$PWD:/work" IMAGE make-film verify /work/film.yaml --root /work
CMD ["sprezzature-video-mcp", "--host", "0.0.0.0", "--port", "8000"]
