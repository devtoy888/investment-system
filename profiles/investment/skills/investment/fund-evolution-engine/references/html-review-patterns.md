Covered in `investment-assistant`s `references/report-html-rendering.md`. This skill's review_engine.py and push_report_r2.py implement the patterns described there.

Key file paths (relative to /opt/data/scripts/):
- `review_engine.py` — daily review cycle (runs at 17:00)
- `push_report_r2.py` — HTML/MD generation + R2 upload
- `report_manager.py` — structured storage by year/month/day + index.json