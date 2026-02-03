# Multi-stage image because we want to keep the runtime image small and only include the app code

FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

# Build wheels for all deps (keeps runtime image smaller and build tooling out of final image).
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


FROM python:3.11-slim AS runtime

WORKDIR /app

COPY requirements.txt .
COPY --from=builder /wheels /wheels

# Install deps from the prebuilt wheels only.
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy application code
COPY app ./app

# Runtime defaults (override in docker-compose if desired)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_LEVEL=info
ENV RELOAD=false

EXPOSE 8000

# Use the existing app entrypoint, which reads env vars via pydantic-settings.
CMD ["python", "-m", "app"]
