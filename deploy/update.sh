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

  # Run a command as the app owner.
  run() { sudo -u "$run_as" "$@"; }

  echo "==> Repo: $app_dir"

  # Refuse to run on a dirty tree — uncommitted edits in /srv would either be
  # clobbered or block the checkout. Surface it instead of guessing.
  if [[ -n "$(run git -C "$app_dir" status --porcelain)" ]]; then
    echo "!! Working tree at $app_dir has local changes. Resolve them first:" >&2
    run git -C "$app_dir" status --short >&2
    exit 1
  fi

  echo "==> Pulling latest (fast-forward only)"
  run git -C "$app_dir" pull --ff-only

  echo "==> Syncing backend dependencies"
  run "$venv_pip" install --quiet --requirement "$app_dir/backend/requirements.txt"

  echo "==> Building frontend"
  # HOME is set so npm's cache lands somewhere raajje can write (it owns app_dir).
  run env HOME="$app_dir" npm --prefix "$app_dir/frontend" ci
  run env HOME="$app_dir" npm --prefix "$app_dir/frontend" run build

  echo "==> Restarting backend"
  sudo systemctl restart "$service"

  echo "==> Done. Service status:"
  sudo systemctl --no-pager --lines=0 status "$service" | head -n 5
}

main "$@"
