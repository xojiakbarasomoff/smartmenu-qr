# ─────────────────────────────────────────────────────────────────
#  SmartMenu QR — Production Dockerfile
#  Two-stage build: compile deps → clean runtime image
#  Entry point: python run.py  (FastAPI + aiogram on one event loop)
# ─────────────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ───────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# gcc is needed to compile some async C extensions (aiohttp, etc.)
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ── Stage 2: lean runtime image ───────────────────────────────────
FROM python:3.11-slim

# Non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Pull installed packages from builder stage
COPY --from=builder /root/.local /home/app/.local

# Copy only the files the running app needs
COPY app/   ./app/
COPY run.py .

# .env is NOT baked into the image.
# Pass secrets at runtime:
#   docker run --env-file .env ...
# or set individual vars:
#   docker run -e BOT_TOKEN=xxx -e NOTIFY_CHAT_ID=yyy ...

ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Hand ownership to the non-root user
RUN chown -R app:app /app
USER app

# FastAPI port
EXPOSE 8000

# Light health-check — probes the menu API every 30 s
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/menu')" \
      || exit 1

CMD ["python", "run.py"]
