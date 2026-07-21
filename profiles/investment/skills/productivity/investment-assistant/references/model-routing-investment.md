# Investment Profile 模型路由配置

> 投资系统的主模型路由策略：DeepSeek v4 Flash 主分析 + Xiaomi MiMo Token Plan 辅助降级

## 文件布局

Investment Profile 的配置与 Default Profile **完全不同**，切勿混淆：

| 文件 | 路径 | 说明 |
|:-----|:-----|:------|
| Investment config | `/opt/data/profiles/investment/config.yaml` | 投资模型的配置 |
| Investment .env | `/opt/data/profiles/investment/.env` | 投资模型的密钥 |
| Default config | `/opt/data/config.yaml` | **不是**投资模型的 |
| Default .env | `/opt/data/.env` | **不是**投资模型的 |

## 当前模型路由设计

### 主模型：DeepSeek v4 Flash（金融分析主力）

```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek
  base_url: https://api.deepseek.com
```

凭证从 `.env` 读取：
```
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### Fallback 链：MiMo → OpenRouter 免费

```yaml
fallback_providers:
  - provider: xiaomi           # MiMo Token Plan
    model: mimo-v2.5-pro
  - provider: xiaomi
    model: mimo-v2.5
  - provider: agnes
    model: agnes-2.0-flash
  - provider: openrouter
    model: cohere/north-mini-code:free
```

DeepSeek 挂了 → MiMo pro 降级 → MiMo 标准版 → Agnes → OpenRouter 免费兜底。

### 辅助任务：MiMo 替换 OpenRouter 免费模型

```yaml
auxiliary:
  compression:
    provider: xiaomi         # 比 openrouter 免费更稳定
    model: mimo-v2.5
  web_extract:
    provider: xiaomi
    model: mimo-v2.5
  title_generation:
    provider: xiaomi
    model: mimo-v2.5
  vision:
    provider: xiaomi         # MiMo 支持多模态
    model: mimo-v2.5
```

理由：OpenRouter 免费模型不稳定（超时/429频繁），MiMo 走订阅制固定费用、响应稳定。

### 子代理模型：DeepSeek v4 Flash（非pro）

```yaml
delegation:
  model: deepseek-v4-flash   # 用 flash 不是 pro，节约 ~90% 成本
  provider: deepseek
```

---

## Xiaomi MiMo Token Plan 配置

### 凭证类型

| 类型 | API Key 前缀 | Base URL | 计费 |
|:-----|:-------------|:---------|:-----|
| Token Plan | `tp-` | `https://token-plan-cn.xiaomimimo.com/v1` | 订阅制 |
| Pay-As-You-Go | `sk-` | `https://api.xiaomimimo.com/v1` | 按量计费 |

### Token Plan Lite 规格

| 维度 | 数值 |
|:-----|:-----|
| 月费 | $6/月（¥39/月） |
| Credits | 4.1B/月 |
| 支持模型 | mimo-v2.5, mimo-v2.5-pro, mimo-v2.5-asr, TTS系列 |
| 消耗比例 | v2.5 输入(Cache Miss) 100 Credits, 输出 200 Credits |
| 夜间折扣(0:00-8:00) | 0.8倍 |

### 注意事项

1. **V2 系列已弃用**（2026-06-30），只能用 V2.5 系列
2. Token Plan **限制**：官方条款写"只能用于编程工具（OpenClaw、OpenCode等）"，但 MiMo 官方提供了 Hermes Agent 集成教程，说明认可 Hermes 属于此范畴
3. Hermes 使用 `xiaomi` 作为 provider 名（不是 `mimo`）
4. `model.base_url: ''` 时，Hermes 自动使用 `api.xiaomimimo.com/v1`（PAYG 端点）。Token Plan 需要显式设置 base_url
5. MiMo V2.5 系列支持：文本、图像、视频、音频理解

### 相关密钥

```bash
# .env 配置
XIAOMI_API_KEY=tp-xxx                     # Token Plan 密钥
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

---

## Cron 脚本层路由（不受 config 控制）

所有 21 个 cron 任务均为 `no_agent: true`（纯脚本），直接调用 Python API **不走 Hermes 模型路由**。

| 管道 | 模型来源 | 方法 |
|:-----|:---------|:-----|
| 早/午/收/周度报告 | DeepSeek v4 Flash | `llm_analysis.py` 硬编码调用 DeepSeek API |
| 执行决策（09:35/14:30） | DeepSeek v4 Flash | `execute_today_plan.py` 包装器 |
| 进化引擎/验证 | DeepSeek v4 Flash | `run_evolution_verify.py` |
| 数据采集脚本 | 无 LLM 调用 | 纯数据操作 |

---

## 最佳实践要点

1. **不要混淆 default 和 investment profile 配置** — 是两个独立文件
2. **DeepSeek 做主模型** — 金融分析更擅长，响应质量高
3. **MiMo 做辅助+降级** — 利用 Token Plan 订阅费分摊，比按量调用 OpenRouter 更经济稳定
4. **Delegation 用 flash 而非 pro** — 子代理任务不需要 pro 级别，节约约 90%成本
5. **编辑 config 后必须重启 gateway** — 否则不生效
6. **MiMo 的 base_url 必须显式设置** — 空字符串会走默认 PAYG 端点而非 Token Plan
7. **V2 系列已死** — 务必用 `mimo-v2.5` 或 `mimo-v2.5-pro`
