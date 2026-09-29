#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PORT="${PORT:-8080}"
HOST="${HOST:-0.0.0.0}"

echo "=========================================================="
echo " Starting Claude Studio Hub (SEO & Blog Commander)"
echo " Server URL: http://${HOST}:${PORT}"
echo " Log directory: ${DIR}/logs"
echo "=========================================================="

exec "${DIR}/venv/bin/python3" -m uvicorn app.main:app --host "${HOST}" --port "${PORT}"
