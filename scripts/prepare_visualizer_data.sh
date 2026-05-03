#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_FILE="${ROOT_DIR}/data/results/analysis.json"
TARGET_DIR="${ROOT_DIR}/visualizer/src/assets"
TARGET_FILE="${TARGET_DIR}/analysis.json"

if [[ ! -f "${SOURCE_FILE}" ]]; then
  echo "ERROR: No existe ${SOURCE_FILE}. Ejecuta Analyzer antes." >&2
  exit 1
fi

mkdir -p "${TARGET_DIR}"
cp "${SOURCE_FILE}" "${TARGET_FILE}"
echo "OK: Copiado ${SOURCE_FILE} -> ${TARGET_FILE}"
