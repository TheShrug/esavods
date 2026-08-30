FROM python:3.12-slim

# ffmpeg     - frame extraction + yt-dlp's ranged --download-sections cuts
# tesseract  - OCR engine; eng data is enough, we whitelist digits anyway
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        tesseract-ocr \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

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
