#!/bin/bash
# Panzoom inline zoom component verification
# Usage: bash verify-panzoom.sh [URL]
# Checks 18 items: DOM structure, buttons, functions, events, old-code removal
# Based on implementation in llm-wiki-visualization skill

URL="${1:-https://wiki.example.com/concepts/knowledge-graph/}"
PASS=0; FAIL=0
log() { echo "[$1] $2"; }

echo "=== Panzoom Verification $(date) ==="
echo "URL: $URL"
HTML=$(curl -s "$URL")

# Page access
curl -sI "$URL" | head -1 | grep -q "200\|302" && { log "PASS" "Page accessible"; PASS=$((PASS+1)); } || { log "FAIL" "Page inaccessible"; FAIL=$((FAIL+1)); }

# Panzoom elements
for elem in "pz-wrap" "pz-stage" "pz-img" "pz-level"; do
  echo "$HTML" | grep -q "id=\"$elem\"" && { log "PASS" "Element $elem exists"; PASS=$((PASS+1)); } || { log "FAIL" "Element $elem missing"; FAIL=$((FAIL+1)); }
done

# Buttons
for btn in 'pzZoom(1.5)' 'pzZoom(1/1.5)' 'pzReset()'; do
  echo "$HTML" | grep -q "onclick=\"$btn\"" && { log "PASS" "Button $btn exists"; PASS=$((PASS+1)); } || { log "FAIL" "Button $btn missing"; FAIL=$((FAIL+1)); }
done

# SVG reference
echo "$HTML" | grep -q "knowledge-graph.svg" && { log "PASS" "SVG reference exists"; PASS=$((PASS+1)); } || { log "FAIL" "SVG reference missing"; FAIL=$((FAIL+1)); }

# Functions
for fn in "window.pzZoom" "window.pzReset"; do
  echo "$HTML" | grep -q "$fn" && { log "PASS" "$fn defined"; PASS=$((PASS+1)); } || { log "FAIL" "$fn missing"; FAIL=$((FAIL+1)); }
done

# Events
for evt in "wheel" "mousedown" "dblclick" "touchstart"; do
  echo "$HTML" | grep -q "addEventListener.*$evt" && { log "PASS" "$evt event bound"; PASS=$((PASS+1)); } || { log "FAIL" "$evt event missing"; FAIL=$((FAIL+1)); }
done

# Old Lightbox removed
echo "$HTML" | grep -q "lb-overlay" && { log "FAIL" "Old Lightbox remains"; FAIL=$((FAIL+1)); } || { log "PASS" "Old Lightbox removed"; PASS=$((PASS+1)); }
echo "$HTML" | grep -q "openLightbox" && { log "FAIL" "Old openLightbox remains"; FAIL=$((FAIL+1)); } || { log "PASS" "Old openLightbox removed"; PASS=$((PASS+1)); }

# Hint text
echo "$HTML" | grep -q "滚轮缩放" && { log "PASS" "Hint text exists"; PASS=$((PASS+1)); } || { log "FAIL" "Hint text missing"; FAIL=$((FAIL+1)); }

echo ""
echo "=== Results: $PASS/$((PASS+FAIL)) passed ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
