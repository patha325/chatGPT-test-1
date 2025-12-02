#!/usr/bin/env bash
set -euo pipefail

export PYTHONUNBUFFERED=1

if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
