#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
PACKAGE_NAME="com.github.khoipm06.panelscroller.plasmoid"

mkdir -p "${BUILD_DIR}"
rm -f "${BUILD_DIR}/${PACKAGE_NAME}"

cd "${ROOT_DIR}"
zip -r "${BUILD_DIR}/${PACKAGE_NAME}" metadata.json contents/ -x "*/.*" "*~" "*.swp" "*.autosave"

echo "Successfully built package: ${BUILD_DIR}/${PACKAGE_NAME}"
