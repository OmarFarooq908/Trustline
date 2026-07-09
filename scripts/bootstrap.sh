#!/usr/bin/env bash
set -euo pipefail

# Bootstrap development environment for Trustline.
# Requires: git, curl (for uv install if missing)

if ! command -v uv &>/dev/null; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

make install-dev
make check

echo "Bootstrap complete. Run: trustline --help"
