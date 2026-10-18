#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
VERSION="${1:-$(grep -o '"Version": "[^"]*"' "${ROOT_DIR}/metadata.json" | cut -d'"' -f4)}"
PACKAGE_NAME="com.github.khoipm06.panelscroller.plasmoid"
VERSIONED_PACKAGE_NAME="com.github.khoipm06.panelscroller-${VERSION}.plasmoid"

mkdir -p "${BUILD_DIR}"
rm -f "${BUILD_DIR}/${PACKAGE_NAME}" "${BUILD_DIR}/${VERSIONED_PACKAGE_NAME}"

cd "${ROOT_DIR}"
zip -r "${BUILD_DIR}/${PACKAGE_NAME}" metadata.json contents/ -x "*/.*" "*~" "*.swp" "*.autosave"
cp "${BUILD_DIR}/${PACKAGE_NAME}" "${BUILD_DIR}/${VERSIONED_PACKAGE_NAME}"

echo "Successfully built package v${VERSION}:"
echo "  - ${BUILD_DIR}/${PACKAGE_NAME}"
echo "  - ${BUILD_DIR}/${VERSIONED_PACKAGE_NAME}"
