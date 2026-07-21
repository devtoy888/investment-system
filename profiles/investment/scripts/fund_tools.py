#!/usr/bin/env python3
"""
基金辅助系统 - 数据采集工具库
市场行情/基金净值/微博采集/存储/上传/外盘
"""
import json, os, sys, time, random, re
import requests
from datetime import datetime, date, timedelta, timezone
from collections import defaultdict
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── 常量 ──
CREDENTIAL_FILE = Path.home() / ".config" / "weibo-cli" / "credential.json"
FUND_SYSTEM_PREFIX = "fund-system"
DATA_DIR = Path("/opt/data")

FUND_CODES = {
    # 黄金
    '009478': '中银上海金ETF联接C',
    # 科技/AI/半导体
    '011613': '华夏科创50ETF联接C',
    '024418': '华夏上证科创板半导体材料设备ETF联接C',
    '026449': '大摩沪港深科技混合C',
    '014871': '大摩科技领先混合C',
    '020233': '大摩景气智选混合C',
    '017103': '大摩数字经济混合C',
    '011712': '大摩万众创新混合C',
    # 资源/周期
    '163302': '大摩资源优选混合(LOF)',
    '025857': '华夏中证电网设备ETF联接C',
    # 新能源（观察仓）
    '012329': '天弘中证新能源指数增强C',
    '011103': '天弘中证光伏C',
    # 2026-07-16 新增建仓
    '003096': '中欧医疗健康混合C',
    '013403': '华夏恒生科技ETF发起式联接(QDII)C',
}

KOLS = {
    '2014433131': '唐史主任司马迁',
    '6114912545': '小浣熊1230',
}

QUOTES = {
    '上证指数': 'sh000001',
    '创业板指': 'sz399006',
    '科创50': 'sh000688',
    '沪深300': 'sh000300',
    '上证50': 'sh000016',
    '黄金ETF市场价': 'sz159934',  # 易方达黄金ETF，跟踪Au99.99，与基金净值不同
}

# 行业ETF（用于板块监测）
SECTOR_ETFS = {
    '半导体': 'sz159813',
    '新能源': 'sz159752',
    '光伏': 'sz159857',
    '军工': 'sh512660',
    '医药': 'sh512170',
    '消费': 'sh510150',
    '券商': 'sh512880',
    '恒生科技ETF': 'sz159740',
    '通信': 'sh515050',
    '有色金属': 'sh512400',
}

# 赛道关键词（用于KOL微博分类）
SECTOR_KEYWORDS = {
    '科技/AI': ['AI','人工智能','算力','芯片','半导体','大模型','机器人','数据','软件','算法','GPU','华为','英伟达','deepseek','智能体'],
    '黄金': ['黄金','金价','贵金属','有色','金矿','Au'],
    '资源/周期': ['资源','周期','铜','铝','锂','稀土','煤炭','钢铁','化工','有色','商品','大宗'],
    '新能源': ['新能源','光伏','锂电','电池','储能','新能源车','电车','太阳能','风电','氢能'],
    '医药': ['医药','医疗','创新药','CXO','医保','药'],
    '消费': ['消费','白酒','食品','家电','汽车','零售'],
    '市场整体': ['大盘','指数','行情','市场','A股','创业板','科创板','上证','趋势'],
}

# 外盘代码 (Yahoo Finance)
OVERNIGHT_SYMBOLS = {
    '道琼斯': '^DJI',
    '标普500': '^GSPC',
    '纳斯达克': '^IXIC',
    '黄金期货': 'GC=F',
    '美元指数': 'DX-Y.NYB',
    '恒生指数': '^HSI',
    '韩国KOSPI': '^KS11',
}

# ── 数据源可用性追踪（供 auto_validate_sources.py 使用）──
_TRACKER_FILE = None

def _init_tracker():
    global _TRACKER_FILE
    if _TRACKER_FILE is None:
        _TRACKER_FILE = DATA_DIR / "fund_system_data" / "_source_availability.jsonl"
        _TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)

def track_source(name: str, success: bool, detail: str = ""):
    """记录一次数据源采集结果，用于自动验证"""
    _init_tracker()
    import json
    record = {
        '_ts': datetime.now().isoformat(),
        '_date': date.today().isoformat(),
        'source': name,
        'success': success,
        'detail': detail[:200],
    }
    try:
        with open(_TRACKER_FILE, 'a') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    except Exception:
        pass


def _tag_freshness(data: dict, source_name: str = "unknown") -> dict:
    """为数据字典添加新鲜度标记，用于非交易日识别。
    
    添加字段:
      - _fresh: bool (True=今日数据, False=旧数据)
      - _data_date: str (数据日期)
      - _fetch_time: str (获取时间)
    
    如果数据中已有 nav_date / date / time 等字段，用它们判断新鲜度。
    """
    today_str = date.today().isoformat()
    is_trading = is_trading_day()
    
    # 尝试从数据中提取日期
    data_date = None
    for date_key in ('nav_date', 'date', 'trade_date'):
        if date_key in data and data[date_key]:
            data_date = str(data[date_key])[:10]
            break
    
    if data_date is None:
        # 无法确定数据日期：非交易日 → stale, 交易日 → fresh(假设)
        data['_fresh'] = is_trading
        data['_stale_reason'] = None if is_trading else "non_trading_day_no_date"
    else:
        data['_fresh'] = (data_date == today_str)
        data['_stale_reason'] = None if data['_fresh'] else f"data_date={data_date}!=today={today_str}"
    
    data['_data_date'] = data_date or (today_str if is_trading else "unknown")
    data['_fetch_time'] = datetime.now().isoformat()
    data['_is_trading_day'] = is_trading
    return data


# ══════════════════════════════════════════════
# 1. 腾讯财经实时行情
# ══════════════════════════════════════════════

def get_tencent_quote(code: str) -> Optional[dict]:
    try:
        url = f"https://qt.gtimg.cn/q={code}"
        r = requests.get(url, timeout=5)
        line = r.text.strip().rstrip(';')
        if '="' in line:
            parts = line.split('="')[1].rstrip('"').split('~')
            if len(parts) < 35:
                return None
            return {
                'name': parts[1],
                'price': parts[3],
                'change_pct': parts[32],
                'open': parts[5],
                'prev_close': parts[4],
                'high': parts[33],
                'low': parts[34],
                'change_amt': parts[31],
                'volume': parts[6],
                'turnover': parts[37],
                'pe': parts[39] if len(parts) > 39 else '',
                'pb': parts[46] if len(parts) > 46 else '',
                'market_cap': parts[45] if len(parts) > 45 else '',
                '_stale': not is_trading_day(),  # 非交易日数据为旧数据
                '_data_source': 'tencent',
            }
    except Exception as e:
        print(f"  ⚠️ get_quote({code}): {e}")
    return None

def get_all_quotes() -> dict:
    result = {}
    items = list(QUOTES.items())
    with ThreadPoolExecutor(max_workers=4) as exc:
        future_map = {exc.submit(get_tencent_quote, code): name for name, code in items}
        for f in as_completed(future_map):
            name = future_map[f]
            q = f.result()
            if q:
                result[name] = q
                print(f"  ✅ {name}: {q['price']} ({q['change_pct']}%)")
                track_source('tencent_quotes', True, f"{name}:{q['price']}")
            else:
                result[name] = None
                print(f"  ❌ {name}: 获取失败")
                track_source('tencent_quotes', False, f"{name}:无数据")
    return result


def grade_market_sentiment(rise_count, fall_count, limit_up=None, limit_down=None):
    """市场情绪机械分档
    基于涨跌家数比例，将市场情绪分为5档，附加涨停/跌停信息。
    """
    if rise_count is None or fall_count is None:
        return '数据不足'
    total = rise_count + fall_count
    if total == 0:
        return '数据不足'
    ratio = rise_count / total
    grade = '普涨 🔴' if ratio > 0.70 else \
            '偏强 🔴' if ratio > 0.55 else \
            '中性 🟡' if ratio > 0.45 else \
            '偏弱 🟢' if ratio > 0.30 else \
            '冰点 🟢'
    up_down_ratio = rise_count / max(fall_count, 1)
    parts = [f'涨跌比{up_down_ratio:.2f}:1']
    if limit_up:
        parts.append(f'涨停{limit_up}')
    if limit_down:
        parts.append(f'跌停{limit_down}')
    if limit_up and limit_up > 50 and ratio > 0.5:
        parts.append('短线活跃 🔥')
    elif limit_up and limit_up < 15 and ratio < 0.5:
        parts.append('短线低迷 ❄️')
    return f'{grade} ({" ".join(parts)})'


def get_short_term_sentiment(market_overview):
    """从市场总览数据构造短线情绪摘要"""
    lines = []
    ov = market_overview or {}
    rc = ov.get('rise_count')
    fc = ov.get('fall_count')
    lu = ov.get('limit_up')
    ld = ov.get('limit_down')
    tt = ov.get('total_turnover')
    if rc is not None:
        sentiment = grade_market_sentiment(rc, fc, lu, ld)
        lines.append(f'📊 大盘情绪: {sentiment}')
    if tt:
        lines.append(f'💰 成交额: {tt/1e8:.0f}亿')
    if lu is not None and ld is not None:
        heat = '🔥' if lu > 50 else '❄️' if lu < 15 else '➖'
        lines.append(f'📈 涨停{lu}家 跌停{ld}家 {heat}')
    return '\n'.join(lines)



# ══════════════════════════════════════════════
# 2. 天天基金净值/实时估值
# ══════════════════════════════════════════════

def get_fund_value(fund_code: str, _retry: bool = True, depth: int = 0) -> Optional[dict]:
    """获取基金净值与实时估算。

    Returns:
        dict with fields:
          'code', 'name', 'nav' (dwjz最新官方净值), 'estimated_nav' (gsz),
          'estimated_change' (gszzl), 'nav_date' (jzrq净值日期),
          'stale': nav_date != today (数据可能非当日),
          'has_official': nav_date == today (官方净值已发布),
          'change_vs_prev': 如果提供了前日净值，计算实际涨跌幅
    """
    try:
        url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
        r = requests.get(url, timeout=8,
            headers={'Referer': 'https://fund.eastmoney.com/'})
        txt = r.text.strip()
        if 'jsonpgz(' in txt:
            data = json.loads(txt[txt.index('(')+1:txt.rindex(')')])
            nav_date_str = data.get('jzrq', '')
            today_str = date.today().isoformat()
            # fresh: 净值日期是否等于今日
            is_fresh = (nav_date_str == today_str)

            # 最多重试读取一次：如果gszzl=0.00且盘中时段，等待3秒重试（应对黄金联接等延迟）
            gszzl = data.get('gszzl', '0')
            if depth < 1 and abs(float(gszzl or 0)) < 0.005 and not is_fresh:
                now = datetime.now()
                h, m = now.hour, now.minute
                # 北京交易时段 9:25-15:30
                bj_minutes = (h + 8) % 24 * 60 + m
                if 565 <= bj_minutes <= 930:  # 9:25~15:30 BJT
                    time.sleep(3)
                    return get_fund_value(fund_code, _retry=_retry, depth=1)

            return {
                'code': fund_code,
                'name': data.get('name', ''),
                'nav': data.get('dwjz', ''),
                'estimated_nav': data.get('gsz', ''),
                'estimated_change': gszzl,
                'nav_date': nav_date_str,
                'stale': not is_fresh,
                'has_official': is_fresh,
                'change_source': 'fundgz',
            }
    except Exception as e:
        if _retry:
            time.sleep(0.5)
            return get_fund_value(fund_code, _retry=False)
    
    # fundgz API 未返回JSONP（可能已失效或跳转），走AKShare备援
    try:
        from fund_source_akshare import get_fund_realtime
        ak_data = get_fund_realtime(fund_code)
        if ak_data:
            return {
                'code': fund_code,
                'name': ak_data.get('name', ''),
                'nav': ak_data.get('nav', 0),
                'estimated_nav': ak_data.get('estimated_nav', 0),
                'estimated_change': ak_data.get('estimated_change', 0),
                'nav_date': ak_data.get('nav_date', date.today().isoformat()),
                'stale': True,
                'has_official': False,
                'change_source': ak_data.get('source', 'akshare'),
            }
    except Exception:
        pass
    return None

