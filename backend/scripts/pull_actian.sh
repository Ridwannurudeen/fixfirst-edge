#!/usr/bin/env bash
set -u
IMG="williamimoh/actian-vectorai-db:latest"
attempt=0
while [ "$attempt" -lt 20 ]; do
  attempt=$((attempt + 1))
  echo "--- attempt $attempt $(date +%T) ---"
  docker pull "$IMG" 2>&1 | tail -3
  if docker image inspect "$IMG" >/dev/null 2>&1; then
    echo "PULL_OK"
    exit 0
  fi
  sleep 10
done
echo "PULL_FAILED"
exit 1
