#!/usr/bin/env python3
"""
Wiki Lint — 自动化 Wiki 健康检查 + 安全自动修复

检查项：
  1. 孤儿页面（不被任何页面引用的页面）
  2. 损坏的 [[wikilinks]]（指向不存在的文件）
  3. Frontmatter 完整性（title/created/updated/type/tags/sources）
  4. 过期内容（updated 超过30天未更新）
  5. Index 遗漏（目录下文件未被 index.md 收录）
  6. 矛盾内容标记（contested: true 页面）

自动修复策略（仅 --apply 时执行）：
  ✅ 安全可自动修复：
     - frontmatter 缺字段 -> 自动补全（title 从文件名推断、created/updated 用文件 mtime、
       type 从目录映射、tags/sources 给空数组）。纯追加，不删不改已有字段。
  ⚠️ 仅报告（有歧义或破坏性，需人判断）：
     - broken_wikilinks / stale_pages / index_misses / orphan_pages / contested_pages

用法:
  python3 lint-wiki.py            # 只报告（默认）
  python3 lint-wiki.py --apply    # 报告 + 自动修复 frontmatter 缺字段，修复后自动重启容器
"""
import os, re, json, argparse, subprocess
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

WIKI_DIR = Path('/llm-wiki/docs')
EXCLUDE_DIRS = {'graphify-out', 'data', 'node_modules'}
EXCLUDE_FILES = {'SCHEMA.md', 'setup-guide.md', 'log.md', 'wiki-repair-changelog.md'}
NOW = datetime.now(timezone.utc)
MAX_AGE_DAYS = 30
REQUIRED_FIELDS = ['title', 'created', 'updated', 'type', 'tags', 'sources']
VALID_TYPES = {'concept', 'entity', 'comparison', 'query', 'index', 'raw', 'source'}

DIR_TYPE_MAP = {
    'concepts': 'concept',
    'entities': 'entity',
    'comparisons': 'comparison',
    'queries': 'query',
    'raw': 'raw',
    'sources': 'source',
}

results = {
    'pages_total': 0,
    'orphan_pages': [],
    'broken_wikilinks': [],
    'frontmatter_issues': [],
    'stale_pages': [],
    'index_misses': [],
    'contested_pages': [],
}
fixed_files = []


def infer_title(rel):
    stem = Path(rel).stem
    title = re.sub(r'[-_]', ' ', stem)
    title = title.replace('gb t', 'GB/T')
    return title.strip().title() if not re.search(r'[一-鿿]', title) else title.strip()


def infer_type(rel):
    return DIR_TYPE_MAP.get(rel.split('/')[0], 'concept')


def auto_fix_frontmatter(rel, path, missing):
    content = path.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return False
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    fm_text = parts[1]
    body = parts[2]
    additions = []
    stem = Path(rel).stem
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    date_str = mtime.strftime('%Y-%m-%d')
    if 'title' in missing:
        additions.append('title: ' + infer_title(rel))
    if 'created' in missing:
        additions.append('created: ' + date_str)
    if 'updated' in missing:
        additions.append('updated: ' + date_str)
    if 'type' in missing:
        additions.append('type: ' + infer_type(rel))
    if 'tags' in missing:
        additions.append('tags: []')
    if 'sources' in missing:
        additions.append('sources: []')
    if not additions:
        return False
    new_fm = fm_text.rstrip() + '\n' + '\n'.join(additions) + '\n'
    path.write_text('---\n' + new_fm + '---' + body, encoding='utf-8')
    return True