def get_all_funds() -> dict:
    result = {}
    items = list(FUND_CODES.items())
    with ThreadPoolExecutor(max_workers=5) as exc:
        future_map = {exc.submit(get_fund_value, code): (code, name) for code, name in items}
        for f in as_completed(future_map):
            code, name = future_map[f]
            v = f.result()
            if v:
                result[code] = v
                print(f"  ✅ {name}: 净值={v['nav']}  估算={v['estimated_change']}%")
                track_source('fund_values', True, f"{code}:{v['nav']}({v['estimated_change']}%)")
            else:
                result[code] = None
                print(f"  ❌ {name}: 获取失败")
                track_source('fund_values', False, f"{code}:无数据")
    return result


# ══════════════════════════════════════════════
# 3. 外盘数据 (Yahoo Finance)
# ══════════════════════════════════════════════

_YAHOO_CACHE = {}

def _yahoo_quote(symbol: str) -> Optional[dict]:
    if symbol in _YAHOO_CACHE:
        return _YAHOO_CACHE[symbol]
    try:
        import urllib.parse
        encoded = urllib.parse.quote(symbol)
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{encoded}'
        r = requests.get(url, timeout=8,
            headers={'User-Agent': 'Mozilla/5.0'})
        data = r.json()
        result = data.get('chart', {}).get('result')
        if not result:
            return None
        meta = result[0].get('meta', {})
        price = meta.get('regularMarketPrice')
        prev_close = meta.get('chartPreviousClose', 0)
        if price is None:
            return None
        change_pct = round((price - prev_close) / prev_close * 100, 2) if prev_close else 0
        
        # 新鲜度判断：用Yahoo自身的时间戳(regularMarketTime)动态判断
        # 不依赖任何硬编码节假日日历
        market_time = meta.get('regularMarketTime')
        now_ts = datetime.now().timestamp()
        is_fresh = False
        stale_reason = None
        if market_time:
            age_hours = (now_ts - market_time) / 3600
            # 如果数据距今<24小时，视为新鲜（覆盖隔夜数据场景）
            if age_hours < 24:
                is_fresh = True
            else:
                stale_reason = f"data_age={age_hours:.1f}h>24h"
        else:
            stale_reason = "no_timestamp"
        
        out = {
            'price': price,
            'change_pct': change_pct,
            'prev_close': prev_close,
            '_stale': not is_fresh,
            '_stale_reason': stale_reason,
            '_data_time': datetime.fromtimestamp(market_time, tz=timezone.utc).isoformat() if market_time else None,
            '_fetch_time': datetime.now().isoformat(),
        }
        _YAHOO_CACHE[symbol] = out
        return out
    except Exception as e:
        print(f"  ⚠️ yahoo({symbol}): {e}")
        return None

def get_overnight_quotes() -> dict:
    result = {}
    items = list(OVERNIGHT_SYMBOLS.items())
    print("  🌙 外盘行情:")
    with ThreadPoolExecutor(max_workers=4) as exc:
        future_map = {exc.submit(_yahoo_quote, symbol): name for name, symbol in items}
        for f in as_completed(future_map):
            name = future_map[f]
            q = f.result()
            if q:
                result[name] = q
                emoji = '🔴' if q['change_pct'] > 0 else ('🟢' if q['change_pct'] < 0 else '🟡')
                print(f"    {emoji} {name}: {q['price']} ({q['change_pct']:+.2f}%)")
                track_source('overnight', True, f"{name}:{q['price']}({q['change_pct']:+.2f}%)")
            else:
                result[name] = None
                print(f"    ❌ {name}: 获取失败")
                track_source('overnight', False, f"{name}:无数据")
    return result


# ══════════════════════════════════════════════
# 3.5 行业ETF板块监测
# ══════════════════════════════════════════════

def get_sector_quotes() -> dict:
    """获取行业ETF板块涨跌排行（批量查询），返回 {板块名: {price, change_pct, code}}"""
    result = {}
    try:
        # 腾讯支持批量查询，一次调用所有板块
        codes = list(SECTOR_ETFS.values())
        url = f"https://qt.gtimg.cn/q={','.join(codes)}"
        r = requests.get(url, timeout=8)
        # 解析返回的多行结果
        lines = r.text.strip().rstrip(';').split(';')
        for line in lines:
            if '=\"' not in line:
                continue
            parts = line.split('=\"')[1].rstrip('\"').split('~')
            if len(parts) < 32:
                continue
            code = parts[2] if len(parts) > 2 else ''
            # 找到对应的板块名（腾讯返回code不带前缀，如 sz159813 → 159813）
            pure_code = code if code.startswith(('sh', 'sz', 'bj')) else code
            sector = next((s for s, c in SECTOR_ETFS.items() if c.endswith(code) or c.endswith(pure_code)), None)
            if not sector:
                continue
            change_str = parts[32]
            try:
                change = float(change_str)
            except (ValueError, TypeError):
                result[sector] = None
                continue
            result[sector] = {
                'price': parts[3],
                'change_pct': change,
                'code': code,
                'open': parts[5] if len(parts) > 5 else '',
                'prev_close': parts[4] if len(parts) > 4 else '',
                'high': parts[33] if len(parts) > 33 else '',
                'low': parts[34] if len(parts) > 34 else '',
                'volume': parts[6] if len(parts) > 6 else '0',
                'turnover': parts[37] if len(parts) > 37 else '0',
            }
        # 填充未返回的板块
        for sector in SECTOR_ETFS:
            if sector not in result:
                result[sector] = None
    except Exception as e:
        print(f"  ⚠️ get_sector_quotes: {e}")
        for sector in SECTOR_ETFS:
            result[sector] = None
    
    # 打印结果
    success_count = sum(1 for v in result.values() if v)
    print(f"  📊 行业板块 ({success_count}/{len(result)}):")
    for name, q in sorted(result.items(), key=lambda x: -(x[1]['change_pct'] if x[1] else 0)):
        if q:
            emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
            print(f"    {emoji} {name}: {q['price']} ({q['change_pct']:+.2f}%)")
        else:
            print(f"    ❌ {name}: 无数据")
    track_source('sector_etfs', success_count > 0, f"获取{success_count}/{len(SECTOR_ETFS)}个板块")
    return result


# ══════════════════════════════════════════════
# 3.6 市场总览（涨跌家数 + 总成交额）
# ══════════════════════════════════════════════

_EM_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://quote.eastmoney.com/',
}

def get_market_overview() -> dict:
    """获取A股市场总览数据：
    返回 { 'rise_count', 'fall_count', 'flat_count', 'limit_up', 'limit_down',
           'sh_turnover', 'sz_turnover', 'total_turnover' }"""
    result = {'rise_count': None, 'fall_count': None, 'flat_count': None, 'limit_up': None, 'limit_down': None}
    
    # 1. 涨跌家数 (东财push2 + push2delay双域名轮换)
    _breadth_sources_tried = []
    # 主源: 东财push2 (两个域名轮换，push2delay是海外备胎)
    for em_domain in ['push2.eastmoney.com', 'push2delay.eastmoney.com']:
        if _breadth_sources_tried:
            break
        try:
            url = f'https://{em_domain}/api/qt/stock/get?secid=1.000001&fields=f57,f58,f167,f168,f169,f170,f171'
            r = requests.get(url, timeout=15, headers=_EM_HEADERS)
            data = r.json().get('data', {})
            if not data or not data.get('f169'):
                continue
            result['rise_count'] = int(data.get('f169', 0))
            result['fall_count'] = int(data.get('f170', 0))
            result['flat_count'] = int(data.get('f171', 0))
            result['limit_up'] = int(data.get('f167', 0))
            result['limit_down'] = int(data.get('f168', 0))
            total = result['rise_count'] + result['fall_count'] + result['flat_count']
            if total == 0:
                continue
            domain_label = '东财p2' if 'push2.' in em_domain else '东财p2d'
            print(f"  📈 [{domain_label}]涨{result['rise_count']} 跌{result['fall_count']} 平{result['flat_count']} 涨停{result['limit_up']} 跌停{result['limit_down']} (共{total})")
            track_source('market_breadth', True, f"{domain_label}涨{result['rise_count']}/跌{result['fall_count']} 涨停{result['limit_up']}")
            _breadth_sources_tried.append(f'eastmoney_{em_domain.split(".")[0]}')
        except Exception as e:
            print(f"  ⚠️ 涨跌家数({em_domain}): {type(e).__name__}")
            track_source('market_breadth', False, f"{em_domain}:{type(e).__name__}"[:100])
    
    # 如果东财双域名都失败，走备援
    if not _breadth_sources_tried:
        # 备援1: 新浪tags行情描述文本（增强正则，支持多种格式）
        try:
            r2 = requests.get('https://tags.sina.com.cn/finance_beixiangzijin',
                headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
            html = r2.text
            rise_val, fall_val = None, None
            # 多种模式匹配上涨家数
            rise_patterns = [
                r'(?:超|约|共|近|达)?(\d+)只个股上涨',
                r'(?:超|约|共|近|达)?(\d+)只上涨',
                r'上涨家数.*?(\d+)',
                r'上涨(\d+)家',
            ]
            for pat in rise_patterns:
                m = re.search(pat, html)
                if m:
                    rise_val = int(m.group(1))
                    break
            # 多种模式匹配下跌家数
            fall_patterns = [
                r'(?:超|约|共|近|达)?(\d+)只个股下跌',
                r'(?:超|约|共|近|达)?(\d+)只下跌',
                r'下跌家数.*?(\d+)',
                r'下跌(\d+)家',
            ]
            for pat in fall_patterns:
                m = re.search(pat, html)
                if m:
                    fall_val = int(m.group(1))
                    break
            if rise_val is not None:
                result['rise_count'] = rise_val
            if fall_val is not None:
                result['fall_count'] = fall_val
            total = (result['rise_count'] or 0) + (result['fall_count'] or 0)
            if total > 1000:
                print(f"  📈 [新浪]涨{result['rise_count']} 跌{result['fall_count']}")
                track_source('market_breadth', True, f"[新浪]涨{result['rise_count']}/跌{result['fall_count']}")
                _breadth_sources_tried.append('sina_tags')
            else:
                print(f"  ⚠️ 涨跌家数(新浪): 提取到{result['rise_count']}/{result['fall_count']}, 数据偏少可能不准")
        except Exception as e2:
            print(f"  ⚠️ 涨跌家数(新浪备援)也失败: {e2}")
        
        # 备援2: AKShare stock_zh_a_spot_em()
        if not _breadth_sources_tried:
            try:
                from fund_source_akshare import get_market_breadth_akshare
                ak_bf = get_market_breadth_akshare()
                if ak_bf:
                    result['rise_count'] = ak_bf['rise_count']
                    result['fall_count'] = ak_bf['fall_count']
                    result['flat_count'] = ak_bf.get('flat_count', 0)
                    total = result['rise_count'] + result['fall_count']
                    print(f"  📈 [AKShare]涨{result['rise_count']} 跌{result['fall_count']}")
                    track_source('market_breadth', True, f"[AKShare]涨{result['rise_count']}/跌{result['fall_count']}")
                    _breadth_sources_tried.append('akshare')
            except Exception as e3:
                print(f"  ⚠️ 涨跌家数(AKShare备援)也失败: {e3}")

    # 2. 总成交额 (腾讯指数A股+深证)
    try:
        sh_url = 'https://qt.gtimg.cn/q=sh000002'  # A股指数
        sz_url = 'https://qt.gtimg.cn/q=sz399001'  # 深证成指
        sh_r = requests.get(sh_url, timeout=5)
        sz_r = requests.get(sz_url, timeout=5)
        
        def parse_turnover(text):
            if '=\"' not in text:
                return 0
            parts = text.strip().rstrip(';').split('=\"')[1].rstrip('\"').split('~')
            f35 = parts[35] if len(parts) > 35 else ''
            if '/' in f35:
                try:
                    return float(f35.split('/')[2])  # 第三段是成交额(元)
                except (ValueError, IndexError):
                    pass
            return 0
        
        sh_turn = parse_turnover(sh_r.text)
        sz_turn = parse_turnover(sz_r.text)
        result['sh_turnover'] = sh_turn
        result['sz_turnover'] = sz_turn
        result['total_turnover'] = sh_turn + sz_turn
        
        if sh_turn + sz_turn > 0:
            print(f"  💰 上证成交:{sh_turn/1e8:.0f}亿 深证成交:{sz_turn/1e8:.0f}亿 合计:{(sh_turn+sz_turn)/1e8:.0f}亿")
            track_source('total_turnover', True, f"合计{(sh_turn+sz_turn)/1e8:.0f}亿")
        else:
            track_source('total_turnover', False, "成交额=0（可能非交易时段）")
    except Exception as e:
        print(f"  ⚠️ 成交额获取失败: {e}")
        track_source('total_turnover', False, str(e)[:100])
    
    return result


# ══════════════════════════════════════════════
# 3.7 北向资金（同花顺 hexin API）
# ══════════════════════════════════════════════

_NORTHBOUND_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0 Safari/537.36',
    'Host': 'data.hexin.cn',
    'Referer': 'https://data.hexin.cn/',
}

