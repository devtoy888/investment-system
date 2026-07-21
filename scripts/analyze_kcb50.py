"""分析科创50成分股行业构成"""
import requests, json, re

headers = {"User-Agent":"Mozilla/5.0"}

# 拉011613科创50ETF持仓
url = "https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=011613&topline=50&year=&month="
r = requests.get(url, headers=headers, timeout=15)
content = r.text
m = re.search(r'content:"(.*?)",', content, re.DOTALL)
if not m:
    print("无数据")
    exit()

raw = m.group(1).replace('\\r', '').replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
import html
raw = bytes(raw, 'utf-8').decode('unicode_escape')

# 从表格中提取：序号 股票代码 股票名称 占净值比例
rows = re.findall(
    r'<tr>.*?<td[^>]*>(\d+)</td>'  
    r'.*?<td[^>]*>(\d+)</td>'      
    r'.*?<td[^>]*>([^<]+)</td>'    
    r'.*?<td[^>]*>[^<]*</td>'      
    r'.*?<td[^>]*>[^<]*</td>'      
    r'.*?<td[^>]*>([^<]+)</td>',   
    raw, re.DOTALL
)

# 行业分类
def classify(stock_name):
    kw_map = {
        '半导体': ['中芯','华虹','中微','澜起','海光','寒武','芯原','拓荆','晶晨','乐鑫','恒玄','兆易','思瑞浦','芯朋','天岳'],
        '光伏/新能源': ['天合光能','大全能源','固德威','派能科技','奥特维','海优新材'],
        '医药/医疗': ['联影医疗','荣昌生物','百济神州','君实','神州细胞','康希诺'],
        'AI/软件': ['金山办公','中控技术','中望软件','奇安信','安恒信息'],
        '高端制造': ['时代电气','中无人机','铁建重工','电气风电'],
        '消费电子': ['传音控股','石头科技'],
    }
    for sec, kws in kw_map.items():
        for kw in kws:
            if kw in stock_name:
                return sec
    return '其他'

sectors = {}
for row in rows[:50]:
    rank = row[0]
    code = row[1][:6] if len(row[1])>=6 else row[1]
    name = row[2]
    pct = float(row[3]) if row[3].replace('.','').isdigit() else 0
    sec = classify(name)
    sectors.setdefault(sec, {'count':0, 'total_pct':0.0})
    sectors[sec]['count'] += 1
    sectors[sec]['total_pct'] += pct

total = sum(v['total_pct'] for v in sectors.values())
print(f"科创50成分股行业分布（基于011613持仓）:")
print(f"{'行业':<12} {'支数':>4} {'占比':>8}")
print("-"*30)
for sec, v in sorted(sectors.items(), key=lambda x: -x[1]['total_pct']):
    bar = '█' * int(v['total_pct'])
    print(f"  {sec:<10} {v['count']:>3}  {v['total_pct']:>5.1f}% {bar}")
print(f"\n总计: {total:.1f}%（其余为现金/其他）")