def main():
    parser = argparse.ArgumentParser(description='Wiki Lint + safe auto-fix')
    parser.add_argument('--apply', action='store_true',
                        help='Apply safe auto-fixes (frontmatter field completion) and restart container if fixed')
    args = parser.parse_args()
    AUTO_FIX = args.apply

    all_files = []
    file_set = set()
    for p in WIKI_DIR.rglob('*.md'):
        rel = str(p.relative_to(WIKI_DIR))
        parts = rel.split('/')
        if any(d in parts for d in EXCLUDE_DIRS):
            continue
        if rel in EXCLUDE_FILES:
            continue
        all_files.append((rel, p))
        file_set.add(rel)
    results['pages_total'] = len(all_files)

    page_wikilinks = {}
    wikilink_targets = defaultdict(set)
    for rel, path in all_files:
        content = path.read_text(encoding='utf-8')
        _content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        _content = re.sub(r'`[^`]*`', '', _content)
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', _content)
        targets = set()
        resolved_targets = set()
        src_dir = os.path.dirname(rel)
        for wl in links:
            target = wl.strip()
            if not target.endswith('.md'):
                target += '.md'
            targets.add(target)
            resolved = os.path.normpath(os.path.join(src_dir, target))
            if resolved in file_set:
                resolved_targets.add(resolved)
            elif target in file_set:
                resolved_targets.add(target)
            else:
                fname_only = target.split('/')[-1]
                alt = os.path.normpath(os.path.join(src_dir, fname_only))
                if alt in file_set:
                    resolved_targets.add(alt)
                else:
                    resolved_targets.add(target)
        page_wikilinks[rel] = targets
        for t in resolved_targets:
            wikilink_targets[t].add(rel)

    _nav_text = (WIKI_DIR.parent / 'mkdocs.yml').read_text(encoding='utf-8') if (WIKI_DIR.parent / 'mkdocs.yml').exists() else ''
    _nav_files = set(re.findall(r':\s*([\w/一-鿿.-]+\.md)', _nav_text))
    _nav_files.update(re.findall(r'([\w/一-鿿.-]+\.md)', _nav_text))

    for rel, _ in all_files:
        if rel.endswith('index.md') or rel == 'index.md':
            continue
        if rel.split('/')[0] in ('raw', 'sources'):
            continue
        if rel in _nav_files:
            continue
        incoming = wikilink_targets.get(rel, set())
        incoming = {s for s in incoming if s != rel}
        if not incoming:
            results['orphan_pages'].append({'file': rel, 'severity': 'warn'})

    # Build stem -> full path mapping for Obsidian-style wikilink resolution
    # Build stem -> full path mapping (includes ALL .md files for wikilink resolution)
    stem_to_path = {}
    for _p in WIKI_DIR.rglob('*.md'):
        _rel = str(_p.relative_to(WIKI_DIR))
        _stem = _p.stem
        stem_to_path[_stem] = _rel

    for rel, targets in page_wikilinks.items():
        src_dir = os.path.dirname(rel)
        for t in targets:
            resolved = os.path.normpath(os.path.join(src_dir, t))
            if resolved in file_set:
                continue
            if t in file_set:
                continue
            fname_only = t.split('/')[-1]
            if os.path.normpath(os.path.join(src_dir, fname_only)) in file_set:
                continue
            # Try: stem-based match (Obsidian-style)
            stem = Path(t).stem
            if stem in stem_to_path:
                continue
            results['broken_wikilinks'].append({'source': rel, 'target': t, 'severity': 'error'})

    for rel, path in all_files:
        content = path.read_text(encoding='utf-8')
        rel_parts = rel.split('/')
        if rel_parts[0] in ('raw', 'sources'):
            continue
        if not content.startswith('---'):
            results['frontmatter_issues'].append({'file': rel, 'issue': 'No frontmatter block', 'severity': 'error'})
            continue
        parts = content.split('---', 2)
        if len(parts) < 3:
            results['frontmatter_issues'].append({'file': rel, 'issue': 'Malformed frontmatter (no closing ---)', 'severity': 'error'})
            continue
        fm_text = parts[1]
        missing = []
        for field in REQUIRED_FIELDS:
            pattern = re.compile(r'^' + re.escape(field) + r'\s*:', re.MULTILINE)
            if not pattern.search(fm_text):
                missing.append(field)
        if missing:
            results['frontmatter_issues'].append({'file': rel, 'issue': f'Missing: {", ".join(missing)}', 'severity': 'error'})
            if AUTO_FIX:
                if auto_fix_frontmatter(rel, path, missing):
                    fixed_files.append({'file': rel, 'added': missing})
        type_match = re.search(r'^type\s*:\s*(\S+)', fm_text, re.MULTILINE)
        if type_match and type_match.group(1) not in VALID_TYPES:
            results['frontmatter_issues'].append({'file': rel, 'issue': f"Invalid type: '{type_match.group(1)}'", 'severity': 'warn'})

    for rel, path in all_files:
        content = path.read_text(encoding='utf-8')
        if not content.startswith('---'):
            continue
        parts = content.split('---', 2)
        if len(parts) < 3:
            continue
        fm_text = parts[1]
        updated_match = re.search(r'^updated\s*:\s*(\S+)', fm_text, re.MULTILINE)
        if updated_match:
            date_str = updated_match.group(1)
            try:
                d = datetime.fromisoformat(date_str)
                if d.tzinfo is None:
                    d = d.replace(tzinfo=timezone.utc)
                days_old = (NOW - d).days
                if days_old > MAX_AGE_DAYS:
                    results['stale_pages'].append({'file': rel, 'updated': date_str, 'days_old': days_old, 'severity': 'warn'})
            except ValueError:
                results['frontmatter_issues'].append({'file': rel, 'issue': f"Invalid updated date: '{date_str}'", 'severity': 'warn'})

    dir_files = defaultdict(list)
    for rel, _ in all_files:
        if rel.endswith('index.md') or rel == 'index.md':
            continue
        d = os.path.dirname(rel)
        dir_files[d].append(rel)
    for dir_path, files in dir_files.items():
        index_rel = f'{dir_path}/index.md' if dir_path else 'index.md'
        if index_rel not in file_set:
            continue
        index_path = WIKI_DIR / index_rel
        index_content = index_path.read_text(encoding='utf-8')
        for f in files:
            fname = Path(f).stem
            if fname not in index_content:
                results['index_misses'].append({'file': f, 'index': index_rel, 'severity': 'warn'})

    for rel, path in all_files:
        content = path.read_text(encoding='utf-8')
        if 'contested: true' in content:
            results['contested_pages'].append({'file': rel, 'severity': 'info'})

    print('=' * 60)
    print('  Wiki Lint Report' + ('  [AUTO-FIX MODE]' if AUTO_FIX else ''))
    print(f'  Pages scanned: {results["pages_total"]}')
    print('=' * 60)
    print()
    severity_counts = defaultdict(int)
    for check_name, items in results.items():
        if check_name in ('pages_total',):
            continue
        if not items:
            print(f'✅ {check_name}: 0 issues')
            continue
        sevs = defaultdict(int)
        for item in items:
            sev = item.get('severity', 'info')
            sevs[sev] += 1
            severity_counts[sev] += 1
        total = len(items)
        sev_str = ', '.join(f'{k}={v}' for k, v in sorted(sevs.items()))
        print(f'⚠️  {check_name}: {total} issues ({sev_str})')
        for item in items[:5]:
            if check_name == 'orphan_pages':
                print(f'    📄 {item["file"]}')
            elif check_name == 'broken_wikilinks':
                print(f'    🔗 {item["source"]} -> ❌ {item["target"]}')
            elif check_name == 'frontmatter_issues':
                print(f'    📋 {item["file"]}: {item["issue"]}')
            elif check_name == 'stale_pages':
                print(f'    ⏰ {item["file"]}: {item["days_old"]}d old')
            elif check_name == 'index_misses':
                print(f'    🏷️  {item["file"]} not in {item["index"]}')
            elif check_name == 'contested_pages':
                print(f'    ⚠️  {item["file"]}')
        if total > 5:
            print(f'    ... and {total - 5} more')
        print()

    print('=' * 60)
    total_issues = sum(severity_counts.values())
    print(f'  Total issues: {total_issues}')
    for sev in ['error', 'warn', 'info']:
        if severity_counts[sev] > 0:
            print(f'    {sev}: {severity_counts[sev]}')
    print('=' * 60)

    if AUTO_FIX:
        if fixed_files:
            print(f'\n🔧 AUTO-FIXED {len(fixed_files)} files (frontmatter fields appended):')
            for f in fixed_files:
                print(f'    ✅ {f["file"]}: +{", ".join(f["added"])}')
            try:
                r = subprocess.run(['docker', 'restart', 'llm-wiki'], capture_output=True, text=True, timeout=60)
                if r.returncode == 0:
                    print('    🔄 docker restart llm-wiki: OK')
                else:
                    print(f'    ⚠️  docker restart failed: {r.stderr[:100]}')
            except Exception as e:
                print(f'    ⚠️  docker restart skipped: {e}')
        else:
            print('\n🔧 AUTO-FIX: nothing to fix')

    out_path = WIKI_DIR / 'lint-report.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\nJSON report saved to {out_path}')


if __name__ == '__main__':
    main()
