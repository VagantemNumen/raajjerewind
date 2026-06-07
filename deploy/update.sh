#!/usr/bin/env bash
#
# Update Raajje Rewind in place on the droplet.
#
# The app lives at /srv/raajje-rewind owned by the `raajje` system user (nologin),
# so every step that touches app files runs via `sudo -u raajje`. Only the service
# restart needs root. Run this as the deploy user (must have sudo):
#
#     /srv/raajje-rewind/deploy/update.sh
#
# chroma_db and .env are gitignored and untracked, so git never touches them.
#
# Note: `git pull` runs as `raajje`, so the repo's origin must be reachable
# without interactive auth — i.e. a public HTTPS remote, or a deploy key/token
# configured for the raajje user if the repo is private.

set -euo pipefail

# Everything lives inside main() so that if `git pull` rewrites this very script
# mid-run, bash has already parsed the whole function and won't execute a
# half-updated file.
main() {
  # Resolve the repo root from this script's location (.../deploy/update.sh).
  local app_dir
  app_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

  local run_as="raajje"
  local service="raajje-rewind-backend"
  local venv_pip="$app_dir/backend/.venv/bin/pip"
  # Dedicated, gitignored home for npm so its cache doesn't litter the repo root.
  local npm_home="$app_dir/.npm-home"

  # Run a command as the app owner.
  run() { sudo -u "$run_as" "$@"; }

  echo "==> Repo: $app_dir"

  # Refuse to run if tracked files have uncommitted edits — those are what a
  # fast-forward pull would conflict with. Untracked files (build caches,
  # chroma_db, .env) are ignored here; git still protects them on checkout.
  if [[ -n "$(run git -C "$app_dir" status --porcelain --untracked-files=no)" ]]; then
    echo "!! Working tree at $app_dir has uncommitted changes. Resolve them first:" >&2
    run git -C "$app_dir" status --short --untracked-files=no >&2
    exit 1
  fi

  echo "==> Pulling latest (fast-forward only)"
  run git -C "$app_dir" pull --ff-only

  echo "==> Syncing backend dependencies"
  run "$venv_pip" install --quiet --requirement "$app_dir/backend/requirements.txt"

  echo "==> Building frontend"
  # HOME points at a dedicated gitignored dir so npm's cache (.npm, .cache) lands
  # somewhere raajje can write without polluting the repo root.
  run mkdir -p "$npm_home"
  run env HOME="$npm_home" npm --prefix "$app_dir/frontend" ci
  run env HOME="$npm_home" npm --prefix "$app_dir/frontend" run build

  echo "==> Restarting backend"
  sudo systemctl restart "$service"

  echo "==> Done. Service status:"
  sudo systemctl --no-pager --lines=0 status "$service" | head -n 5
}

main "$@"
