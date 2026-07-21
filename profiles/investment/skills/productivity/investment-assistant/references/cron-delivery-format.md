# Cron Delivery 格式 — 纯文本摘要 + R2链接

> 来源: 2026-07-21 用户要求盘中报告同时包含文本概述和R2链接，不要只有链接。

## 规则

no_agent cron脚本的stdout是推送到QQ的消息体。消息体应包含：

1. **关键数据摘要**（纯文本+emoji，不markdown格式）
2. **AI分析一句话**
3. **R2完整报告链接**

示例（午报）：
```
📈 盘中直击 · 2026-07-21 周二 12:48

📊 大盘: 上证3819.66🔴0.62% | 科创1837.94🔴6.94% | 创业板3622.27🔴5.20% | 沪深4679.41🔴1.76%
🔥 领涨: 半导体+8.28% 通信+6.19% 新能源+3.36%
🟢 领跌: 券商-0.81% 消费-1.01%
🌊 北向资金: 沪+16.16亿 深+37.70亿 合计+53.86亿
💰 半日成交20003亿
📊 持仓: 科技/AI🔴-3.31% | 资源/周期🟢0% | 黄金🟢0% | 新能源🟢0% | 医药🟢0%

🤖 好的，老板。盘中数据已收到，我们先抓住盘中的关键信号进行梳理。

📄 完整报告: https://hermes-main-media.devtoy.xyz/fund-system/reports/noon_2026-07-21.md
🌐 HTML预览: https://hermes-main-media.devtoy.xyz/fund-system/reports/noon_2026-07-21.html
```

## 格式要求

- ❌ 禁用 `##` / `**bold**` / `#tag` / `_italic_`（QQ Bot渲染大号字）
- ✅ 纯文本 + emoji ️
- ✅ 表格用"|"符号（QQ支持简单表格）
- ✅ 关键数据先列，AI分析在后，链接收尾
- ✅ 内容适当截断（不宜超过4000字符）

## 实现模式（参考 run_noon.py）

1. 采集数据 → 读 `/tmp/fund_data/_noon_*.txt`
2. 格式化摘要 → 构建 lines_out 列表
3. push_report 上传R2 → 临时禁用其stdout避免重复（`sys.stdout = io.StringIO()`）
4. `print("\n".join(lines_out))` → 供no_agent cron deliver

```python
# 抑制push_report的旧摘要输出
old_stdout = sys.stdout
sys.stdout = io.StringIO()
try:
    md_link, html_link = push_report("noon", title, tables, analysis)
finally:
    sys.stdout = old_stdout

# 打印自己的摘要
print("\n".join(lines_out))
```
