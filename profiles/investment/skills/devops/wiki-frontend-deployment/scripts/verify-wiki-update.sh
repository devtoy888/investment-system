#!/bin/bash
# verify-wiki-update.sh — Post-update verification for LLM Wiki
# Usage: ./scripts/verify-wiki-update.sh
# Checks SVG font integrity, page structure, and container sync.
# Exit code: 0 = all passed, 1+ = issues found

set -e
errors=0

echo "=== LLM Wiki Update Verification ==="
echo ""

# 1. SVG font check (on host)
SVG_FILE="docs/images/knowledge-graph.svg"
if [ -f "$SVG_FILE" ]; then
    echo "[1/4] SVG host file check: $SVG_FILE"
    SIZE=$(stat -c%s "$SVG_FILE" 2>/dev/null || stat -f%z "$SVG_FILE" 2>/dev/null)
    echo "  Size: $SIZE bytes"
    
    LXGW=$(grep -o 'LXGWWenKai-' "$SVG_FILE" | wc -l)
    WQY=$(grep -o 'WenQuanYi-' "$SVG_FILE" | wc -l)
    DJVU=$(grep -o 'DejaVuSans-' "$SVG_FILE" | wc -l)
    
    echo "  LXGW WenKai glyphs: $LXGW"
    echo "  WenQuanYi glyphs: $WQY"
    echo "  DejaVuSans glyphs: $DJVU"
    
    if [ "$LXGW" -eq 0 ] && [ "$WQY" -eq 0 ] && [ "$DJVU" -gt 0 ]; then
        echo "  ❌ SVG uses DejaVuSans — Chinese will show as boxes"
        errors=$((errors+1))
    elif [ "$WQY" -gt 0 ]; then
        echo "  ⚠️ SVG uses WenQuanYi TTC — may have glyph offset issues"
    elif [ "$LXGW" -gt 0 ]; then
        echo "  ✅ LXGW WenKai font OK"
    else
        echo "  ⚠️ No recognized CJK font paths found"
    fi
else
    echo "[1/4] ❌ SVG file not found: $SVG_FILE"
    errors=$((errors+1))
fi
echo ""

# 2. Page structure check
PAGE_FILE="docs/concepts/knowledge-graph.md"
if [ -f "$PAGE_FILE" ]; then
    echo "[2/4] Page structure check: $PAGE_FILE"
    for section in "图谱概览" "社区分类" "可视化文件" "自动分类机制" "查看图谱"; do
        if grep -q "$section" "$PAGE_FILE"; then
            echo "  ✅ Section: $section"
        else
            echo "  ❌ Missing section: $section"
            errors=$((errors+1))
        fi
    done
    for component in "openLightbox()" "lbZoomIn()" "lbZoomOut()" "lbReset()" "closeLightbox()"; do
        if grep -q "$component" "$PAGE_FILE"; then
            echo "  ✅ Lightbox: $component"
        else
            echo "  ❌ Lightbox missing: $component"
            errors=$((errors+1))
        fi
    done
else
    echo "[2/4] ❌ Page file not found: $PAGE_FILE"
    errors=$((errors+1))
fi
echo ""

# 3. Container file sync check
CONTAINER="llm-wiki"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^$CONTAINER\$"; then
    echo "[3/4] Container sync check: $CONTAINER"
    # Try both possible paths: /docs/images/ and /docs/docs/images/
    for _svg_path in "/docs/docs/images/knowledge-graph.svg" "/docs/images/knowledge-graph.svg"; do
        CONTENT=$(docker exec "$CONTAINER" sh -c "test -f $_svg_path && head -c 500 $_svg_path" 2>/dev/null || true)
        if [ -n "$CONTENT" ]; then
            echo "  Container path: $_svg_path"
            break
        fi
    done
    if [ -n "$CONTENT" ]; then
        if echo "$CONTENT" | grep -q 'LXGWWenKai'; then
            echo "  ✅ Container has LXGW WenKai SVG"
        elif echo "$CONTENT" | grep -q 'WenQuanYi'; then
            echo "  ⚠️ Container has WenQuanYi SVG (old version?) — restart may be needed"
        else
            echo "  ❌ Container SVG has no CJK font paths"
            errors=$((errors+1))
        fi
    else
        echo "  ❌ Container SVG not found — check volume mount path"
        errors=$((errors+1))
    fi
else
    echo "[3/4] ⚠️ Container $CONTAINER not running — skip"
fi
echo ""

# 4. Graphify build script font config check
BUILD_SCRIPT="scripts/build-graph.py"
if [ -f "$BUILD_SCRIPT" ]; then
    echo "[4/4] Build script check: $BUILD_SCRIPT"
    if grep -q 'wqy-zenhei' "$BUILD_SCRIPT"; then
        echo "  ⚠️ Still using WenQuanYi TTC — consider switching to TTF"
    elif grep -q 'WenKai' "$BUILD_SCRIPT"; then
        echo "  ✅ LXGW WenKai configured"
    elif grep -q 'font.sans-serif' "$BUILD_SCRIPT"; then
        echo "  ⚠️ CJK font configured but not LXGW WenKai — check compatibility"
    fi
else
    echo "[4/4] ⚠️ No build script found — skip"
fi

echo ""
echo "=== Results ==="
if [ "$errors" -eq 0 ]; then
    echo "✅ All checks passed"
    exit 0
else
    echo "❌ $errors issue(s) found"
    exit "$errors"
fi
