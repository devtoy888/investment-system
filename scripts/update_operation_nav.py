#!/usr/bin/env python3
"""操作净值更新脚本 — 持仓确认后自动更新操作记录的份额/净值"""
import sys, os, json, re
sys.path.insert(0, '/opt/data/akshare-deps')
from datetime import date, datetime
from pathlib import Path

DATA_DIR = Path('/opt/data/fund_system_data')
OPER_DIR = DATA_DIR / 'operations'
PORT_DIR = DATA_DIR / 'portfolio'

def get_fund_value(code):
    """从fund_tools获取基金净值""" 
    import requests
    try:
        url = f"https://fundgz.1234567.com.cn/js/{code}.js"
        r = requests.get(url, timeout=8, headers={'Referer': 'https://fund.eastmoney.com/'})
        txt = r.text.strip()
        if 'jsonpgz(' in txt:
            data = json.loads(txt[txt.index('(')+1:txt.rindex(')')])
            return {
                'code': code,
                'name': data.get('name',''),
                'nav': data.get('dwjz',''),
                'nav_date': data.get('jzrq',''),
                'estimated_nav': data.get('gsz',''),
                'estimated_change': data.get('gszzl',''),
            }
    except Exception as e:
        print(f"  ⚠️ get_fund({code}): {e}")
    return None

def find_operation_for_date(target_date):
    """查找指定日期的操作记录文件"""
    fname = f"operation_{target_date}.md"
    fpath = OPER_DIR / fname
    if fpath.exists():
        return fpath
    return None

def update_operation_nav(op_file, fund_code, actual_nav, actual_nav_date, shares, cost):
    """更新操作记录中的实际份额和净值"""
    content = op_file.read_text(encoding='utf-8')
    
    # Find the row for this fund and update it
    # Current format: | 7/16 | fund | code | amount | prev_nav | est_chg | est_nav | est_shares | note |
    # We want to add actual columns
    lines = content.split('\n')
    new_lines = []
    updated = False
    
    for line in lines:
        if f'| {fund_code} |' in line and '合计' not in line:
            # This is the row to update
            # Add actual NAV info after the estimated values
            parts = line.split('|')
            if len(parts) >= 10:
                # Find where to add actual NAV - after est_shares, before note
                est_shares = parts[7].strip()
                note = parts[8].strip() if len(parts) > 8 else ''
                
                actual_shares_str = f"{shares:.2f}" if shares else est_shares
                
                # Update row with actual data
                # New format: add actual_nav and actual_shares columns
                if '待确认' in line or '≈' in parts[7]:
                    # This is estimated, update with actual
                    new_note = note if '确认' not in note else f"✅ 已确认({actual_nav_date})"
                    cells = parts[:]
                    # Update estimated nav to actual, estimated shares to actual
                    cells[6] = actual_nav  # replace est_nav with actual
                    cells[7] = actual_shares_str  # replace est_shares with actual
                    if len(cells) > 9:
                        cells[9] = f"✅ {actual_nav_date}确认"
                    new_line = '|'.join(cells)
                    new_lines.append(new_line)
                    updated = True
                    print(f"  ✅ 已更新 {fund_code}: 净值={actual_nav}, 份额={actual_shares_str}, 日期={actual_nav_date}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if updated:
        op_file.write_text('\n'.join(new_lines), encoding='utf-8')
        return True
    return False

def main():
    today = date.today()
    today_str = today.isoformat()
    print(f"📊 操作净值更新 · {today_str}")
    
    # Check for yesterday's operation (T+1 confirmation)
    yesterday = date(2026, 7, 16)  # The operation date
    yesterday_str = "2026-07-16"
    
    op_file = find_operation_for_date(yesterday_str)
    if not op_file:
        print(f"  ❌ 未找到 {yesterday_str} 的操作记录")
        return
    
    print(f"  📄 找到操作记录: {op_file}")
    
    # Update 003096 (A股基金, T+1确认)
    v1 = get_fund_value('003096')
    if v1:
        nav = v1.get('nav', '')
        nav_date = v1.get('nav_date', '')
        print(f"  003096: nav={nav}, date={nav_date}")
        
        # Check if the NAV is for July 16 (yesterday, the operation date)
        if nav and nav_date and nav_date <= today_str:
            # Calculate actual shares
            cost = 160.00
            try:
                shares = cost / float(nav)
                print(f"  003096: 成本160元 ÷ 净值{nav} = {shares:.2f}份")
                
                # Update the operation record
                update_operation_nav(op_file, '003096', nav, nav_date, shares, cost)
            except (ValueError, ZeroDivisionError) as e:
                print(f"  003096: 计算失败 {e}")
    
    # Update 013403 (QDII基金, T+2确认, 可能还没更新)
    v2 = get_fund_value('013403')
    if v2:
        nav = v2.get('nav', '')
        nav_date = v2.get('nav_date', '')
        print(f"  013403: nav={nav}, date={nav_date}")
        
        # QDII usually T+2, so July 16 NAV might not be available until July 18
        # Check if nav_date >= 2026-07-16
        if nav and nav_date and nav_date >= '2026-07-16':
            cost = 150.00
            try:
                shares = cost / float(nav)
                print(f"  013403: 成本150元 ÷ 净值{nav} = {shares:.2f}份")
                update_operation_nav(op_file, '013403', nav, nav_date, shares, cost)
            except (ValueError, ZeroDivisionError) as e:
                print(f"  013403: 计算失败 {e}")
        else:
            print(f"  013403: QDII净值尚未更新(当前{nav_date})，跳过")
    else:
        print(f"  013403: 获取净值失败")

if __name__ == '__main__':
    main()
