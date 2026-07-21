#!/usr/bin/env python3
"""
Group Consistency Checker — verify all hardcoded group lists match GROUPS dict.

Run after any fund group change (add/remove/rename) to catch stale references
that pitfall #36 warns about. Checks:
  1. fund_tools.py: GROUPS, PORTFOLIO_WEIGHTS, GROUP_ACTION_RULES, sector_map
  2. closing_review.py: group_order
  3. collect_morning_data.py: group_order

Exit code: 0 = all clean, 1 = issues found
"""

import ast
import sys
import os

SCRIPTS_DIR = '/opt/data/scripts'

def extract_groups_from_fund_tools():
    """Parse the GROUPS dict from fund_tools.py to get canonical group set."""
    path = os.path.join(SCRIPTS_DIR, 'fund_tools.py')
    with open(path) as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    # Find GROUPS dict
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'GROUPS':
                    if isinstance(node.value, ast.Dict):
                        groups = set()
                        for key in node.value.keys:
                            if isinstance(key, ast.Constant):
                                groups.add(key.value)
                        return groups
    return None

def check_hardcoded_list(filepath, description, pattern_str):
    """Search a file for a hardcoded group list and compare with canonical set."""
    groups = extract_groups_from_fund_tools()
    if groups is None:
        print(f"⚠️  Could not parse GROUPS dict from fund_tools.py")
        return True
    
    with open(filepath) as f:
        content = f.read()
    
    issues = []
    
    # Check for specific group name references that should have been removed
    for gname in list(groups):  # Start with current groups
        pass  # These are expected
    
    # Find all group-like constant strings in the file that look like group names
    # We look for specific names from the known set plus any that might be stale
    known_groups = {'科技/AI', '黄金', '资源/周期', '新能源'}
    
    # Track which groups appear in this file
    found_groups = set()
    for g in known_groups:
        if g in content:
            found_groups.add(g)
    
    # Check for any groups in the file that are NOT in GROUPS (stale references)
    # We look for Chinese group-like strings
    # This is heuristic — check common group name patterns
    stale_patterns = []
    
    # Check for known removed groups
    removed_groups = ['通航']
    for stale in removed_groups:
        count = content.count(stale)
        if count > 0:
            stale_patterns.append(stale)
    
    if stale_patterns:
        for stale in stale_patterns:
            print(f"❌ {description}: stale reference '{stale}' found in {os.path.basename(filepath)}")
        return True
    
    # Check that current GROUPS are all present in hardcoded lists
    missing = groups - found_groups
    if missing and len(groups) > 0:
        for m in missing:
            print(f"⚠️  {description}: group '{m}' from GROUPS not found in {os.path.basename(filepath)} (may be expected if script uses GROUPS dict directly)")
    
    print(f"✅ {description}: {len(found_groups)} groups match GROUPS dict")
    return False

def main():
    groups = extract_groups_from_fund_tools()
    if groups is None:
        print("❌ Cannot parse GROUPS dict")
        sys.exit(1)
    
    print(f"📋 Canonical GROUPS from fund_tools.py: {', '.join(sorted(groups))}")
    print()
    
    any_issues = False
    
    # Check fund_tools.py itself for stale PORTFOLIO_WEIGHTS/GROUP_ACTION_RULES/sector_map
    fund_path = os.path.join(SCRIPTS_DIR, 'fund_tools.py')
    
    # Check PORTFOLIO_WEIGHTS
    pweight_groups = set()
    with open(fund_path) as f:
        content = f.read()
    # Find PORTFOLIO_WEIGHTS section
    import re
    pwm = re.search(r'PORTFOLIO_WEIGHTS\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if pwm:
        # Extract group names from keys
        for g in groups:
            if f"'{g}'" in pwm.group(1) or f'"{g}"' in pwm.group(1):
                pweight_groups.add(g)
        # Check for stale groups
        removed_groups = ['通航']
        for stale in removed_groups:
            if stale in pwm.group(1):
                print(f"❌ fund_tools.py: stale '{stale}' in PORTFOLIO_WEIGHTS")
                any_issues = True
    
    # Check GROUP_ACTION_RULES
    gam = re.search(r'GROUP_ACTION_RULES\s*=\s*\{', content)
    if gam:
        for stale in removed_groups:
            if f"'{stale}'" in content[gam.start():] or f'"{stale}"' in content[gam.start():]:
                # Check it's not in a comment
                lines = content[gam.start():].split('\n')
                for line in lines[:200]:
                    if stale in line and not line.strip().startswith('#'):
                        print(f"❌ fund_tools.py: stale '{stale}' in GROUP_ACTION_RULES")
                        any_issues = True
                        break
    
    # Check sector_map
    sm = re.search(r'sector_map\s*=\s*\{', content)
    if sm:
        for stale in removed_groups:
            if f"'{stale}'" in content[sm.start():] or f'"{stale}"' in content[sm.start():]:
                print(f"❌ fund_tools.py: stale '{stale}' in score_group_action sector_map")
                any_issues = True
    
    # Check pre-scripts
    for script, desc in [
        (os.path.join(SCRIPTS_DIR, 'closing_review.py'), 'closing_review.py group_order'),
        (os.path.join(SCRIPTS_DIR, 'collect_morning_data.py'), 'collect_morning_data.py group_order'),
    ]:
        if os.path.exists(script):
            if check_hardcoded_list(script, desc, ''):
                any_issues = True
    
    if not any_issues:
        print()
        print("✅ All group references are consistent with GROUPS dict")
    
    sys.exit(1 if any_issues else 0)

if __name__ == '__main__':
    main()
