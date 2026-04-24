#!/usr/bin/env bash
# FixFirst Edge — one-command startup.
# Runs database, backend, ingest (if needed), frontend, and opens the browser.
# Usage (from repo root): ./start.sh
# Stop:                   ./stop.sh

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${FFE_VENV:-$HOME/ffe-venv}"
MODEL_CACHE="${MODEL_CACHE_DIR:-$HOME/ffe-cache/models}"
LOGDIR="$ROOT/.runtime"
mkdir -p "$LOGDIR" "$MODEL_CACHE" "$ROOT/data/raw"

say()  { printf "\033[36m[ffe]\033[0m %s\n" "$*"; }
err()  { printf "\033[31m[err]\033[0m %s\n" "$*" >&2; }
ok()   { printf "\033[32m[ok]\033[0m  %s\n" "$*"; }

pick_python() {
  for candidate in python3.11 python3.12 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      version="$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
      case "$version" in
        3.11|3.12)
          printf "%s" "$candidate"
          return 0
          ;;
      esac
    fi
  done
  return 1
}

ensure_venv_target() {
  if [ -n "${FFE_VENV:-}" ]; then
    printf "%s" "$FFE_VENV"
    return 0
  fi
  if [ -f "$HOME/ffe-venv/bin/activate" ]; then
    printf "%s" "$HOME/ffe-venv"
    return 0
  fi
  printf "%s" "$ROOT/.venv"
}

# ── 1. Database ──────────────────────────────────────────────────────────
say "checking database..."
if ! command -v docker >/dev/null 2>&1; then
  err "docker not found. install Docker Desktop first."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  err "Docker Desktop isn't running. open it and retry."
  exit 1
fi

if docker ps --format '{{.Names}}' | grep -q '^vectoraidb$'; then
  ok "database already running"
elif docker ps -a --format '{{.Names}}' | grep -q '^vectoraidb$'; then
  docker start vectoraidb >/dev/null
  ok "database started"
else
  say "creating database container (first run)..."
  docker run -d --name vectoraidb -p 50051:50051 --restart unless-stopped \
    williamimoh/actian-vectorai-db:latest >/dev/null
  ok "database created and running"
fi

# ── 2. Python venv ───────────────────────────────────────────────────────
VENV="$(ensure_venv_target)"
if [ ! -f "$VENV/bin/activate" ]; then
  say "creating python venv at $VENV..."
  if ! PYTHON_BIN="$(pick_python)"; then
    err "Python 3.11 or 3.12 is required. Install one of them or set FFE_VENV to a compatible virtualenv."
    exit 1
  fi
  "$PYTHON_BIN" -m venv "$VENV"
  ok "venv created with $PYTHON_BIN"
fi
# shellcheck source=/dev/null
source "$VENV/bin/activate"

if ! python -c "import fastapi" >/dev/null 2>&1; then
  say "installing backend dependencies into $VENV..."
  pip install -r "$ROOT/backend/requirements.txt" >"$LOGDIR/pip-install.log" 2>&1 || {
    err "dependency install failed. check $LOGDIR/pip-install.log"
    exit 1
  }
  ok "backend dependencies installed"
fi

# ── 3. Backend ───────────────────────────────────────────────────────────
if curl -sfm 2 http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
  ok "backend already running on :8000"
else
  say "starting backend..."
  (
    cd "$ROOT/backend"
    MODEL_CACHE_DIR="$MODEL_CACHE" \
      nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 \
      >"$LOGDIR/backend.log" 2>&1 &
    echo $! > "$LOGDIR/backend.pid"
  )
  for _ in $(seq 1 40); do
    if curl -sfm 2 http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
      ok "backend up (pid $(cat "$LOGDIR/backend.pid"))"
      break
    fi
    sleep 2
  done
  if ! curl -sfm 2 http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
    err "backend failed to come up. check $LOGDIR/backend.log"
    exit 1
  fi
fi

# ── 4. Ingest (if corpus empty) ──────────────────────────────────────────
ready=$(curl -sf http://127.0.0.1:8000/api/health 2>/dev/null \
          | grep -o '"collection_ready":[a-z]*' | cut -d: -f2 || true)
if [ "$ready" != "true" ]; then
  say "ingesting demo corpus (2-4 min on first run)..."
  cp -n "$ROOT"/data/fixtures/*.csv "$ROOT/data/raw/" 2>/dev/null || true
  (
    cd "$ROOT/backend"
    MODEL_CACHE_DIR="$MODEL_CACHE" PYTHONPATH=. \
      python scripts/bulk_ingest.py >"$LOGDIR/ingest.log" 2>&1
  )
  ok "corpus ingested"
else
  ok "corpus already ingested"
fi

# ── 5. Frontend ──────────────────────────────────────────────────────────
if curl -sfm 2 http://127.0.0.1:3000 >/dev/null 2>&1; then
  ok "frontend already running on :3000"
else
  say "starting frontend..."
  if ! command -v npm >/dev/null 2>&1; then
    err "npm not found. install Node.js in WSL: sudo apt install -y nodejs npm"
    exit 1
  fi
  (
    cd "$ROOT/frontend"
    if [ ! -d node_modules ]; then
      say "installing frontend deps (first run, ~1 min)..."
      npm install --silent >"$LOGDIR/npm-install.log" 2>&1
    fi
    nohup npm run dev >"$LOGDIR/frontend.log" 2>&1 &
    echo $! > "$LOGDIR/frontend.pid"
  )
  for _ in $(seq 1 30); do
    if curl -sfm 2 http://127.0.0.1:3000 >/dev/null 2>&1; then
      ok "frontend up (pid $(cat "$LOGDIR/frontend.pid"))"
      break
    fi
    sleep 2
  done
fi

# ── 6. Open browser ──────────────────────────────────────────────────────
URL="http://localhost:3000"
if command -v wslview >/dev/null 2>&1; then
  wslview "$URL" 2>/dev/null || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
  open "$URL"
else
  say "open $URL in your browser"
fi

echo
ok "all up. the app is at $URL"
ok "stop everything with: ./stop.sh"
ok "logs:   $LOGDIR/backend.log  $LOGDIR/frontend.log"
