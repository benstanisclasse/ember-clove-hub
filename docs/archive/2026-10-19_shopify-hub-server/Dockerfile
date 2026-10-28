FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ffmpeg: video thumbnails / covers for ad uploads (Meta + TikTok require one)
# libgomp1: OpenMP runtime LightGBM needs
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 hub
WORKDIR /app

# Install dependencies first (cached unless pyproject.toml changes), then drop the
# placeholder package so the real code under /app is what gets imported.
COPY pyproject.toml ./
RUN mkdir app && touch app/__init__.py \
    && pip install . \
    && pip uninstall -y shopify-hub \
    && rm -rf app build *.egg-info

COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app

USER hub
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*", "--no-server-header"]
