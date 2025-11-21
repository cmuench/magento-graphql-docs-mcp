#!/usr/bin/env sh
set -euo pipefail

DOCS_PATH="${MAGENTO_GRAPHQL_DOCS_PATH:-/data}"
AUTO_FETCH="${MAGENTO_GRAPHQL_DOCS_AUTO_FETCH:-true}"
CLONE_ROOT="/tmp/commerce-webapi"
CLONE_TARGET="${CLONE_ROOT}/src/pages/graphql"

has_docs() {
  [ -d "$DOCS_PATH" ] && find "$DOCS_PATH" -maxdepth 1 -name "*.md" -print -quit | grep -q .
}

if ! has_docs && [ "$AUTO_FETCH" = "true" ]; then
  echo "Docs not found at ${DOCS_PATH}. Auto-fetch enabled; cloning commerce-webapi..."
  rm -rf "$CLONE_ROOT"
  git clone --depth=1 https://github.com/AdobeDocs/commerce-webapi.git "$CLONE_ROOT"
  export MAGENTO_GRAPHQL_DOCS_PATH="$CLONE_TARGET"
  echo "Docs cloned to ${MAGENTO_GRAPHQL_DOCS_PATH}"
fi

exec "$@"
