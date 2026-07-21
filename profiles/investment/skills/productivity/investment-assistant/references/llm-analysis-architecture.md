# LLM分析层架构 — Hybrid 设计模式

> 基于2026-07-20会议实现。将纯脚本推送升级为"数据采集+LLM深度分析"双层架构。

## 架构总览

```
采集层 (no_agent, 纯脚本)         分析层 (no_agent, 脚本调DeepSeek API)
fund_tools.py                     llm_analysis.py
  ↓ 写入 /tmp/fund_data/            ↓ 读取结构化数据
格式化推送层 (不变)                   ↓ 5套系统提示词
send_*.py                          ↓ DeepSeek V4 Flash API
  ↓ Markdown                       ↓ 返回分析文本
QQ Bot API (推送)
```

**核心原则：** 采集层保底（数据必达），分析层增强（有则更好）。LLM API失败时降级为纯数据推送，不丢数据。

## 文件结构

```
/opt/data/scripts/
├── llm_analysis.py        # 核心模块：5套system prompt + API调用 + 数据构建
├── llm_validate.py        # 质量验证框架：自我评分 + 多轮验证 + R2上传
└── run_closing.py (已改)   # 示范：采集→格式化→LLM分析→合并推送
```

## llm_analysis.py 模块

### 公开接口

| 函数 | 用途 | max_tokens | 
|:-----|:------|:----------:|
| `generate_morning_analysis()` | 早报 · 隔夜传导·今日关注 | 1000 |
| `generate_noon_analysis()` | 午报 · 上午走势·午后策略 | 1000 |
| `generate_closing_analysis()` | 收盘 · 全天复盘·明日关注 | 1000 |
| `generate_decision_analysis()` | 14:30决策 · 赛道评估·操作参考 | 1200 |
| `generate_weekly_analysis()` | 周度复盘 · 趋势·归因·下周策略 | 1200 |

所有函数：接受 `use_cache=True`（当日复用），返回 `Optional[str]`

### 调用方式（从no_agent脚本）

```python
import os
# 1. 加载API key（从.env文件）
env_path = '/opt/data/profiles/investment/.env'
if os.path.exists(env_path):
    for line in open(env_path):
        if line.startswith('DEEPSEEK_API_KEY='):
            os.environ['DEEPSEEK_API_KEY'] = line.split('=', 1)[1].strip()

# 2. 调用分析
sys.path.insert(0, '/opt/data/scripts')
from llm_analysis import generate_closing_analysis, format_analysis_block
analysis = generate_closing_analysis(use_cache=False)  # 不回读当日缓存
if analysis:
    block = format_analysis_block("收盘 AI 深度解读", analysis)
    # 追加到推送内容中
```

### DeepSeek API 调用要点

- **模型**: `deepseek-v4-flash`（已配置think模式，需处理reasoning_content）
- **Base URL**: `https://api.deepseek.com`
- **认证**: 从 `.env` 文件读取 `DEEPSEEK_API_KEY`（注意注入到 `os.environ`）
- **超时**: 90秒（分析输入~4K tokens，输出~1K tokens）
- **降级**: API失败返回 `None`，调用方自行处理（不阻断数据推送）
- **缓存**: 每日每报告类型只调一次API，后续复用缓存

## 5套系统提示词设计要点

每套prompt针对DeepSeek的金融分析优势设计：

### 收盘复盘
- 识别"高低切换"等风格轮动主题
- 各赛道对持仓的**实际影响**（指名道姓具体基金）
- 关键信号：放量/缩量/突破/破位/北向异动
- 明日关注：3个具体观察维度

### 早报
- 外盘→A股传导路径分析
- 今日开盘关键位置（技术面+消息面）
- 风险提示在前（先说不利的，再说机会）

### 午报
- 上午走势定性（延续/反转/震荡）
- 板块轮动识别（对比昨日）
- 午后策略参考（方向性，非具体买卖）

### 14:30决策
- **T+1适配**：考虑了次日延续性，不只看当日
- **建仓基金保护**：003096/013403在建仓期只考虑加仓，不考虑减仓
- 回撤分层：连续下跌后缩量企稳→可观察，放量破位→观望
- 每个赛道独立评估，不泛化

### 周度复盘
- **不用指数代理估算净值**（用户明确纠正过）
- KOL观点聚合+历史准确率加权
- 组合配比偏离度分析
- 下周策略方向（防御/进攻/再平衡）

## 质量验证框架 (llm_validate.py)

### 评估方法

让DeepSeek对自身分析做5维度评分（JSON格式）：

| 维度 | 缩写 | 评分标准 |
|:-----|:----:|:---------|
| 数据准确性 | A  | 分析是否严格基于给出的数据 |
| 逻辑一致性 | B  | 推理是否自洽，有无臆测 |
| 实用性 | C  | 对基金投资者的参考价值 |
| 简洁性 | D  | 是否废话少、重点突出 |
| 风险意识 | E  | 是否充分强调风险 |

### 输出格式

评估prompt用JSON输出（避免DeepSeek thinking模式干扰格式解析）：
```json
{"data_accuracy": 8, "logic_consistency": 9, "practicality": 8,
 "conciseness": 9, "risk_awareness": 9, "total_score": 8.6,
 "comment": "分析全面", "improvement": "无"}
```

### 验证结果存储

```
/opt/data/fund_system_data/llm_validation/
├── validation_round{N}_{YYYY-MM-DD}.json   # 原始评分数据
├── validation_round{N}_{YYYY-MM-DD}.md     # 可读报告
└── validation_round{N}_{YYYY-MM-DD}.html   # 自适应前端预览
```

上传R2路径：`fund-system/llm-validation/`

## 已知pitfalls

1. **DEEPSEEK_API_KEY必须在os.environ中** — 从.env文件读取后需`os.environ['DEEPSEEK_API_KEY']=...`注入，单纯定义变量不够（requests库从env读取）
2. **thinking模式导致content为空** — DeepSeek V4 Flash默认带thinking，有时`content`为空（`finish_reason: length`）。解决方案：增大max_tokens（1000+），使用简单的prompt结构
3. **JSON格式评估易失败** — DeepSeek的thinking模式可能输出JSON前有文字前缀。需用正则 `r'```(?:json)?\s*(\{.*?\})\s*```'` 做模糊提取
4. **缓存文件不过期** — 当日缓存不会自动清理。测试时用 `use_cache=False` 覆盖
5. **调用的脚本必须在no_agent上下文** — cron job是`no_agent: true`，脚本自身负责API Key加载（不能依赖Hermes agent配置）
6. **cost估算为粗略值** — 实际token消耗取决于输入数据量和输出长度。按输入4K+输出1K估算，单次分析约 ¥0.01-0.02
