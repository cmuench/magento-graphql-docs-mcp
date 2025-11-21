# Minimal image to run the Magento GraphQL Docs MCP server.
# Default behavior: mount docs into /data. If not mounted and auto-fetch is enabled,
# the entrypoint clones the docs into /tmp/commerce-webapi and updates MAGENTO_GRAPHQL_DOCS_PATH.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MAGENTO_GRAPHQL_DOCS_PATH=/data \
    MAGENTO_GRAPHQL_DOCS_AUTO_FETCH=true

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install server and dependencies
COPY . /app
RUN pip install --no-cache-dir .

COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["magento-graphql-docs-mcp"]
