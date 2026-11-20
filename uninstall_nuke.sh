#!/usr/bin/env bash
# Linux and macOS counterpart of uninstall_nuke.cmd
# Idempotent: remove this toolkit's pluginAddPath line from ~/.nuke/init.py
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TEXT="nuke.pluginAddPath(r'${ROOT}')"
FILE="${HOME}/.nuke/init.py"

if [[ ! -f "${FILE}" ]]; then
  echo "[ark_nuke] already uninstalled - init.py not found"
  exit 0
fi

if ! grep -Fqx "${TEXT}" "${FILE}"; then
  echo "[ark_nuke] already uninstalled"
else
  tmp="$(mktemp "${HOME}/.nuke/init.py.ark_nuke.XXXXXX")"
  status=0
  grep -Fvx "${TEXT}" "${FILE}" > "${tmp}" || status=$?
  if [[ "${status}" -ne 0 && "${status}" -ne 1 ]]; then
    rm -f "${tmp}"
    echo "[ark_nuke] uninstall FAILED - edit ${FILE} manually" >&2
    exit "${status}"
  fi
  mv -f "${tmp}" "${FILE}"
  echo "[ark_nuke] uninstall OK - restart Nuke"
fi

echo "----- current init.py -----"
cat "${FILE}"
echo "---------------------------"
