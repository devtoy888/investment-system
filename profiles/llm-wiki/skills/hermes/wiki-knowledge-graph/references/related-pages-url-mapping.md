# related-pages.js URL Mapping Generator

When new pages are added to the wiki, the `PAGE_URLS`, `INDEX_URLS`, and `LABEL_MAP` in `related-pages.v{N}.js` become stale. Regenerate them with this script.

## Script

```python
import os, json

docs_dir = '/llm-wiki/docs'
exclude_dirs = {'data', 'stylesheets', 'javascripts', 'images', '__pycache__'}
exclude_files = {'wiki-repair-changelog.md'}

files = []
for root, dirs, fnames in os.walk(docs_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
    for f in fnames:
        if not f.endswith('.md'): continue
        if f in exclude_files: continue
        rel = os.path.relpath(os.path.join(root, f), docs_dir)
        files.append(rel)

page_urls = {}
index_urls = {}
label_map = {}

for rel in files:
    fn = os.path.basename(rel)
    fn_stem = fn.replace('.md', '')
    dirname = os.path.dirname(rel)
    
    if fn == 'index.md':
        url = '/' if dirname == '' else '/' + dirname.replace(os.sep, '/') + '/'
        key = 'root' if dirname == '' else dirname.replace(os.sep, '/')
        index_urls[key] = url
        page_urls[fn_stem] = url
        # Friendly labels for index pages
        NAME_OVERRIDES = {
            '': '首页', 'entities': '实体索引', 'concepts': '概念索引',
            'comparisons': '对比分析', 'queries': '查询归档', 'raw': '原始文档'
        }
        label_map[rel] = NAME_OVERRIDES.get(dirname, os.path.basename(dirname) + ' 索引')
    else:
        url = '/' + rel.replace('.md', '').replace(os.sep, '/') + '/'
        page_urls[fn_stem] = url

# Output as JS variable declarations
def js_dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

print(f'var PAGE_URLS = {js_dump(page_urls)};')
print(f'var INDEX_URLS = {js_dump(index_urls)};')
print(f'var LABEL_MAP = {js_dump(label_map)};')
```

## Integration with deployment pipeline

After adding new pages and rebuilding the graph, regenerate the URL mapping and inject it into the JS:

```bash
python3 /llm-wiki/scripts/.graphify-venv/bin/python3 \
  /llm-wiki/scripts/generate-url-mapping.py \
  > /tmp/url_mapping.js

# Extract and insert into related-pages.v{N}.js
# (or regenerate the entire JS file)
```

## Pitfall: duplicate `index` key

Multiple `index.md` files (one per directory) each map to key `"index"` in `PAGE_URLS`, but dict keys must be unique — only the last one processed survives. The script handles this by also storing index page URLs separately in `INDEX_URLS` keyed by directory path. But `PAGE_URLS["index"]` will always point to the LAST `index.md` found, which is wrong for all others.

**Fix**: The `getUrlForNode()` JS function checks `source_file.endsWith("index.md")` first and looks up `INDEX_URLS` by directory, never relying on `PAGE_URLS["index"]`.