def get_northbound_flow() -> dict:
    """获取北向资金当日实时净流入（最新累计值），内置2次重试+备用源。
    返回: { 'hgt': 沪股通亿, 'sgt': 深股通亿, 'total': 合计亿, 'time': 最新时间点, 'stale': bool }
    stale=True 表示数据是缓存/快照（非实时），非交易时段正常。"""
    result = {'hgt': None, 'sgt': None, 'total': None, 'time': None, 'stale': False}
    
    # 先读已保存的最新数据日期，用于判断是否刷新
    _NB_DATE_FILE = Path('/tmp/fund_data/_northbound_date.txt')
    _NB_DATA_FILE = Path('/tmp/fund_data/_northbound_fallback.json')
    today_str = date.today().isoformat()

    # 主源：hexin 同花顺API
    for attempt in range(2):
        try:
            r = requests.get(
                'https://data.hexin.cn/market/hsgtApi/method/dayChart/',
                headers=_NORTHBOUND_HEADERS, timeout=8)
            d = r.json()
            times = d.get('time', [])
            hgt = d.get('hgt', [])
            sgt = d.get('sgt', [])
            last_idx = -1
            best_idx = -1
            now = datetime.now()
            now_minutes = now.hour * 60 + now.minute
            for i in range(len(times) - 1, -1, -1):
                if times[i] and hgt[i] is not None and sgt[i] is not None:
                    if last_idx == -1:
                        last_idx = i
                    # 找最接近当前时间的数据点（120分钟内）
                    data_minutes = int(times[i].split(':')[0]) * 60 + int(times[i].split(':')[1])
                    if abs(now_minutes - data_minutes) <= 120:
                        if best_idx == -1 or abs(now_minutes - data_minutes) < abs(now_minutes - int(times[best_idx].split(':')[0])*60 - int(times[best_idx].split(':')[1])):
                            best_idx = i
            # 优先用最接近当前时间的，否则用最后一个
            use_idx = best_idx if best_idx >= 0 else last_idx
            if use_idx >= 0:
                result['hgt'] = hgt[use_idx]
                result['sgt'] = sgt[use_idx]
                result['total'] = (hgt[use_idx] or 0) + (sgt[use_idx] or 0)
                result['time'] = times[use_idx]
                # 时效性判断
                data_minutes = int(times[use_idx].split(':')[0]) * 60 + int(times[use_idx].split(':')[1])
                if 9 <= now.hour <= 16 and 540 <= now_minutes <= 960:  # 交易相关时段
                    if abs(now_minutes - data_minutes) > 60:  # 数据比当前时间早1小时以上
                        result['stale'] = True
                emoji = '🔴' if result['total'] > 0 else '🟢' if result['total'] < 0 else '🟡'
                # 日期级新鲜度检测
                last_date = _NB_DATE_FILE.read_text().strip() if _NB_DATE_FILE.exists() else ''
                if last_date and last_date != today_str:
                    result['stale'] = True  # 数据是昨天的
                # ★ 防重复陈数据：hexin返回的总金额与已缓存的一致 → 跳过hexin走备用源
                skip_hexin = False
                if result['stale'] and _NB_DATA_FILE.exists():
                    try:
                        prev_nb = json.loads(_NB_DATA_FILE.read_text())
                        if prev_nb.get('total') is not None and abs(prev_nb['total'] - result['total']) < 0.001:
                            skip_hexin = True
                            print(f"  ⚠️ 北向资金(hexin): total={result['total']:+.2f}亿 与缓存一致→跳过(陈数据)")
                            track_source('northbound_flow', False, 'total_matches_cache')
                    except Exception:
                        pass
                if skip_hexin:
                    continue  # 跳出hexin，走备用源
                stale_tag = ' ⚠️(缓存)' if result['stale'] else ''
                print(f"  {emoji} 北向资金: 沪{result['hgt']:+.2f}亿 深{result['sgt']:+.2f}亿 合计{result['total']:+.2f}亿 ({result['time']}){stale_tag}")
                track_source('northbound_flow', True, f"合计{result['total']:+.2f}亿")
                # 保存最新数据日期和数值
                _NB_DATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                _NB_DATE_FILE.write_text(today_str)
                _NB_DATA_FILE.write_text(json.dumps(result, ensure_ascii=False))
                return result
            else:
                print(f"  ⚠️ 北向资金(attempt {attempt+1}): 无有效数据")
                if attempt == 0:
                    time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ 北向资金(attempt {attempt+1}): {e}")
            track_source('northbound_flow', False, str(e)[:100])
            if attempt == 0:
                time.sleep(1)

    # 备用源1：新浪财经北向快讯（提取每日净流入总额，过滤个股级别数据）
    for attempt in range(2):
        try:
            import re
            r = requests.get('https://tags.sina.com.cn/finance_beixiangzijin',
                headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            html = r.text
            # 匹配"北向资金今天净买入X亿" / "北向资金合计净买入X亿"（只取亿级，排除万元级个股数据）
            all_m = list(re.finditer(r'北向资金\s*(?:今天|昨日|当日|合计)?\s*净([买卖出入]+)\s*([\d.]+)\s*亿', html))
            if all_m:
                # 取金额最接近10-100亿的匹配（每日北向总流入通常在10-100亿范围）
                best = None
                best_diff = float('inf')
                for m in all_m:
                    try:
                        amt = float(m.group(2))
                        if 1 <= amt <= 200 and abs(amt - 50) < best_diff:
                            best = m
                            best_diff = abs(amt - 50)
                    except:
                        continue
                if best:
                    direction = best.group(1)
                    amount = float(best.group(2))
                    total = -amount if '卖' in direction else amount
                    result['total'] = total
                    result['hgt'] = total * 0.3
                    result['sgt'] = total * 0.7
                    result['time'] = '15:00'
                    result['source'] = 'sina'
                    emoji = '🔴' if total > 0 else '🟢'
                    print(f"  {emoji} 北向资金(新浪): 合计{total:+.2f}亿")
                    track_source('northbound_flow', True, f"[新浪]合计{total:+.2f}亿")
                    return result
            if attempt == 0:
                time.sleep(1)
        except Exception as e:
            if attempt == 1:
                print(f"  ⚠️ 北向资金(新浪备用): {e}")
    
    # 备用源1.5: AKShare 北向资金（在新浪tags和东财push2之间）
    try:
        from fund_source_akshare import get_northbound_flow as ak_nb
        ak_data = ak_nb()
        if ak_data and ak_data.get('total') is not None:
            result['total'] = ak_data['total']
            result['hgt'] = ak_data.get('hgt', ak_data['total'] * 0.3)
            result['sgt'] = ak_data.get('sgt', ak_data['total'] * 0.7)
            result['time'] = '15:00'
            result['source'] = 'akshare'
            emoji = '🔴' if result['total'] > 0 else '🟢'
            print(f"  {emoji} 北向资金(AKShare): 合计{result['total']:+.2f}亿")
            track_source('northbound_flow', True, f"[AKShare]合计{result['total']:+.2f}亿")
            return result
    except Exception as e:
        print(f"  ⚠️ 北向资金(AKShare备用): {e}")
    
    # 备用源2: 东财 push2 北向资金API（新增，最可靠）
    try:
        from urllib.parse import urlencode
        em_url = 'https://push2.eastmoney.com/api/qt/kamt.kline/get' + urlencode({
            'fields1': 'f1,f3,f5', 'fields2': 'f51,f52,f53,f54,f55',
            'klt': '1', 'lmt': '1'
        })
        r = requests.get(em_url, headers=_EM_HEADERS, timeout=8)
        d = r.json()
        kl = d.get('data', {}).get('klines', [])
        if kl:
            parts = kl[0].split(',')
            # f51=时间, f52=沪股通, f53=深股通, f54=总额, f55=MA5
            if len(parts) >= 5:
                result['hgt'] = float(parts[1]) if parts[1] else 0
                result['sgt'] = float(parts[2]) if parts[2] else 0
                result['total'] = float(parts[3]) if parts[3] else 0
                result['time'] = parts[0][-5:] if parts[0] else '?'
                result['source'] = 'eastmoney'
                emoji = '🔴' if result['total'] > 0 else '🟢'
                print(f"  {emoji} 北向资金(东财): 沪{result['hgt']:+.2f}亿 深{result['sgt']:+.2f}亿 合计{result['total']:+.2f}亿")
                track_source('northbound_flow', True, f"[东财]合计{result['total']:+.2f}亿")
                return result
    except Exception as e:
        print(f"  ⚠️ 北向资金(东财备用): {e}")
    
    # 备用源3：快照文件
    try:
        snap_path = Path('/tmp/fund_data/_yesterday_snapshot.json')
        if snap_path.exists():
            snap = json.loads(snap_path.read_text())
            nb = snap.get('northbound', {})
            if nb.get('total') is not None:
                result['hgt'] = nb['hgt']
                result['sgt'] = nb['sgt']
                result['total'] = nb['total']
                result['time'] = nb.get('time', '?')
                result['stale'] = True
                stale_tag = ' ⚠️(缓存)' if result['stale'] else ''
                print(f"  🟡 北向资金(备用·快照): 合计{nb['total']:+.2f}亿{stale_tag}")
                track_source('northbound_flow_snap', True, f"合计{nb['total']:+.2f}亿")
                return result
    except Exception:
        pass

    return result


# ══════════════════════════════════════════════
# 3.8 赛道 RSS 新闻采集
# ══════════════════════════════════════════════

def fetch_rss_news(max_per_source: int = 3, timeout: int = 10) -> dict:
    """采集赛道 RSS 新闻，返回 {赛道名: [(标题, 链接, 来源), ...]}"""
    import json, urllib.request, xml.etree.ElementTree as ET
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import os

    sources_file = os.path.join(os.path.dirname(__file__), "news_sources.json")
    if not os.path.exists(sources_file):
        print("  \u26a0\ufe0f news_sources.json 不存在，跳过 RSS 采集")
        return {}

    with open(sources_file) as f:
        config = json.load(f)

    industries = {i['key']: i['name'] for i in config.get('industries', [])}
    sources = config.get('sources', [])
    per_source = max_per_source or config.get('fetch', {}).get('per_source', 3)
    req_timeout = timeout or config.get('fetch', {}).get('timeout', 10)
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def fetch_one(src):
        results = []
        try:
            req = urllib.request.Request(src['url'], headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=req_timeout) as resp:
                data = resp.read()
            root = ET.fromstring(data)
            items = root.findall('.//item')
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            if not items:
                items = root.findall('.//entry')
            for item in items[:per_source]:
                title, link = '', ''
                t = item.find('title')
                if t is not None:
                    title = t.text or ''
                if not title:
                    t = item.find('{http://www.w3.org/2005/Atom}title')
                    if t is not None:
                        title = t.text or ''
                l = item.find('link')
                if l is not None:
                    link = l.text or l.get('href', '') or ''
                if not link:
                    l = item.find('{http://www.w3.org/2005/Atom}link')
                    if l is not None:
                        link = l.get('href', '') or ''
                if title and link:
                    results.append((title.strip(), link.strip(), src['name']))
        except Exception:
            pass
        return src['hint'], results

    grouped = {}
    with ThreadPoolExecutor(max_workers=8) as exc:
        futures = {exc.submit(fetch_one, s): s for s in sources}
        for f in as_completed(futures):
            hint, results = f.result()
            if hint not in grouped:
                grouped[hint] = []
            grouped[hint].extend(results)

    result = {}
    for hint, items in grouped.items():
        name = industries.get(hint, hint)
        seen = set()
        unique = []
        for title, link, source in items:
            if title not in seen:
                seen.add(title)
                unique.append((title, link, source))
        if unique:
            result[name] = unique[:5]

    total = sum(len(v) for v in result.values())
    print(f"  \U0001f4e1 赛道 RSS: {total}\u6761\u65b0\u95fb ({len(result)}\u4e2a\u8d5b\u9053)")
    return result


# ── 翻译辅助 ──
_TRANSLATE_CACHE = {}

def translate_text(text: str, target: str = "zh-CN") -> str:
    """调用 Google 免费翻译 API 将文本翻译为中文。带内存缓存。"""
    if not text or not text.strip():
        return text
    key = text.strip()[:200]
    if key in _TRANSLATE_CACHE:
        return _TRANSLATE_CACHE[key]
    try:
        import requests
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "auto", "tl": target, "dt": "t", "q": text.strip()[:1000]}
        r = requests.get(url, params=params, timeout=8,
                         headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        if r.status_code == 200:
            result = r.json()[0][0][0]
            _TRANSLATE_CACHE[key] = result
            return result
    except Exception:
        pass
    return text


def is_mostly_english(text: str) -> bool:
    """判断文本是否以英文字符为主（>50% 英文字母）"""
    if not text:
        return False
    letters = sum(1 for c in text if c.isascii() and c.isalpha())
    total = len(text.strip())
    return letters > 0 and (letters / max(total, 1)) > 0.4


def format_rss_news(news: dict) -> str:
    """将 RSS 新闻格式化为 markdown，英文标题自动翻译为中文"""
    if not news:
        return ''
    lines = ['📡 **隔夜赛道要闻**']
    for category, items in news.items():
        lines.append('')
        lines.append(f'**{category}**')
        for title, link, source in items:
            display_title = title[:60] + '…' if len(title) > 60 else title
            # 如果标题主要是英文，翻译为中文
            if is_mostly_english(display_title):
                cn_title = translate_text(display_title)
                if cn_title and cn_title != display_title:
                    display_title = f"{cn_title}"
            lines.append(f'  ● [{display_title}]({link}) — {source}')
    return '\n'.join(lines)



# ══════════════════════════════════════════════
# 4. 微博博主采集（桌面API）
# ══════════════════════════════════════════════

def get_user_weibos(uid: str, count: int = 5) -> list:
    if not CREDENTIAL_FILE.exists():
        print(f"  ❌ 微博凭据文件不存在")
        return []
    try:
        cred = json.loads(CREDENTIAL_FILE.read_text())
        cookies = cred.get('cookies', {})
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://weibo.com/",
            "X-Requested-With": "XMLHttpRequest",
        }
        r = requests.get(
            f"https://weibo.com/ajax/statuses/mymblog",
            params={"uid": uid, "page": "1", "feature": "1"},
            cookies=cookies, headers=headers, timeout=15
        )
        data = r.json()
        if data.get("ok") == 1:
            posts = data.get("data", {}).get("list", [])
            results = []
            for p in posts[:count]:
                # 获取文本：先取短文本
                text = p.get("text_raw", p.get("text", ""))
                text = re.sub(r'<[^>]+>', '', text).strip()
                
                # 如果是长文本(isLongText=True)，调用长文本API获取完整内容
                if p.get("isLongText"):
                    try:
                        lt_url = f"https://weibo.com/ajax/statuses/longtext?id={p.get('id','')}"
                        lt_r = requests.get(lt_url, cookies=cookies, headers=headers, timeout=8)
                        lt_data = lt_r.json()
                        if lt_data.get("ok") == 1:
                            full_text = lt_data.get("data", {}).get("longTextContent", "")
                            if full_text:
                                text = re.sub(r'<[^>]+>', '', full_text).strip()
                    except Exception as e:
                        print(f"  ⚠️ 长文本拉取失败: {e}")
                
                results.append({
                    'id': p.get('id', ''),
                    'mblogid': p.get('mblogid', ''),
                    'created_at': p.get('created_at', ''),
                    'text': text[:2000],  # 放宽到2000字
                    'is_longtext': p.get('isLongText', False),
                    'reposts_count': p.get('reposts_count', 0),
                    'comments_count': p.get('comments_count', 0),
                    'attitudes_count': p.get('attitudes_count', 0),
                })
            return results
        elif data.get("ok") == -100:
            print(f"  ⚠️ UID={uid}: 会话过期，需重新登录")
        else:
            print(f"  ⚠️ UID={uid}: ok={data.get('ok')}")
    except Exception as e:
        print(f"  ⚠️ get_weibos({uid}): {e}")
    return []


