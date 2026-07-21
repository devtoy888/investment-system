#!/bin/bash
set -e
echo "=== Nightly Wiki Build: $(date) ==="

# Step 1: Full graph rebuild (build + enrich + deploy, no restart inside)
echo "[1/3] Rebuilding knowledge graph..."
python3 /llm-wiki/scripts/rebuild-graph.py

# Step 2: Update navigation
echo "[2/3] Updating navigation..."
python3 /llm-wiki/scripts/update-nav.py

# Step 3: Single restart
echo "[3/3] Restarting llm-wiki..."
docker restart llm-wiki

echo "=== Done at $(date) ==="
