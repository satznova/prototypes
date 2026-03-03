# ─────────────────────────────────────────────────────────────
# FROM — every Dockerfile starts here.
# This pulls the official Python 3.11 image from Docker Hub.
# "slim" = stripped-down version, smaller size (~50MB vs ~900MB)
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ─────────────────────────────────────────────────────────────
# WORKDIR — sets the working directory inside the container.
# All subsequent commands run from here.
# Created automatically if it doesn't exist.
# ─────────────────────────────────────────────────────────────
WORKDIR /app

# ─────────────────────────────────────────────────────────────
# COPY requirements.txt FIRST (before your code).
# Why? Layer cache optimization.
# This layer only rebuilds if requirements.txt changes.
# If you change main.py, this layer is still cached → pip skipped.
# ─────────────────────────────────────────────────────────────
COPY model-app/requirements.txt .


# ─────────────────────────────────────────────────────────────
# RUN — executes a command during the BUILD phase.
# --no-cache-dir = don't store pip cache inside image (keeps image smaller)
# ─────────────────────────────────────────────────────────────
RUN pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────
# COPY your app code LAST.
# This layer changes on every code edit — and that's fine,
# because all the expensive layers above are cached.
# ─────────────────────────────────────────────────────────────
COPY model-app/ .

# ─────────────────────────────────────────────────────────────
# EXPOSE — documents which port the app listens on.
# Note: this is documentation only. The actual port mapping
# happens when you run: docker run -p 8000:8000
# ─────────────────────────────────────────────────────────────
EXPOSE 8000

# ─────────────────────────────────────────────────────────────
# CMD — the command that runs when the container starts.
# Use array form (not string) — avoids shell interpretation issues.
# "0.0.0.0" is critical: without it, the app listens only on
# localhost INSIDE the container and is unreachable from outside.

# uvicorn is the WebServer
# ─────────────────────────────────────────────────────────────
CMD ["uvicorn", "my-app:app", "--host", "0.0.0.0", "--port", "8000"]
