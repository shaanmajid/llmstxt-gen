# Build stage
FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_PREFERENCE=only-managed
ENV UV_NO_DEV=1

WORKDIR /app

# Copy .python-version and install Python (uv reads it automatically)
COPY .python-version .
RUN uv python install

# Install dependencies (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy source and install project
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Runtime stage
FROM debian:bookworm-slim

# Non-root user for security
RUN groupadd --system --gid 999 app \
    && useradd --system --gid 999 --uid 999 --create-home app

COPY --from=builder --chown=app:app /python /python
COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"
USER app
WORKDIR /app

# Default command (customize for your application)
CMD ["python", "-m", "python_template"]
