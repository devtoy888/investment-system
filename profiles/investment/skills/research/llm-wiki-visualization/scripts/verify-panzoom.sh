#!/bin/bash
# verify-panzoom.sh — Inline Panzoom SVG verification
# Usage: bash scripts/verify-panzoom.sh [URL]
# Default: test against the wiki's knowledge-graph page
# Checks: 18 items — DOM structure, buttons, functions, events, old-code removal, hint text
# Expected: 18/18 PASS, exit 0

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "Usage: $0 <wiki-knowledge-graph-page-url>"
  echo "Example: $0 https://wiki.example.com/concepts/knowledge-graph/"
  exit 1
fi

PASS=0; FAIL=0
log() { echo "[$1] $2"; }

echo "=== Panzoom Verification $(date) ==="
echo "URL: $URL"
echo ""

# Fetch page
HTML=$(curl -s "$URL")

if [ -z "$HTML" ]; then
  echo "FAIL: Could not fetch URL"
  exit 1
fi

# 1. Page accessibility
if curl -sI "$URL" | head -1 | grep -q "200\|302"; then
  log "PASS" "Page accessible"; PASS=$((PASS+1))
else
  log "FAIL" "Page not accessible"; FAIL=$((FAIL+1))
fi

# 2-5. Panzoom DOM structure
for elem in "pz-wrap" "pz-stage" "pz-img" "pz-level"; do
  if echo "$HTML" | grep -q "id=\"$elem\""; then
    log "PASS" "Element $elem exists"; PASS=$((PASS+1))
  else
    log "FAIL" "Element $elem missing"; FAIL=$((FAIL+1))
  fi
done

# 6-8. Control buttons
for btn in 'pzZoom(1.5)' 'pzZoom(1/1.5)' 'pzReset()'; do
  if echo "$HTML" | grep -q "onclick=\"$btn\""; then
    log "PASS" "Button $btn exists"; PASS=$((PASS+1))
  else
    log "FAIL" "Button $btn missing"; FAIL=$((FAIL+1))
  fi
done

# 9. SVG image reference
if echo "$HTML" | grep -qi "svg"; then
  log "PASS" "SVG image reference found"; PASS=$((PASS+1))
else
  log "FAIL" "No SVG reference"; FAIL=$((FAIL+1))
fi

# 10-11. JavaScript functions
for fn in "window.pzZoom" "window.pzReset"; do
  if echo "$HTML" | grep -q "$fn"; then
    log "PASS" "Function $fn defined"; PASS=$((PASS+1))
  else
    log "FAIL" "Function $fn missing"; FAIL=$((FAIL+1))
  fi
done

# 12-15. Event listeners
for evt in "wheel" "mousedown" "dblclick" "touchstart"; do
  if echo "$HTML" | grep -q "addEventListener.*$evt"; then
    log "PASS" "Event $evt bound"; PASS=$((PASS+1))
  else
    log "FAIL" "Event $evt missing"; FAIL=$((FAIL+1))
  fi
done

# 16-17. Old Lightbox removed
for old in "lb-overlay" "openLightbox"; do
  if echo "$HTML" | grep -q "$old"; then
    log "FAIL" "Old code $old still present"; FAIL=$((FAIL+1))
  else
    log "PASS" "Old code $old removed"; PASS=$((PASS+1))
  fi
done

# 18. Hint text present
if echo "$HTML" | grep -qE "滚轮缩放|scroll.*zoom|zoom.*pan"; then
  log "PASS" "Usage hint text present"; PASS=$((PASS+1))
else
  log "FAIL" "No usage hint text"; FAIL=$((FAIL+1))
fi

echo ""
echo "=== Results ==="
echo "PASS: $PASS | FAIL: $FAIL | Total: $((PASS+FAIL))"
echo "Date: $(date '+%Y-%m-%d %H:%M')"
if [ $FAIL -eq 0 ]; then
  echo "Status: ALL PASSED"
  exit 0
else
  echo "Status: FAILURES DETECTED"
  exit 1
fi
