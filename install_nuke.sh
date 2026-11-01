#!/usr/bin/env bash
# Unix counterpart of install_nuke.cmd ? append pluginAddPath to ~/.nuke/init.py
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TEXT="nuke.pluginAddPath(r'${ROOT}')"
FILE="${HOME}/.nuke/init.py"

mkdir -p "${HOME}/.nuke"
if [[ ! -f "${FILE}" ]]; then
  printf 'import nuke\n' > "${FILE}"
fi

if grep -Fqx "${TEXT}" "${FILE}"; then
  echo "[ark_nuke] already installed"
else
  printf '\n%s\n' "${TEXT}" >> "${FILE}"
  echo "[ark_nuke] install OK ? restart Nuke"
fi

echo "----- current init.py -----"
cat "${FILE}"
echo "---------------------------"