def get_weibo_comments(post_id: str, count: int = 20) -> list:
    """拉取指定博文的评论区。
    post_id: 博文数字ID（不是mblogid）
    返回评论列表，每条含：user, text, has_zr_reply, likes
    """
    if not CREDENTIAL_FILE.exists():
        print(f"  ❌ 微博凭据文件不存在")
        return []
    try:
        cred = json.loads(CREDENTIAL_FILE.read_text())
        cookies = cred.get('cookies', {})
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://weibo.com/",
            "X-Requested-With": "XMLHttpRequest",
        }
        all_comments = []
        pages_needed = min(3, max(1, (count + 19) // 20))
        for page in range(1, pages_needed + 1):
            r = requests.get(
                'https://weibo.com/aj/v6/comment/big',
                params={'ajwvr': 6, 'id': post_id, 'from': 'singleWeiBo', 'page': page},
                cookies=cookies, headers=headers, timeout=15
            )
            html = r.json().get('data', {}).get('html', '')
            if not html:
                break
            blocks = re.findall(r'node-type="root_comment"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*<div[\s>]', html, re.DOTALL)
            for block in blocks:
                users = re.findall(r'<a[^>]*>([^<]+)</a>', block)
                user = users[0] if users else '?'
                texts = re.findall(r'WB_text[^>]*>(.*?)</div>', block, re.DOTALL)
                text = re.sub(r'<[^>]+>', '', texts[0]).strip() if texts else ''
                text = re.sub(r'\s+', ' ', text)[:300]
                has_reply = '唐史主任司马迁' in block
                likes_m = re.findall(r'like_counts["\']:\s*(\d+)', block)
                likes_c = int(likes_m[0]) if likes_m else 0
                all_comments.append({
                    'user': user.strip(),
                    'text': text,
                    'has_zr_reply': has_reply,
                    'likes': likes_c,
                })
            time.sleep(0.15)
        # 去重
        seen = set()
        unique = []
        for c in all_comments:
            if c['text'] not in seen:
                seen.add(c['text'])
                unique.append(c)
        print(f"  💬 拉取评论 {len(unique)} 条, 主任回复 {sum(1 for c in unique if c['has_zr_reply'])} 条")
        return unique[:count]
    except Exception as e:
        print(f"  ⚠️ get_comments({post_id}): {e}")
        return []


# 是否值得拉评论的信号词
COMMENT_TRIGGER_KEYWORDS = [
    '融资仓', '加仓', '补仓', '接货', '接筹', '右侧', '底部',
    '触底', '反弹', '抄底',
]


# ══════════════════════════════════════════════
# 5. 微博AI解读（深度分析引擎）
# ══════════════════════════════════════════════

# 一级黑话：市场参与者/主体
SIGNALS_PARTICIPANTS = {
    '村里': '政策层面/监管层（证监会/交易所）',
    '上面': '高层/监管机构',
    '大家伙': '大资金/机构/国家队',
    '聪明钱': '北向资金/外资',
    '老乡': '散户投资者',
    '掌柜': '基金经理/操盘手',
    '量化': '量化交易基金（高频/程序化交易）',
    '耐心资本': '倡导长期持有的监管导向资金',
    '汪汪队': '国家队/证金/汇金等维稳资金',
    '柚子': '游资/短线炒作资金',
    '鸡狗': '机构（谐音）',
    '机构': '公募/私募基金等专业投资机构',
}

# 二级黑话：市场状态/走势
SIGNALS_STATE = {
    'ICU': '暴跌后的底部区域/极度悲观状态',
    'KTV': '暴涨行情/市场亢奋状态',
    '开线': '行情结束/暴涨后暴跌回调',
    '刷大火箭': '重仓追高/大额加仓',
    '地板': '股价处于底部区间',
    '天花板': '股价到达顶部区间',
    '半山腰': '股价处于中间位置，不上不下',
    '右侧': '趋势确认后的上涨阶段',
    '左侧': '趋势未确认的底部区域/逆向布局',
    '格局': '市场整体结构/大趋势判断',
    '高波': '高波动状态（波动率放大）',
    '缩量': '成交量萎缩，流动性下降',
    '放量': '成交量放大，资金活跃',
    '触底': '市场/个股触及底部',
    '反弹': '下跌后的技术性回升',
    '修复': '市场从悲观情绪中恢复',
    '企稳': '下跌后止跌，进入横盘整理',
    '分歧': '市场参与者意见不一致，多空博弈',
    '一致': '市场形成共识，方向明确',
    '兑现': '利好消息落地后获利了结',
    '高低切换': '资金从高位板块流向低位板块（板块轮动）',
    '泥沙俱下': '全市场普跌，不分好坏',
}

# 三级黑话：交易行为/操作
SIGNALS_ACTION = {
    '建仓': '主力开始买入建仓 🟢 积极信号',
    '加仓': '增加持仓比例 🟢 看好后市',
    '补仓': '下跌后买入降低成本 🟡 摊薄成本操作',
    '减仓': '减少持仓比例 🔴 规避风险',
    '清仓': '全部卖出离场 🔴 极度看空',
    '抄底': '在底部区域买入 🟢 左侧交易',
    '逃顶': '在顶部区域卖出 🟢 精准离场',
    '砸盘': '大资金集中卖出打压股价 🔴 负面',
    '护盘': '资金托市/维稳价格 🟡 支撑信号',
    '出货': '主力卖出离场 🔴 风险信号',
    '洗盘': '主力震荡清洗不坚定筹码 🟡 上涨前准备',
    '接货': '在低位承接抛盘 🟢 承接信号',
    '接筹': '在低位收集筹码 🟢 吸筹信号',
    '打满': '仓位加到上限/满仓',
    '做T': '当日先买后卖或先卖后买做差价',
    '锁仓': '持有不动，等待上涨',
    '抬轿': '追高买入为主力接盘 🔴 危险操作',
    '拉高出货': '拉升股价后趁机卖出 🔴 顶部信号',
    '定投': '定期定额买入 🟢 长线策略',
}

# 四级黑话：盈利/风险状态
SIGNALS_PROFIT = {
    '吃肉': '有大行情/有盈利空间 🟢 看多',
    '喝汤': '小幅盈利，没赚到大钱 🟡',
    '埋单': '买入后被套/亏损 🔴',
    '被埋': '深套/大幅亏损 🔴',
    '回本': '从亏损回到成本价',
    '割肉': '亏损卖出止损 🔴',
    '抄作业': '跟随大V/机构的操作',
    '确定性': '有明确逻辑支撑的投资机会 🟢',
    '弹性': '高波动/高beta品种，涨跌幅度大',
    '泡沫': '估值过高，有破裂风险 🔴 风险警示',
    '透支': '利好已提前price in，后续乏力 🔴',
    '兑现': '利好落地，获利了结 🔴',
}

# 五级黑话：特定事件/主题
SIGNALS_EVENTS = {
    '长鑫': '国内存储芯片巨头CXMT（合肥长鑫），其IPO是近期科技线核心事件',
    '中芯': '中芯国际（SMIC），国内芯片制造龙头',
    '英伟达': 'NVIDIA，全球AI算力龙头，其股价是AI泡沫风向标',
    '懂王': '特朗普（Donald Trump）',
    '老登': '拜登（Joe Biden）',
    '美联储': '美国联邦储备系统（FED），全球货币政策核心',
    '鲍威尔': '美联储主席，货币政策关键人物',
    '沃什': '前美联储理事，常被市场解读为鸽派/鹰派信号',
    '纳斯达克': 'Nasdaq指数，科技股风向标（尤其是AI板块）',
    '韩股': '韩国KOSPI指数，近期因韩国政治危机+杠杆问题暴跌',
    'bom交易': '泡沫股交易（meme stock/泡沫标的）',
    'AI泡沫': '人工智能板块估值过高风险',
    'IPO': '首次公开发行（新股上市）',
    '缴款': 'IPO申购后的资金缴付（影响市场流动性）',
    '业绩/中报': '上市公司半年度财务报告（7-8月密集发布）',
    '质押率': '股票质押比例，质押率低→强制平仓风险小',
    'QDII': '合格境内机构投资者（投资海外市场的通道）',
    '离岸人民币': '境外人民币市场（CNH），国际化指标',
    '美债': '美国国债，全球资产定价锚',
    '私募信贷': 'Private Credit，影子银行风险',
}

def interpret_weibo(text: str, author: str) -> str:
    """深度解读微博，返回结构化分析结果"""
    findings = []
    all_signals = {**SIGNALS_PARTICIPANTS, **SIGNALS_STATE,
                   **SIGNALS_ACTION, **SIGNALS_PROFIT, **SIGNALS_EVENTS}

    for keyword, meaning in all_signals.items():
        if keyword in text:
            findings.append(f"「{keyword}」→ {meaning}")

    # 组合完整解读
    output_parts = []
    if findings:
        output_parts.append("🔍 **黑话破译**")
        for f in findings[:8]:
            output_parts.append(f"> {f}")

    return "\n".join(output_parts)


# ── KOL事实核查：将博主数值断言对照行情数据验证 ──
import re as _re

def fact_check_kol_claims(text: str, quotes: dict = None, sectors: dict = None,
                           market_overview: dict = None, northbound: dict = None) -> list:
    """验证博主博文中的数值断言是否与行情数据一致。
    返回 str 列表，每项一条验证结果，带 ✅/⚠️ 标记。"""
    results = []
    if not text:
        return results

    # 1. 指数/板块涨跌幅校验
    # 匹配 "xxx涨/跌X%" 模式
    all_items = {}
    if quotes:
        all_items.update(quotes)
    if sectors:
        all_items.update(sectors)

    for name, q in all_items.items():
        if not q:
            continue
        try:
            actual_pct = float(str(q.get('change_pct', '0')).rstrip('%'))
        except (ValueError, TypeError):
            continue

        # 在博文中搜索 "指数名 + 涨/跌 + 数字%"
        pattern = _re.escape(name) + r'.*?[涨跌].*?(\d+\.?\d*)\s*%'
        m = _re.search(pattern, text)
        if not m:
            # 也试 "数字% + 的涨跌 + 指数名"
            pattern2 = r'(\d+\.?\d*)\s*%.*?' + _re.escape(name)
            m = _re.search(pattern2, text)
        if m:
            claimed = abs(float(m.group(1)))
            actual_abs = abs(actual_pct)
            diff = abs(claimed - actual_abs)
            if diff < 0.3:
                results.append(f"✅ {name}: 博主说{'涨' if actual_pct > 0 else '跌'}{claimed:.1f}%, 实际{actual_pct:+.2f}%, 一致 ✓")
            elif diff < 1.0:
                results.append(f"⚠️ {name}: 博主说{'涨' if actual_pct > 0 else '跌'}{claimed:.1f}%, 实际{actual_pct:+.2f}%, 偏差{diff:.1f}%")
            else:
                results.append(f"❌ {name}: 博主说{'涨' if actual_pct > 0 else '跌'}{claimed:.1f}%, 实际{actual_pct:+.2f}%, 偏差{diff:.1f}% ⚠️")

    # 2. 成交额校验 (万亿/亿)
    turnover = None
    if market_overview and market_overview.get('total_turnover'):
        turnover = market_overview['total_turnover'] / 1e8  # 转亿
    elif quotes:
        # 尝试从两市指数主连加总（腾讯api单位可能是千元）
        pass  # 不准确，跳过

    if turnover and turnover > 1000:  # 至少有数据
        # 匹配 "成交3.68万亿" 或 "成交量2.6万亿"
        for m in _re.finditer(r'(\d+\.?\d*)\s*万亿', text):
            claimed = float(m.group(1))
            claimed_yi = claimed * 10000  # 万亿转亿
            diff = abs(claimed_yi - turnover)
            if diff < 2000:
                results.append(f"✅ 成交额: 博主说{claimed:.2f}万亿, 实际{turnover/10000:.2f}万亿, 一致 ✓")
            else:
                results.append(f"⚠️ 成交额: 博主说{claimed:.2f}万亿, 实际{turnover/10000:.2f}万亿, 偏差{abs(claimed - turnover/10000):.2f}万亿")
        # 匹配 "成交X亿"（过滤掉不足千亿的噪音匹配，如"40亿"）
        for m in _re.finditer(r'[成放量交].*?(\d+\.?\d*)\s*亿', text):
            claimed = float(m.group(1))
            if claimed < 1000:  # 只验证千亿以上的成交额断言
                continue
            diff = abs(claimed - turnover)
            if diff < 2000:
                results.append(f"✅ 成交额: 博主说{claimed:.0f}亿, 实际{turnover:.0f}亿, 一致 ✓")
            else:
                results.append(f"⚠️ 成交额: 博主说{claimed:.0f}亿, 实际{turnover:.0f}亿, 偏差{abs(claimed - turnover):.0f}亿")

    # 3. 北向资金校验
    nb_total = None
    if northbound and northbound.get('total') is not None:
        nb_total = northbound['total']

    if nb_total is not None:
        # 匹配 "北向流出40亿" 或 "北向流入X亿"
        nb_pattern = r'北向[流出流入].*?(\d+\.?\d*)\s*亿'
        m = _re.search(nb_pattern, text)
        if m:
            claimed = float(m.group(1))
            claimed_sign = -1 if '流出' in m.group() else 1
            actual_sign = -1 if nb_total < 0 else 1
            diff = abs(abs(claimed * claimed_sign) - abs(nb_total))
            if diff < 10:
                results.append(f"✅ 北向: 博主说{'流出' if nb_total < 0 else '流入'}{m.group(1)}亿, 实际{nb_total:+.1f}亿, 一致 ✓")
            else:
                results.append(f"⚠️ 北向: 博主说{'流出' if nb_total < 0 else '流入'}{m.group(1)}亿, 实际{nb_total:+.1f}亿")

    return results


# ── 全量KOL分析引擎（从原始数据生成深度解读文件）──
def generate_kol_deep_analysis(kol_data: dict, quotes: dict = None,
                                fund_groups: dict = None) -> str:
    """从KOL原始帖子生成深度分析文本（黑话解读+操作映射）"""
    lines = ["📊 **KOL深度解读 · 今日操作映射**", ""]

    # ---- 1. 汇总段 ----
    sector_bullish = {}
    sector_bearish = {}
    all_signals = {**SIGNALS_PARTICIPANTS, **SIGNALS_STATE,
                   **SIGNALS_ACTION, **SIGNALS_PROFIT, **SIGNALS_EVENTS}

    for uid, kd in kol_data.items():
        name = kd['name']
        for p in kd.get('posts', []):
            txt = p['text']
            # 每个帖子提取黑话
            matched = [kw for kw in all_signals if kw in txt]
            # 判断方向（简化版）
            is_bullish = any(w in txt for w in _DIRECTION_BULLISH)
            is_bearish = any(w in txt for w in _DIRECTION_BEARISH)
            # 判断涉及赛道
            sectors_mentioned = set()
            for sector, kws in SECTOR_KEYWORDS.items():
                if any(kw.lower() in txt.lower() for kw in kws):
                    sectors_mentioned.add(sector)

            for sec in sectors_mentioned:
                if is_bullish:
                    sector_bullish[sec] = sector_bullish.get(sec, 0) + 1
                elif is_bearish:
                    sector_bearish[sec] = sector_bearish.get(sec, 0) + 1

    # ---- 2. 整体判断 ----
    net_score = sum(sector_bullish.values()) - sum(sector_bearish.values())
    if net_score >= 3:
        lines.append("**🔴 整体偏多** — KOL共识积极，关注加仓机会")
    elif net_score <= -3:
        lines.append("**🟢 整体偏空** — KOL共识谨慎，注意控制仓位")
    else:
        lines.append("**🟡 整体中性** — KOL观点分歧，等待明确信号")

    lines.append("")

    # ---- 3. 赛道逐项分析 ----
    lines.append("**📊 赛道情绪扫描**")
    lines.append("| 赛道 | 看多 | 看空 | 净方向 | 信号等级 |")
    lines.append("|:----|:---:|:---:|:-----:|:--------:|")
    all_sectors = set(list(sector_bullish.keys()) + list(sector_bearish.keys()))
    for sec in sorted(all_sectors):
        b = sector_bullish.get(sec, 0)
        s = sector_bearish.get(sec, 0)
        net = b - s
        if net >= 2:
            level = "🔴积极看多"
        elif net >= 1:
            level = "📈偏多"
        elif net <= -2:
            level = "🟢积极看空"
        elif net <= -1:
            level = "📉偏空"
        else:
            level = "➖中性"
        lines.append(f"| {sec} | {b} | {s} | {net:+d} | {level} |")
    lines.append("")

    # ---- 4. 按博主逐条深度解读（关键信号博文）----
    lines.append("**📌 关键信号解读**")
    signal_phrases = ['IPO', '触底', '泡沫', '加仓', '减仓', '反弹', '清仓',
                      '缩量', '放量', 'ICU', 'KTV', '长鑫', '泡沫', '业绩',
                      '底部', '抄底', '右侧', '格局', '高波']
    for uid, kd in kol_data.items():
        name = kd['name']
        lines.append("")
        lines.append(f"**{name} 关键信号**")
        for p in kd.get('posts', []):
            txt = p['text']
            # 只分析有信号词的博文
            if not any(sp in txt for sp in signal_phrases):
                continue
            # 提取前200字
            excerpt = txt[:200].replace('\n', ' ')
            lines.append(f"> 📝 _{excerpt}..._")
            # 深度解读
            depth = interpret_weibo(txt, name)
            if depth:
                lines.append(f"{depth}")
            lines.append("")

    # ---- 5. 操作建议映射 ----
    lines.append("")
    lines.append("**🎯 操作建议映射**")
    lines.append("| 组别 | 方向 | 参考操作 |")
    lines.append("|:----|:----:|:--------|")

    for gname in ['科技/AI', '黄金', '资源/周期', '新能源', '医药']:
        b = sector_bullish.get(gname, 0)
        s = sector_bearish.get(gname, 0)
        net = b - s
        if net >= 2:
            direction = "🔴积极"
            action = "逢跌加仓，关注催化事件"
        elif net >= 1:
            direction = "📈偏多"
            action = "持有为主，可小幅加仓"
        elif net <= -2:
            direction = "🟢谨慎"
            action = "减少仓位，等待企稳信号"
        elif net <= -1:
            direction = "📉偏空"
            action = "持有不动，不加仓"
        else:
            direction = "➖中性"
            action = "持有观望，等待明确信号"
        lines.append(f"| {gname} | {direction} | {action} |")

    lines.append("")
    lines.append("> ⚠️ 以上分析基于关键词规则匹配，仅供参考")
    return "\n".join(lines)


# ══════════════════════════════════════════════
# 6. R2 存储
# ══════════════════════════════════════════════

def upload_to_r2(file_path: str, key: str, content_type: str = None) -> Optional[str]:
    import subprocess
    hermes_python = "/opt/hermes/.venv/bin/python3"
    r2_script = str(DATA_DIR / "r2_uploader.py")
    try:
        args = [hermes_python, r2_script, file_path, key]
        if content_type:
            args.append(content_type)
        result = subprocess.run(
            args,
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            url = result.stdout.strip().split('\n')[-1]
            return url if url.startswith('http') else None
        else:
            print(f"  ⚠️ R2 upload error: {result.stderr[:200]}")
    except Exception as e:
        print(f"  ⚠️ R2 upload exception: {e}")
    return None

def upload_to_r2_bytes(data: bytes, key: str, content_type: str = "application/json") -> Optional[str]:
    tmp = DATA_DIR / "tmp_fund_upload.json"
    tmp.write_bytes(data)
    result = upload_to_r2(str(tmp), key, content_type)
    tmp.unlink(missing_ok=True)
    return result

def store_jsonl(record: dict, filename: str):
    today = date.today().isoformat()
    local_path = DATA_DIR / f"fund_system_data/{filename}"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    record['_stored_at'] = datetime.now().isoformat()
    record['_date'] = today
    with open(local_path, 'a') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    r2_key = f"{FUND_SYSTEM_PREFIX}/data/{filename}"
    upload_to_r2(str(local_path), r2_key, "application/jsonl")
    return local_path


# ══════════════════════════════════════════════
# 7. 交易日判断（含节假日）
# ══════════════════════════════════════════════

# 2026年A股法定休市日（上交所公告：上证公告〔2025〕45号）
CHINESE_HOLIDAYS_2026 = {
    # 元旦：1/1(四)-1/3(六)，1/5(一)起
    '2026-01-01', '2026-01-02', '2026-01-03',
    # 春节：2/15(日)-2/23(一)，2/24(二)起
    '2026-02-15', '2026-02-16', '2026-02-17', '2026-02-18', '2026-02-19',
    '2026-02-20', '2026-02-21', '2026-02-22', '2026-02-23',
    # 清明：4/4(六)-4/6(一)，4/7(二)起
    '2026-04-04', '2026-04-05', '2026-04-06',
    # 劳动节：5/1(五)-5/5(二)，5/6(三)起
    '2026-05-01', '2026-05-02', '2026-05-03', '2026-05-04', '2026-05-05',
    # 端午：6/19(五)-6/21(日)，6/22(一)起
    '2026-06-19', '2026-06-20', '2026-06-21',
    # 中秋：9/25(五)-9/27(日)，9/28(一)起
    '2026-09-25', '2026-09-26', '2026-09-27',
    # 国庆：10/1(四)-10/7(三)，10/8(四)起
    '2026-10-01', '2026-10-02', '2026-10-03', '2026-10-04',
    '2026-10-05', '2026-10-06', '2026-10-07',
}

def _scrape_sse_holidays(year: int) -> set:
    """尝试从上交所官网抓取指定年份的休市安排。
    每年12月，上交所发布下一年公告（格式固定），此函数自动解析。
    若失败返回空集（回退到硬编码）。
    """
    try:
        url = f"https://www.sse.com.cn/disclosure/announcement/general/"
        # SSE通常会发布类似 c_20251222_10802507.shtml 格式的公告
        # 先搜索最新公告
        search_url = f"https://www.sse.com.cn/disclosure/dealinstruc/closed/"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return set()
        text = r.text
        # 尝试找到年份对应的闭市安排链接
        import re
        # 查找类似 /disclosure/announcement/general/c_2025xxxx_xxxxx.shtml 的链接
        links = re.findall(r'href=[\'"]?([^\'" >]+\.shtml)', text)
        holiday_urls = [l for l in links if 'dealinstruct' in l or 'closed' in l]
        return set()  # 占位，后续可完善解析逻辑
    except Exception:
        return set()

# 缓存自动抓取的节假日（惰性加载）
_auto_holidays_cache = {}

def get_chinese_holidays(year: int) -> set:
    """获取指定年份的A股法定休假日。优先自动抓取，回退硬编码。"""
    if year in _auto_holidays_cache:
        return _auto_holidays_cache[year]

    # 2026年用硬编码
    if year == 2026:
        return CHINESE_HOLIDAYS_2026

    # 其他年份：尝试自动抓取
    scraped = _scrape_sse_holidays(year)
    if scraped:
        _auto_holidays_cache[year] = scraped
        return scraped
    # 抓取失败则返回空集（所有工作日按交易日处理）
    return set()

def is_trading_day(d: Optional[date] = None) -> bool:
    """判断指定日期（默认今天）是否为A股交易日。"""
    if d is None:
        d = date.today()
    # 周末不交易
    if d.weekday() >= 5:
        return False
    # 法定节假日不交易
    holidays = get_chinese_holidays(d.year)
    if d.isoformat() in holidays:
        return False
    return True


# ══════════════════════════════════════════════
# 8. 基金分组统计
# ══════════════════════════════════════════════

GROUPS = {
    '科技/AI': ['011613', '024418', '026449', '014871', '020233', '017103', '011712'],
    '资源/周期': ['163302', '025857'],
    '黄金': ['009478'],
    '新能源': ['012329', '011103'],
    '医药': ['001551', '014565'],
}

# ── 持仓权重（2026-07-06 更新：新增医药组）
PORTFOLIO_WEIGHTS = {
    '黄金':     {'weight': 7,  'target_min': 3,  'target_max': 15, 'rebalance_trigger': 5},
    '科技/AI':  {'weight': 55, 'target_min': 40, 'target_max': 70, 'rebalance_trigger': 10},
    '资源/周期': {'weight': 12, 'target_min': 5,  'target_max': 20, 'rebalance_trigger': 5},
    '新能源':   {'weight': 6,  'target_min': 3,  'target_max': 15, 'rebalance_trigger': 5},
    '医药':     {'weight': 6,  'target_min': 3,  'target_max': 15, 'rebalance_trigger': 3},
}

# ── 用户实时持仓 ──
USER_PORTFOLIO_FILE = Path('/tmp/fund_data/_user_portfolio.json')

def load_user_portfolio() -> dict:
    """读取用户实时持仓（份额 × 成本价）"""
    if not USER_PORTFOLIO_FILE.exists():
        return {}
    try:
        return json.loads(USER_PORTFOLIO_FILE.read_text())
    except Exception:
        return {}

def save_user_portfolio(portfolio: dict):
    """保存用户实时持仓"""
    USER_PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    USER_PORTFOLIO_FILE.write_text(json.dumps(portfolio, ensure_ascii=False, indent=2))

def calc_group_actual_weights(fund_data: dict) -> dict:
    """根据用户真实持仓份额 × 当日净值, 计算各组实际权重"""
    portfolio = load_user_portfolio()
    if not portfolio or not fund_data:
        return {}  # 无持仓数据时返回空
    
    # 计算各组总市值
    group_values = defaultdict(float)
    total_value = 0.0
    for code, info in portfolio.items():
        shares = info.get('shares', 0)
        if shares <= 0:
            continue
        fv = fund_data.get(code)
        nav = float(fv.get('nav', 0)) if fv and fv.get('nav') else info.get('cost', 1)
        value = shares * nav
        group = None
        for gname, codes in GROUPS.items():
            if code in codes:
                group = gname
                break
        if group:
            group_values[group] += value
            total_value += value
    
    if total_value <= 0:
        return {}
    
    weights = {}
    for gname, val in group_values.items():
        weights[gname] = {
            'value': round(val, 2),
            'pct': round(val / total_value * 100, 1),
        }
    weights['_total'] = round(total_value, 2)
    return weights

# ── 组别操作判定规则（KOL信号 + 市场数据 → 操作建议）
GROUP_ACTION_RULES = {
    '黄金': {
        'buy_triggers': ['黄金期货连涨2日', 'KOL看多黄金', '避险情绪升温'],
        'sell_triggers': ['黄金期货连跌3日', '美元走强', 'KOL看空黄金'],
    },
    '科技/AI': {
        'buy_triggers': ['科创50涨>2%且放量', 'KOL看多科技', '半导体板块领涨'],
        'sell_triggers': ['科创50连跌3日', 'KOL提示科技过热', '北向大幅流出'],
    },
    '资源/周期': {
        'buy_triggers': ['有色板块涨>2%', '大宗商品反弹'],
        'sell_triggers': ['KOL提示周期见顶', '资源板块连跌5日'],
    },
    '新能源': {
        'buy_triggers': ['光伏/新能源板块领涨', 'KOL看多新能源'],
        'sell_triggers': ['新能源板块连跌', '利空政策'],
    },
    '医药': {
        'buy_triggers': ['医药板块领涨', 'KOL看多医药/创新药', '创新药政策利好'],
        'sell_triggers': ['医药板块连跌5日', '集采利空', 'KOL提示医药风险'],
    },
}

def group_funds(fund_data: dict) -> dict:
    result = {}
    for group_name, codes in GROUPS.items():
        items = []
        total_change = 0
        count = 0
        for code in codes:
            if code in fund_data and fund_data[code]:
                v = fund_data[code]
                v['code'] = code  # 注入code字段
                items.append(v)
                try:
                    total_change += float(v.get('estimated_change', 0) or 0)
                    count += 1
                except ValueError:
                    pass
        avg_change = round(total_change / count, 2) if count > 0 else 0
        result[group_name] = {
            'funds': items,
            'avg_change': avg_change,
            'count': count,
        }
    return result


# ── 趋势记录 + 操作评分 ──────────────────────
TREND_WINDOW_FILE = DATA_DIR / "fund_system_data" / "_group_trends.jsonl"

def record_group_trend(fund_data: dict):
    """每日收盘后记录各组涨跌趋势（用于N日连续判定）"""
    groups = group_funds(fund_data)
    record = {'_date': date.today().isoformat(), '_ts': datetime.now().isoformat()}
    for gname, gdata in groups.items():
        if gdata['count'] > 0:
            record[gname] = gdata['avg_change']
    TREND_WINDOW_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TREND_WINDOW_FILE, 'a') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f"  ✅ 趋势记录已保存 ({len(record)-2}组)")

def get_group_trend(group_name: str, days: int = 5) -> list:
    """读取最近N天该组涨跌幅，返回 [(date, change_pct), ...]"""
    if not TREND_WINDOW_FILE.exists():
        return []
    trends = []
    for line in open(TREND_WINDOW_FILE):
        try:
            rec = json.loads(line)
            val = rec.get(group_name)
            if val is not None:
                trends.append((rec['_date'], val))
        except Exception:
            pass
    return trends[-days:]


def check_rebalance(fund_data: dict) -> list:
    """检查实际持仓权重是否偏离目标，返回建议列表"""
    advice = []
    actual_weights = calc_group_actual_weights(fund_data)
    
    for gname, cfg in PORTFOLIO_WEIGHTS.items():
        if gname in actual_weights:
            # 用真实权重
            current_pct = actual_weights[gname]['pct']
        else:
            # 回退到估算（单日涨跌漂移）
            groups = group_funds(fund_data)
            gdata = groups.get(gname)
            if not gdata or gdata['count'] == 0:
                continue
            change = gdata['avg_change']
            drift = cfg['weight'] * (change / 100)
            current_pct = cfg['weight'] + drift
        
        if current_pct > cfg['target_max'] + cfg['rebalance_trigger']:
            advice.append({
                'group': gname, 'type': 'overweight', 'urgency': '中',
                'current_est': f"{current_pct:.0f}%",
                'target_max': f"{cfg['target_max']}%",
                'suggestion': f"占比{current_pct:.0f}%超出目标上限{cfg['target_max']}%，可考虑部分止盈",
            })
        elif current_pct < cfg['target_min'] - cfg['rebalance_trigger']:
            advice.append({
                'group': gname, 'type': 'underweight', 'urgency': '中',
                'current_est': f"{current_pct:.0f}%",
                'target_min': f"{cfg['target_min']}%",
                'suggestion': f"占比{current_pct:.0f}%低于目标下限{cfg['target_min']}%，可逢低补仓",
            })
    return advice


def score_group_action(group_name: str, quotes: dict, sectors: dict,
                       kol_signals: list, trend_data: list,
                       prev_action: str = None) -> dict:
    """给一组打分，返回操作建议 (得分 -5~+5)
    prev_action: 前一日建议（增持/减持/关注/观望/持有），用于防频繁翻转"""
    rules = GROUP_ACTION_RULES.get(group_name)
    if not rules:
        return {'group': group_name, 'score': 0, 'action': '持有', 'reasons': ['无规则定义']}

    score = 0
    reasons = []

    # 1. 趋势得分：最近N天连续涨跌
    if len(trend_data) >= 2:
        recent_changes = [c for _, c in trend_data[-3:]]
        avg_recent = sum(recent_changes) / len(recent_changes)
        if avg_recent > 1.5:
            score += 2
            reasons.append(f"近3日均涨{avg_recent:.2f}%，上升趋势")
        elif avg_recent < -1.5:
            score -= 2
            reasons.append(f"近3日均跌{avg_recent:.2f}%，下降趋势")
        elif avg_recent > 0.5:
            score += 1
            reasons.append(f"温和上行({avg_recent:+.2f}%)")
        elif avg_recent < -0.5:
            score -= 1
            reasons.append(f"温和下行({avg_recent:+.2f}%)")

    # 2. 板块动量得分
    sector_map = {
        '黄金': '黄金ETF市场价',
        '科技/AI': '科创50',
        '资源/周期': '有色金属',
        '新能源': '新能源',
        '医药': '医药',  # 新增医药板块关联
    }
    sector_key = sector_map.get(group_name)
    if sector_key and sector_key in quotes:
        q = quotes[sector_key]
        if q:
            try:
                cp = float(q['change_pct'])
                if cp > 2:
                    score += 2
                    reasons.append(f"{sector_key}大涨{cp:+.2f}%")
                elif cp > 1:
                    score += 1
                    reasons.append(f"{sector_key}涨{cp:+.2f}%")
                elif cp < -2:
                    score -= 2
                    reasons.append(f"{sector_key}大跌{cp:+.2f}%")
                elif cp < -1:
                    score -= 1
                    reasons.append(f"{sector_key}跌{cp:+.2f}%")
            except (ValueError, TypeError):
                pass

    # 3. KOL信号得分
    if kol_signals:
        for sig in kol_signals:
            s_name = sig.get('kol_name', '')
            s_text = sig.get('text_snippet', '')
            s_dir = sig.get('predicted_direction', 'neutral')
            sector_match = any(kw in s_text for kw in [group_name, sector_key or ''])
            if sector_match:
                if s_dir == 'bullish':
                    score += 1
                    reasons.append(f"{s_name}看多{group_name}")
                elif s_dir == 'bearish':
                    score -= 1
                    reasons.append(f"{s_name}看空{group_name}")

    # 4. 综合判定（含稳定性逻辑）
    raw_action = '持有'
    if score >= 3:
        raw_action = '增持'
    elif score <= -3:
        raw_action = '减持'
    elif score >= 1:
        raw_action = '关注'
    elif score <= -1:
        raw_action = '观望'

    # 稳定性：如果前日有明确方向，避免一天就翻转
    action = raw_action
    if prev_action and prev_action != '持有':
        flip_warnings = {
            ('增持', '减持'): ('前日建议增持，今日数据转弱但不建议立即翻空', -2),
            ('增持', '观望'):  ('前日建议增持，今日数据偏弱转为观望', -1),
            ('减持', '增持'): ('前日建议减持，今日数据转好但不建议立即翻多', 2),
            ('减持', '关注'):  ('前日建议减持，今日数据回暖转为关注', 1),
            ('关注', '观望'):  ('前日建议关注，今日数据偏弱转为中性', 0),
            ('关注', '减持'):  ('前日建议关注，今日数据恶化但暂不建议直接翻空', -1),
            ('观望', '关注'):  ('前日建议观望，今日数据回暖转为中性', 0),
            ('观望', '增持'):  ('前日建议观望，今日数据转好但暂不建议直接翻多', 1),
        }
        flip = (prev_action, raw_action)
        if flip in flip_warnings:
            msg, interim_score = flip_warnings[flip]
            action = '持有'  # 强制中性过渡
            # 保留原始score用于显示，但action强制稳定
            reasons.append(f"🛑 {msg}")

    return {
        'group': group_name,
        'score': score,
        'action': action,
        'raw_action': raw_action,
        'urgency': '高' if abs(score) >= 4 else ('中' if abs(score) >= 2 else '低'),
        'reasons': reasons[:4],
    }


# ══════════════════════════════════════════════
# 9. 数据合理性校验 (维度A)
# ══════════════════════════════════════════════

_SANITY_RANGES = {
    'quotes': {
        '上证指数': (2500, 4500),
        '创业板指': (1500, 5000),
        '科创50': (800, 3000),
        '沪深300': (3000, 6000),
        '上证50': (2000, 4000),
        '黄金ETF市场价': (5, 15),
    },
    'turnover_billions': (500, 50000),
    'breadth_total': 100,
    'fund_success_rate': 0.60,
    'sector_success_rate': 0.50,
}

def run_sanity_checks(raw_data: dict) -> dict:
    """验证采集数据的合理性，返回 {status, checks[], warnings[]}"""
    checks = []
    warnings = []

    quotes = raw_data.get('quotes', {}) or {}
    for name, q in quotes.items():
        if not q:
            continue
        try:
            price = float(q.get('price', 0))
            lo, hi = _SANITY_RANGES['quotes'].get(name, (0, 99999))
            if price <= 0:
                warnings.append(f"{name}: 价格为0")
            elif price < lo:
                warnings.append(f"{name}: {price} 低于合理范围({lo}-{hi})")
            elif price > hi:
                warnings.append(f"{name}: {price} 高于合理范围({lo}-{hi})")
        except (ValueError, TypeError):
            warnings.append(f"{name}: 价格无法解析")
    checks.append(f"📈 大盘指数: {sum(1 for v in quotes.values() if v)}/{len(quotes)}")

    sectors = raw_data.get('sectors', {}) or {}
    sector_ok = sum(1 for v in sectors.values() if v)
    sector_total = len(sectors)
    if sector_total > 0:
        sector_rate = sector_ok / sector_total
        status = '✅' if sector_rate >= _SANITY_RANGES['sector_success_rate'] else '⚠️'
        checks.append(f"{status} 📊 板块: {sector_ok}/{sector_total}")
        if sector_rate < _SANITY_RANGES['sector_success_rate']:
            warnings.append(f"板块采集率仅 {sector_rate:.0%}")

    overview = raw_data.get('market_overview', {}) or {}
    rise = overview.get('rise_count', 0)
    fall = overview.get('fall_count', 0)
    total = (rise or 0) + (fall or 0)
    if total > 0:
        status = '✅' if total >= _SANITY_RANGES['breadth_total'] else '⚠️'
        limit_up = raw_data.get('limit_up', 0)
        limit_down = raw_data.get('limit_down', 0)
        limit_str = f" 涨停{limit_up}/跌停{limit_down}" if limit_up else ''
        checks.append(f"{status} 📈 涨跌家数: 涨{rise} 跌{fall} (合计{total}){limit_str}")
        if total < _SANITY_RANGES['breadth_total']:
            warnings.append(f"涨跌家数合计仅{total}，可能非交易时段")
    else:
        checks.append("ℹ️ 涨跌家数: 无数据（跳过）")

    turnover = overview.get('total_turnover', 0) or 0
    if turnover > 0:
        turnover_b = turnover / 1e8
        lo, hi = _SANITY_RANGES['turnover_billions']
        if turnover_b < lo:
            warnings.append(f"成交额{turnover_b:.0f}亿 低于合理范围({lo}-{hi}亿)")
        status = '✅' if lo <= turnover_b <= hi else '⚠️'
        checks.append(f"{status} 💰 两市成交: {turnover_b:.0f}亿")
    else:
        checks.append("ℹ️ 成交额: 无数据（跳过）")

    nf = raw_data.get('northbound', {}) or {}
    north_total = nf.get('total')
    if north_total is not None:
        status = '✅' if -200 <= north_total <= 200 else '⚠️'
        checks.append(f"{status} 🌊 北向: {north_total:+.2f}亿")
        if north_total < -200 or north_total > 200:
            warnings.append(f"北向资金{north_total:+.2f}亿超出正常范围(-200~+200)")
    else:
        checks.append("ℹ️ 北向: 无数据（跳过）")

    funds = raw_data.get('funds', {}) or {}
    fund_ok = sum(1 for v in funds.values() if v)
    fund_total = len(funds)
    if fund_total > 0:
        fund_rate = fund_ok / fund_total
        status = '✅' if fund_rate >= _SANITY_RANGES['fund_success_rate'] else '⚠️'
        checks.append(f"{status} 💰 基金: {fund_ok}/{fund_total} ({fund_rate:.0%})")
        if fund_rate < _SANITY_RANGES['fund_success_rate']:
            warnings.append(f"基金采集率仅{fund_rate:.0%}，低于60%阈值")
    else:
        checks.append("ℹ️ 基金: 无数据（跳过）")

    kols = raw_data.get('kol_posts', {}) or {}
    if kols:
        total_posts = sum(len(kd.get('posts', [])) for kd in kols.values())
        status = '✅' if len(kols) > 0 else '⚠️'
        checks.append(f"{status} 📰 KOL: {len(kols)}位, {total_posts}条博文")
    else:
        checks.append("ℹ️ KOL: 本推送无采集（收盘复盘不拉取）")

    return {
        'checked_at': datetime.now().isoformat(),
        'checks': checks,
        'warnings': warnings,
        'issue_count': len(warnings),
        'status': '⚠️' if warnings else '✅',
    }


# ══════════════════════════════════════════════
# 10. 信号归因追踪 (维度B)
# ══════════════════════════════════════════════

_SIGNAL_SECTOR_MAP = {
    '科技': '科创50', 'AI': '科创50', '半导体': '科创50',
    '大盘': '上证指数', 'A股': '上证指数',
    '创业板': '创业板指', '中小盘': '创业板指',
    '权重': '上证50', '黄金': '黄金ETF市场价',
}

_DIRECTION_BULLISH = {'右侧', '加仓', '补仓', '接货', '接筹', '触底', '反弹', '抄底', '建仓', '吃肉'}
_DIRECTION_BEARISH = {'泡沫', '风险', '过热', '警惕', '回调', '出货', '洗盘', '砸盘', '左侧'}

# 全文本方向扫描词典（KOL实际用语扩充版）
_DIRECTION_BULLISH_FULL = _DIRECTION_BULLISH | {
    '看多', '做多', '低位', '地板', '吸筹', '买入', '增持', '机会', '利好',
    '趋势向上', '突破', '放量上攻', '探底回升', '企稳', '止跌', '反攻',
    '加', '上车', '主力买入', '机构进场', '估值修复', '戴维斯双击',
}
_DIRECTION_BEARISH_FULL = _DIRECTION_BEARISH | {
    '看空', '做空', '做减法', '卖出', '减持', '利空', '警告', '下跌',
    '趋势向下', '跌破', '放量下跌', '缩量阴跌', '滞涨', '见顶',
    '减', '逃顶', '主力出逃', '机构减仓', '估值过高', '估值泡沫',
    '强弩之末', '分歧加大',
}


def extract_signals_from_kols(kol_posts: dict, push_type: str = 'morning_brief', quotes: dict = None) -> list:
    """从KOL博文中提取交易信号，返回信号列表"""
    today = date.today().isoformat()
    signals = []
    for uid, kd in kol_posts.items():
        name = kd.get('name', '?')
        for p in kd.get('posts', []):
            text = p.get('text', '')
            found_words = [w for w in {**SIGNALS_PARTICIPANTS, **SIGNALS_STATE, **SIGNALS_ACTION, **SIGNALS_PROFIT, **SIGNALS_EVENTS} if w in text]
            if not found_words:
                continue
            # 方向检测：同时检查found_words和全文本（解决neutral泛滥问题）
            bullish = sum(1 for w in found_words if w in _DIRECTION_BULLISH)
            bearish = sum(1 for w in found_words if w in _DIRECTION_BEARISH)
            # 全文本方向扫描（扩充词典）
            bullish += sum(1 for w in _DIRECTION_BULLISH_FULL if w in text)
            bearish += sum(1 for w in _DIRECTION_BEARISH_FULL if w in text)
            direction = 'bullish' if bullish > bearish else ('bearish' if bearish > bullish else 'neutral')
            predicted_sectors = set()
            for sk, idx in _SIGNAL_SECTOR_MAP.items():
                if sk in text:
                    predicted_sectors.add(idx or sk)
            if not predicted_sectors:
                predicted_sectors.add('大盘')
            index_price = None
            for ps in predicted_sectors:
                if ps and quotes:
                    q = quotes.get(ps)
                    if q:
                        try:
                            index_price = float(q.get('price', 0))
                        except Exception:
                            pass
                        break
            signals.append({
                'date': today, 'push_type': push_type,
                'kol_uid': uid, 'kol_name': name,
                'signal_words': found_words[:5],
                'text_snippet': text[:120].replace('\\n', ' '),
                'predicted_sector': list(predicted_sectors)[0],
                'predicted_direction': direction,
                'pred_index_price': index_price,
                'resolved': False,
            })
    # 同时用kol_analysis框架做深度分析（不影响原有格式）
    try:
        from kol_analysis import analyze_from_kol_data
        kol_data = {uid: {'name': kd.get('name', '?'), 'posts': kd.get('posts', [])}
                     for uid, kd in kol_posts.items()}
        analysis = analyze_from_kol_data(kol_data, quotes or {})
        for s in analysis.get('signals', []):
            if s.get('confidence', 0) >= 60:  # 只保存高置信度信号
                signals.append({
                    'date': today, 'push_type': f'{push_type}_v2',
                    'kol_uid': uid, 'kol_name': s.get('kol', '?'),
                    'signal_words': s.get('matched', []),
                    'text_snippet': s.get('claim', '')[:120],
                    'predicted_sector': s['sector'],
                    'predicted_direction': s['direction'],
                    'pred_index_price': None,
                    'resolved': False,
                    'confidence': s['confidence'],
                    'timeframe': s.get('timeframe', 'soon'),
                    'verification': s.get('verification', {}),
                })
    except Exception:
        pass
    return signals


def store_signals(signals: list):
    """追加信号到 signals.jsonl"""
    if not signals:
        return
    path = DATA_DIR / "fund_system_data" / "signals.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    for s in signals:
        s['_stored_at'] = datetime.now().isoformat()
        with open(path, 'a') as f:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')
    upload_to_r2(str(path), f"{FUND_SYSTEM_PREFIX}/data/signals.jsonl", "application/jsonl")


def resolve_past_signals(today_date: date = None, quotes: dict = None) -> list:
    """查询3-7天前的未解析信号，对比实际走势标记结果"""
    if today_date is None:
        today_date = date.today()
    check_from = (today_date - timedelta(days=7)).isoformat()
    past_date = (today_date - timedelta(days=4)).isoformat()
    signal_path = DATA_DIR / "fund_system_data" / "signals.jsonl"
    if not signal_path.exists():
        return []
    pending = {}
    with open(signal_path) as f:
        for line in f:
            s = json.loads(line.strip())
            if s.get('resolved'):
                continue
            if check_from <= s['date'] <= past_date:
                sid = f"{s['date']}_{s['kol_uid']}_{s.get('text_snippet','')[:20]}"
                pending[sid] = s
    if not pending or not quotes:
        return []
    resolved = []
    for sid, s in pending.items():
        sector = s.get('predicted_sector', '大盘')
        q = quotes.get(sector)
        if not q:
            continue
        try:
            actual_change = float(q.get('change_pct', 0))
        except (ValueError, TypeError):
            continue
        pred_dir = s.get('predicted_direction')
        # 判断正确性：bullish→涨, bearish→跌, neutral→看幅度推断
        if pred_dir == 'bullish':
            correct = actual_change > 0
        elif pred_dir == 'bearish':
            correct = actual_change < 0
        else:
            # neutral: 如果行业波动>1.5%则视为"有信息量",否则"无法判断"
            correct = None  # 仍为无法判断
        # 增加信号强度评估
        magnitude = abs(actual_change)
        signal_strength = 'strong' if magnitude > 2 else ('moderate' if magnitude > 1 else 'weak')
        
        resolved.append({
            'signal_id': sid, 'signal_date': s['date'],
            'kol_name': s['kol_name'], 'text_snippet': s['text_snippet'],
            'predicted_direction': pred_dir, 'predicted_sector': sector,
            'actual_change_pct': actual_change, 'correct': correct,
            'magnitude': round(magnitude, 2),
            'signal_strength': signal_strength,
            'resolved_at': datetime.now().isoformat(),
        })
    if resolved:
        r_path = DATA_DIR / "fund_system_data" / "signals-resolved.jsonl"
        r_path.parent.mkdir(parents=True, exist_ok=True)
        for r in resolved:
            with open(r_path, 'a') as f:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        upload_to_r2(str(r_path), f"{FUND_SYSTEM_PREFIX}/data/signals-resolved.jsonl", "application/jsonl")
    return resolved


def generate_signal_report() -> dict:
    """从signals-resolved.jsonl生成信号准确率报告"""
    r_path = DATA_DIR / "fund_system_data" / "signals-resolved.jsonl"
    if not r_path.exists():
        return {'summary': '尚无已解析信号', 'kol_stats': {}}
    from collections import defaultdict
    stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'details': []})
    cutoff = (date.today() - timedelta(days=30)).isoformat()
    with open(r_path) as f:
        for line in f:
            r = json.loads(line.strip())
            if r.get('signal_date', '') < cutoff:
                continue
            name = r.get('kol_name', '?')
            stats[name]['total'] += 1
            if r.get('correct'):
                stats[name]['correct'] += 1
            stats[name]['details'].append({
                'date': r.get('signal_date'), 'text': r.get('text_snippet', '')[:60],
                'dir': r.get('predicted_direction'), 'sector': r.get('predicted_sector'),
                'actual': r.get('actual_change_pct'), 'correct': r.get('correct'),
            })
    kol_stats = {}
    for name, s in stats.items():
        acc = round(s['correct'] / s['total'] * 100) if s['total'] > 0 else 0
        kol_stats[name] = {
            'total_signals': s['total'], 'correct': s['correct'],
            'accuracy': acc, 'status': '✅' if acc >= 70 else ('🔶' if acc >= 50 else '❌'),
            'details': s['details'][-10:],
        }
    return {
        'generated_at': datetime.now().isoformat(),
        'period': f"近30天 ({cutoff} ~ 今天)",
        'total_resolved': sum(s['total_signals'] for s in kol_stats.values()),
        'kol_stats': kol_stats,
    }


