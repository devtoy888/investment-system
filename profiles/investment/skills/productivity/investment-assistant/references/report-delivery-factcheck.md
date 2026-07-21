# 报告交付与全量事实核查纪律（2026-07-16 用户纠正）

## 一、报告必须 md + html + R2 三步走，不能停在 md

用户纠正："报告你要更新r2的md以及html，为什么你漏了"。

增量修改一份报告后，交付动作不能只写 .md 就停。完整流程：
1. 写/改 `reports/xxx.md`（含 charset=utf-8 防乱码）
2. 生成同名的 `reports/xxx.html`（自适应深色UI，`fetch('xxx.md')` + marked.js 渲染，便于手机查看）
3. 上传两者到 R2：
```python
from r2_uploader import R2Uploader
u = R2Uploader()
u.upload_file('fund_system_data/reports/xxx.md', 'fund-system/reports/xxx.md', 'text/markdown; charset=utf-8')
u.upload_file('fund_system_data/reports/xxx.html', 'fund-system/reports/xxx.html', 'text/html; charset=utf-8')
```
4. 报告末尾标注数据来源（"均实时拉取无虚构"）与模型。

## 二、交付前必须全量事实核查（不能只做增量修改就交付）

用户要求："因为你是增量修改的这份报告，我希望你再对这份报告做一次全量事实核查"。

增量修改容易在旧段落留下与新增数据矛盾的表述（本会话实测：第四节说"应纳入候选"与第三节"无独立ETF"、第五节"不新增标的"矛盾）。

**核查流程：**
1. 重拉所有原始数据（基金净值用 AKShare `fund_open_fund_info_em` 重算；微博用 API 重跑提取），逐项与报告数字比对，误差仅允许四舍五入。
2. 检查逻辑一致性：章节间结论不能互相矛盾（如"纳入候选" vs "无独立标的"）。
3. 标注口径：微博"公司提及"按"微博条数"还是"词出现次数"必须写清，避免与旧版"次/条"混用。
4. 修正后重新上传 R2（md+html）。

本会话核查结果：17支基金净值零误差；微博框架词一致；仅"长鑫8次→7条"、"中石油4次→2条"口径修正 + 1处章节矛盾修正。

## 三、模型纪律

用户明确要求：分析必须用 `tencent/hy3:free`，且"不要切换模型做分析"。若某步输出异常（如乱码/无意义片段），先排查数据/脚本问题，不要默认切换 fallback 模型。全程不切模型。
