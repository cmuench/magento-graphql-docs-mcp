#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"
SCRIPT_PATH="${SCRIPT_DIR}/$(basename "$0")"

DOCKER_BIN="${DOCKER_BIN:-docker}"
IMAGE="${MAGENTO_GRAPHQL_DOCS_IMAGE:-magento-graphql-docs-mcp}"
DOCKERFILE_PATH="${PROJECT_ROOT}/docker/Dockerfile"
HOST_DOCS_PATH="${MAGENTO_GRAPHQL_DOCS_PATH:-${PROJECT_ROOT}/data}"
AUTO_FETCH="${MAGENTO_GRAPHQL_DOCS_AUTO_FETCH:-true}"

if ! command -v "${DOCKER_BIN}" >/dev/null 2>&1; then
  echo "Error: docker is not installed or not on PATH." >&2
  exit 1
fi

ensure_image() {
  if ! "${DOCKER_BIN}" image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "Docker image ${IMAGE} not found. Building using context ${PROJECT_ROOT} (Dockerfile: ${DOCKERFILE_PATH})..."
    "${DOCKER_BIN}" build -t "${IMAGE}" -f "${DOCKERFILE_PATH}" "${PROJECT_ROOT}"
  fi
}

docker_args=(run --rm -i)
docker_args+=(-e "MAGENTO_GRAPHQL_DOCS_AUTO_FETCH=${AUTO_FETCH}")

if [ -n "${MAGENTO_GRAPHQL_DOCS_DB_PATH:-}" ]; then
  docker_args+=(-e "MAGENTO_GRAPHQL_DOCS_DB_PATH=${MAGENTO_GRAPHQL_DOCS_DB_PATH}")
fi

DOCS_MESSAGE="No docs mounted. Container will rely on MAGENTO_GRAPHQL_DOCS_AUTO_FETCH=${AUTO_FETCH}."
if [ -n "${HOST_DOCS_PATH}" ] && [ -d "${HOST_DOCS_PATH}" ]; then
  DOCS_ABS="$(cd "${HOST_DOCS_PATH}" && pwd)"
  docker_args+=(-v "${DOCS_ABS}:/data")
  docker_args+=(-e "MAGENTO_GRAPHQL_DOCS_PATH=/data")
  DOCS_MESSAGE="Docs mounted from ${DOCS_ABS} -> /data (MAGENTO_GRAPHQL_DOCS_PATH=/data inside container)."
fi

docker_args+=("${IMAGE}")
docker_args+=("$@")

cat <<EOF
Magento GraphQL Docs MCP (Docker)
- STDIO bridge (no TTY). Point your MCP client command to: ${SCRIPT_PATH}
- Example: set command to ${SCRIPT_PATH} in Claude Desktop config
- Host doc path (mounted to /data): ${HOST_DOCS_PATH}
- Auto-fetch in container: ${AUTO_FETCH} (set MAGENTO_GRAPHQL_DOCS_AUTO_FETCH=false to disable)
${DOCS_MESSAGE}
Image: ${IMAGE}

Starting container and forwarding STDIN/STDOUT...
EOF

ensure_image
exec "${DOCKER_BIN}" "${docker_args[@]}"
