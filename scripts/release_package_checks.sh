#!/usr/bin/env bash
set -euo pipefail

if ! command -v python >/dev/null 2>&1; then
  echo "python is required" >&2
  exit 1
fi

if [[ -z "${SOURCE_DATE_EPOCH:-}" ]]; then
  SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)"
  export SOURCE_DATE_EPOCH
fi

echo "Using SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}"

python -m pip install --upgrade build twine

mkdir -p dist
find dist -mindepth 1 -delete

python -m build
python -m twine check dist/*

wheel_path="$(ls dist/*.whl)"
first_hash="$(sha256sum "${wheel_path}" | awk '{print $1}')"

python -m venv /tmp/femic-wheel-smoke
/tmp/femic-wheel-smoke/bin/pip install --upgrade pip
/tmp/femic-wheel-smoke/bin/pip install "${wheel_path}"
/tmp/femic-wheel-smoke/bin/femic --help >/dev/null
/tmp/femic-wheel-smoke/bin/femic instance init \
  --instance-root /tmp/femic-wheel-smoke-instance \
  --no-download-bc-vri \
  --yes >/dev/null

find dist -maxdepth 1 -name '*.whl' -delete
python -m build --wheel
wheel_path_second="$(ls dist/*.whl)"
second_hash="$(sha256sum "${wheel_path_second}" | awk '{print $1}')"

if [[ "${first_hash}" != "${second_hash}" ]]; then
  echo "Wheel reproducibility check failed: ${first_hash} != ${second_hash}" >&2
  exit 1
fi

echo "Wheel reproducibility check passed: ${second_hash}"
sha256sum dist/*
