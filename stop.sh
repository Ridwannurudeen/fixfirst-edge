#!/usr/bin/env bash
# FixFirst Edge — stop everything start.sh started.
# Usage (from repo root): ./stop.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGDIR="$ROOT/.runtime"

say()  { printf "\033[36m[ffe]\033[0m %s\n" "$*"; }
ok()   { printf "\033[32m[ok]\033[0m  %s\n" "$*"; }

kill_pidfile() {
  local name="$1" file="$2"
  [ -f "$file" ] || return 0
  local pid
  pid=$(cat "$file")
  if kill -0 "$pid" 2>/dev/null; then
    say "stopping $name (pid $pid)..."
    pkill -TERM -P "$pid" 2>/dev/null || true
    kill -TERM "$pid" 2>/dev/null || true
    # give it 3s to exit cleanly, then force
    for _ in 1 2 3; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 1
    done
    kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" 2>/dev/null || true
  fi
  rm -f "$file"
}

kill_pidfile frontend "$LOGDIR/frontend.pid"
kill_pidfile backend  "$LOGDIR/backend.pid"

if command -v docker >/dev/null 2>&1 \
   && docker ps --format '{{.Names}}' | grep -q '^vectoraidb$'; then
  say "stopping database..."
  docker stop vectoraidb >/dev/null
fi

ok "all stopped"
