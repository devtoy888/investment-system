#!/usr/bin/env bash
# Wrapper: morning briefing - collect data + send cards
set -e
cd /opt/data/scripts
python3 collect_morning_data.py
PYTHONPATH=/opt/data/.feishu-deps python3 send_morning_cards.py
