#!/usr/bin/env bash
set -euo pipefail
if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 -c CHECKSUMS.sha256
elif command -v sha256sum >/dev/null 2>&1; then
  sha256sum -c CHECKSUMS.sha256
else
  echo "Kein shasum/sha256sum gefunden" >&2; exit 1
fi
