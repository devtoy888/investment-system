#!/usr/bin/env python3
"""Auto-rebuild knowledge graph and deploy to website."""
import subprocess, sys, json, shutil
from pathlib import Path

WIKI_DIR = Path('/llm-wiki')
VENV_PY = WIKI_DIR / 'scripts/.graphify-venv/bin/python3'
BUILD = WIKI_DIR / 'scripts/build-graph.py'
GOUT = WIKI_DIR / 'graphify-out'
DIMG = WIKI_DIR / 'docs/images'
DDAT = WIKI_DIR / 'docs/data/graph'

def run(cmd, timeout=300):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        print(f'ERR: {r.stderr[:300]}'); return False
    return True

print('Building graph...')
if not run([str(VENV_PY), str(BUILD)]): sys.exit(1)

with open(GOUT / 'graph.json') as f:
    data = json.load(f)
n, e = len(data['nodes']), len(data['links'])

DIMG.mkdir(parents=True, exist_ok=True)
DDAT.mkdir(parents=True, exist_ok=True)
shutil.copy2(GOUT / 'graph.svg', DIMG / 'knowledge-graph.svg')
shutil.copy2(GOUT / 'graph.json', DDAT / 'graph.json')

print(f'OK: {n} nodes, {e} edges')
r = subprocess.run(['docker', 'restart', 'llm-wiki'], capture_output=True, text=True, timeout=30)
print('mkdocs restarted' if r.returncode == 0 else f'restart err: {r.stderr}')
