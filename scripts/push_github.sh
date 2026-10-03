#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEY="${MOKO_AI_DEPLOY_KEY:-$ROOT/.secrets/moko-ai-brand-book-deploy}"
REMOTE="git@github.com:mokoaibot/moko-ai-brand-book.git"

if [[ ! -f "$KEY" ]]; then
  echo "Missing deploy key: $KEY" >&2
  exit 1
fi
chmod 600 "$KEY"

if git -C "$ROOT" remote get-url origin >/dev/null 2>&1; then
  git -C "$ROOT" remote set-url origin "$REMOTE"
else
  git -C "$ROOT" remote add origin "$REMOTE"
fi

export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
git -C "$ROOT" push origin main
git -C "$ROOT" push origin v2.0.0
