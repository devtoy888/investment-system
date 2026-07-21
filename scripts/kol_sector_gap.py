#!/usr/bin/env python3
"""Compare Tang's industry recommendations vs user's holdings"""
import json

data = json.loads(open('/tmp/kol_tang_extra.json').read())
posts = data['2014433131']['posts']

USER_HOLDINGS = {
    'name': ['科创50C','半导体C','沪港深科技C','ESG混合C',
             '黄金C','黄金C','新能源C','创新药C',
             '资源LOF','恒生科技C','通航C'],
    'code': ['011613','012552','016803','012045',
             '002963','009477','013209','012879',
             '014280','013403','016298'],
}

USER_COVERAGE = {
    '科技/半导体':['011613','012552','016803','012045'],
    '黄金':['002963','009477'],
    '新能源':['013209'],
    '医药/创新药':['012879'],
    '资源':['014280'],
    '恒生科技/港股':['013403'],
    '通航/航空':['016298'],
}

INDUSTRY_KW = {
    '存储芯片':['存储','DRAM','NAND','HBM','长鑫','内存','闪存'],
    'AI/大模型':['AI','大模型','OpenAI','英伟达','算力','人工智能'],
    '光通信/光模块':['光模块','光纤','光通信','玻璃基','光学桥','CPO'],
    '功率半导体':['功率','IGBT','SiC','碳化硅'],
    '半导体设备':['设备','刻蚀','薄膜','沉积','光刻'],
    '封装测试':['封装','先进封装','Chiplet','CoWoS'],
    '芯片设计':['芯片','SoC','CPU','GPU','NPU','DPU'],
    '消费/白酒':['消费','白酒','茅台','五粮液','酒'],
    '新能源':['新能源','光伏','锂电','电动车','风光'],
    '军工':['军工','国防','航天','航空','军','航母'],
    '医药/医疗':['医药','医疗','创新药','CXO','器械'],
    '金融/券商':['券商','保险','银行','金融','证券'],
    '电力/能源':['电力','电','电网','能源','煤炭','石油'],
    '机器人':['机器人','人形','具身','机器狗'],
    '商业航天':['商业航天','卫星','火箭','低空'],
    '汽车':['汽车','自动驾驶','智能驾驶'],
    '数据中心':['数据中心','IDC','算力中心'],
    '通信':['通信','5G','6G','基站'],
}

# Count hits
hits = {}
for ind, kws in INDUSTRY_KW.items():
    c = sum(1 for p in posts if any(k in p['text'] for k in kws))
    if c > 0:
        ex = []
        for p in posts:
            if any(k in p['text'] for k in kws):
                ex.append(p['text'][:100].replace('\n',' '))
                if len(ex) >= 2: break
        hits[ind] = {'c':c, 'pct':round(c/len(posts)*100,1), 'ex':ex}

# Coverage map
COV = {
    '科技/半导体':['存储芯片','AI/大模型','光通信/光模块','功率半导体','半导体设备','封装测试','芯片设计','机器人','数据中心','通信'],
    '新能源':['新能源'],
    '医药/创新药':['医药/医疗'],
    '资源':['电力/能源'],
    '恒生科技/港股':['AI/大模型'],
    '通航/航空':['商业航天','军工'],
    '黄金':[],
}

print("="*70)
print("主任行业 vs 你的持仓 - 对照分析")
print("="*70)

print("\n你已有覆盖:")
for us, codes in USER_COVERAGE.items():
    names = [USER_HOLDINGS['name'][USER_HOLDINGS['code'].index(c)] for c in codes if c in USER_HOLDINGS['code']]
    related = [f'{ind}({hits[ind]["c"]}次)' for ind in COV.get(us,[]) if ind in hits]
    print(f"  {us}: {', '.join(names)}")
    if related: print(f"    主任相关: {' | '.join(related)}")

print(f"\n{'='*70}")
print("主任有、你没有的行业缺口")
print("="*70)
print(f"{'行业':16s} {'频次':8s} {'含买入信号':10s} {'优先级':12s}")
print("-"*50)

SIG = ['买','加仓','补','建仓','机会','确定性','核心','好','加']
UNCOV = ['光通信/光模块','功率半导体','半导体设备','封装测试','AI/大模型',
         '存储芯片','芯片设计','消费/白酒','军工','机器人','商业航天',
         '数据中心','通信','金融/券商','汽车']

gaps = []
for ind in UNCOV:
    if ind in hits:
        h = hits[ind]
        kws = INDUSTRY_KW[ind]
        sig_in = sum(1 for p in posts if any(k in p['text'] for k in kws) and any(s in p['text'] for s in SIG))
        sig_pct = round(sig_in/max(1,h['c'])*100)
        
        hi = '⭐⭐' if sig_pct >= 30 else ('⭐' if sig_pct >= 15 else '⚪')
        
        # Check coverage
        covered = False
        for us, codes in USER_COVERAGE.items():
            if ind in COV.get(us, []):
                covered = True
        
        if not covered:
            gaps.append((ind, h['c'], sig_pct, hi, h['pct']))
            print(f"  {ind:14s} {h['c']:3d}次({h['pct']:.0f}%) {sig_pct:3d}%    {hi}")

print(f"\n{'='*70}")
print("结论")
print("="*70)

print(f"\n你持有的行业: 科技/半导体 黄金 新能源 创新药 资源 恒生科技 通航")
print(f"主任关注但你无直接持仓的: {len(gaps)}个")

print("\n高优先级(含信号词>30%):")
for ind, c, sig_pct, hi, pct in gaps:
    if sig_pct >= 30:
        ex = hits[ind]['ex'][0] if hits[ind]['ex'] else ''
        print(f"  {ind}: {c}次, {sig_pct}%含操作信号")
        print(f"    {ex[:70]}")

print("\n中优先级:")
for ind, c, sig_pct, hi, pct in gaps:
    if 15 <= sig_pct < 30:
        print(f"  {ind}: {c}次, {sig_pct}%含操作信号")

print("\n低优先级(仅为提及):")
for ind, c, sig_pct, hi, pct in gaps:
    if sig_pct < 15:
        print(f"  {ind}: {c}次, 信号稀少")

json.dump({'gaps':gaps,'all_hits':hits}, open('/tmp/sector_gap.json','w'), ensure_ascii=False, indent=2)
print(f"\n-> /tmp/sector_gap.json")
