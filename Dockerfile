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

# The API, the MCP endpoint mounted beside it, and the Click twin. fastapi and
# uvicorn live behind the `api` extra precisely so nobody installing the
# library pays for them, so an image that serves has to ask for it.
RUN pip install --no-cache-dir ".[cli,api,mcp,post]"

EXPOSE 8000

# Serve what the image was built for. A CMD of `--help` is a container that
# starts, prints and exits — which looks like it works and does nothing.
# Override with the command line:
#
#   docker run --rm -v "$PWD:/work" IMAGE make-film verify /work/film.yaml --root /work
CMD ["uvicorn", "sprezzature_video.api:app", "--host", "0.0.0.0", "--port", "8000"]
