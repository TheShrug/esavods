# Deno, for yt-dlp's JS challenge solver. Taken from the official binary-only
# image rather than a curl-pipe-sh installer so the version is pinned and the
# build needs no network fetch of its own.
FROM denoland/deno:bin-2.9.6 AS deno

FROM python:3.12-slim

# ffmpeg     - frame extraction + yt-dlp's ranged --download-sections cuts
# tesseract  - OCR engine; eng data is enough, we whitelist digits anyway
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        tesseract-ocr \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# YouTube's `n` signature challenge has to be solved in JavaScript, and
# yt-dlp only auto-detects deno (node needs an explicit --js-runtimes).
# Without one, extraction still works for now but yt-dlp calls it deprecated
# and drops to whatever formats avoid the challenge - and when those go, the
# failure reads as `Only images are available for download`, or with cookies
# as `The page needs to be reloaded`. Neither names the real cause, and the
# second looks exactly like the bot wall, so the obvious diagnosis is wrong.
COPY --from=deno /deno /usr/local/bin/deno

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY vodtimer ./vodtimer

# Cache lives on a volume so re-running a video costs no bandwidth.
ENV PYTHONUNBUFFERED=1
ENV VODTIMER_CACHE=/cache
VOLUME ["/cache"]

ENTRYPOINT ["python", "-m", "vodtimer"]
CMD ["--help"]
