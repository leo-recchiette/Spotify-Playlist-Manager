FROM python:3.14-slim AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir spotipy==2.26.0

FROM python:3.14-slim
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
COPY --from=builder /opt/venv /opt/venv
RUN useradd --create-home app
USER app
WORKDIR /home/app
COPY spotify_sync_liked.py .
ENTRYPOINT ["python", "spotify_sync_liked.py"]