# ══════════════════════════════════════════════
# 7. 量价分析
# ══════════════════════════════════════════════

def get_volume_analysis(quotes: dict, sectors: dict, prev_total_turnover: float = None) -> dict:
    """
    从已有的腾讯行情数据生成量价分析。
    
    quotes: {品种名: {price, change_pct, volume, turnover, high, low, prev_close}}
    sectors: {板块名: {price, change_pct, volume, turnover, high, low, prev_close}}
    prev_total_turnover: 前日两市总成交额（亿），用于判断放量/缩量
    
    返回: {
        'total_turnover_now': float,  # 当前半日总成交额(亿)
        'volume_signals': [           # 量价信号列表
            {'name': str, 'change_pct': float, 'amplitude': float, 'signal': str, 'emoji': str, 'volume': str}
        ],
        'total_signal': str,          # 总体量价判断
        'turnover_change': str,       # 相对前日变化描述
        'amplitude_summary': str,     # 振幅异常汇总
        'text_summary': str,          # 纯文本摘要行（供LLM直接使用）
    }
    """
    result = {
        'volume_signals': [],
        'text_lines': [],
    }
    
    # 计算当前总成交额（从上证+深证）
    total_turnover = 0
    for name, q in quotes.items():
        if not q:
            continue
        if '上证指数' in name or '深证成指' in name:
            try:
                total_turnover += float(q.get('turnover', 0))
            except (ValueError, TypeError):
                pass
    
    total_turnover_billion = total_turnover / 10000  # 万→亿
    result['total_turnover_now'] = round(total_turnover_billion, 0)
    
    # 整理所有品种（指数+板块）
    all_items = []
    for name, q in {**quotes, **sectors}.items():
        if not q:
            continue
        try:
            price = float(q['price'])
            pct = float(q['change_pct'])
            high = float(q.get('high', 0) or 0)
            low = float(q.get('low', 0) or 0)
            prev = float(q.get('prev_close', 0) or 1)
            vol = float(q.get('volume', 0))
            turn = float(q.get('turnover', 0))
        except (ValueError, TypeError):
            continue
        if prev <= 0:
            continue
        
        amplitude = (high - low) / prev * 100
        
        # 量价信号分类
        if pct > 1.5 and amplitude > 3:
            signal, emoji = '放量上攻', '🔥'
        elif pct > 0.5 and amplitude > 1.5:
            signal, emoji = '温和放量', '📈'
        elif pct < -1.0 and amplitude > 3:
            signal, emoji = '放量下跌', '💧'
        elif pct < -0.5 and amplitude > 2:
            signal, emoji = '放量回调', '📉'
        elif abs(pct) < 0.3 and amplitude < 1.5:
            signal, emoji = '缩量横盘', '➖'
        elif pct > 0 and amplitude > 2:
            signal, emoji = '放量反弹', '🔥'
        elif pct < 0 and amplitude < 1.5:
            signal, emoji = '缩量阴跌', '💧'
        else:
            signal, emoji = '正常波动', '🔸'
        
        # 成交量格式化
        if turn > 1000000:  # >100亿
            vol_str = f'{turn/10000:.0f}亿'
        elif turn > 10000:
            vol_str = f'{turn/10000:.1f}亿'
        else:
            vol_str = f'{turn:.0f}万'
        
        all_items.append({
            'name': name,
            'change_pct': pct,
            'amplitude': round(amplitude, 1),
            'signal': signal,
            'emoji': emoji,
            'volume': vol_str,
        })
    
    # 排序：振幅从大到小
    all_items.sort(key=lambda x: x['amplitude'], reverse=True)
    
    # 生成成交量变化描述
    if prev_total_turnover and prev_total_turnover > 0:
        ratio = total_turnover_billion / prev_total_turnover * 100
        if ratio > 120:
            turnover_change = f'较前日放量{ratio-100:.0f}%↑'
        elif ratio > 100:
            turnover_change = f'较前日微幅放量↑'
        elif ratio > 80:
            turnover_change = f'较前日缩量至{ratio:.0f}%↓'
        else:
            turnover_change = f'较前日明显缩量至{ratio:.0f}%↓'
    else:
        turnover_change = ''
    
    # 振幅异常汇总
    high_amp = [i for i in all_items if i['amplitude'] > 4]
    amp_summary = f'振幅异常（>4%）：{len(high_amp)}个' if high_amp else '振幅正常'
    
    # 总体信号
    strong_ups = [i for i in all_items if i['change_pct'] > 1.5 and i['amplitude'] > 3]
    strong_downs = [i for i in all_items if i['change_pct'] < -1.0 and i['amplitude'] > 3]
    if len(strong_ups) > len(strong_downs):
        total_signal = '偏强：多方放量上攻'
    elif len(strong_downs) > len(strong_ups):
        total_signal = '偏弱：空方放量砸盘'
    else:
        total_signal = '震荡：多空博弈激烈'
    
    result['volume_signals'] = all_items
    result['total_signal'] = total_signal
    result['turnover_change'] = turnover_change
    result['amplitude_summary'] = amp_summary
    
    # 生成纯文本摘要行（用于预格式化表格）
    text_lines = []
    text_lines.append(f"💰 两市成交{total_turnover_billion:.0f}亿")
    if turnover_change:
        text_lines.append(turnover_change)
    text_lines.append(f"| {'总量':>10} | {'':>8} | {'':>6} | {total_signal} |")
    text_lines.append('')
    
    result['text_summary'] = '\n'.join(text_lines)
    
    return result
