#!/bin/bash
echo "=== Auto Nav Sync ==="
python3 /llm-wiki/scripts/update-nav.py
rc=$?
if [ $rc -ne 0 ]; then
  echo "ERROR: Nav update failed (exit $rc)"
  exit $rc
fi

echo "Restarting llm-wiki container..."
if command -v docker &>/dev/null && docker ps -q --filter name=llm-wiki 2>/dev/null | grep -q .; then
  docker restart llm-wiki >/dev/null 2>&1 || echo "WARNING: docker restart failed (container may not exist)"
  echo "Done at $(date)"
else
  echo "SKIPPED: Docker daemon or llm-wiki container not available"
  echo "Done at $(date)"
fi
