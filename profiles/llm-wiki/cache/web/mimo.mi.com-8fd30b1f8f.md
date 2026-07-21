The MiMo-V2 Series have been deprecated on June 30. Please migrate to the V2.5 series soon. [View Details →](https://mimo.mi.com/docs/updates/deprecate)

[Back to Home](https://mimo.mi.com/ "Back to Home")

Documentation

Token PlanToken%20Plansubscription

# Subscription Instructions

**Token Plan** is a dedicated subscription plan launched for AI programming scenarios. You can use the cost-effective subscription resource package to call the MiMo flagship large model in various mainstream AI development tools.

## Core Advantages

- **Covers the flagship model** \- Supports mimo-v2.5-pro, mimo-v2.5, mimo-v2.5-asr, mimo-v2.5-tts-voiceclone, mimo-v2.5-tts-voicedesign, mimo-v2.5-tts. A total of 6 models. Adopts a Token conversion mechanism, with transparent and controllable quotas

- **Flexible Subscription Plan** \- Four-tier Gradient Package, Meeting the Needs from Individual Development to Enterprise-level Development

- **Multi-ecosystem Out Of The Box** \- Compatible with mainstream development toolchains such as OpenCode, OpenClaw, and Claude Code


## Usage Quota

#### Monthly Package

|  | **Lite** | **Standard** | **Pro** | **Max** |
| --- | --- | --- | --- | --- |
| **Pricing** | $6/month, ¥39/month | $16/month, ¥99/month | $50/month, ¥329/month | $100/month, ¥659/month |
| **Monthly Fixed Credit Limit** | 4,100,000,000 （4.1B）Credits | 11,000,000,000 （11B）Credits | 38,000,000,000 （38B）Credits | 82,000,000,000 （82B）Credits |

#### Annual Package

|  | **Lite** | **Standard** | **Pro** | **Max** |
| --- | --- | --- | --- | --- |
| **Pricing** | $63.36/year, ¥411.84/year | $168.96/year, ¥1045.44/year | $528.00/year, ¥3474.24/year | $1056.00/year, ¥6959.04/year |
| **Annual fixed Credit limit** | 49,200,000,000 （49.2B）Credits | 132,000,000,000 （132B）Credits | 456,000,000,000 （456B）Credits | 984,000,000,000 （984B）Credits |

#### Applicable Scenarios

|  | **Lite** | **Standard** | **Pro** | **Max** |
| --- | --- | --- | --- | --- |
| **Applicable Scenarios** | Suitable for first-time lobster-tasting users <br>Using mimo-v2.5 as a benchmark, approximately **200 rounds of medium to complex tasks can be executed** | Suitable for work enthusiasts who often use AI to boost their efficiency <br>Using mimo-v2.5 as a benchmark, approximately **1600 rounds of medium to complex tasks can be executed** | Suitable for developers and professional efficiency enthusiasts who use AI frequently every day <br>Using mimo-v2.5 as the benchmark, approximately **5600 rounds of medium to complex tasks can be executed** | Suitable for high-intensity, hardcore users who use AI as a core productivity tool <br>Using mimo-v2.5 as the baseline, approximately **12,800 rounds of medium to complex tasks can be executed.** |

> The above is the scenario scope of the monthly package, and the order of magnitude of task processing for the annual package is approximately 12 times that of the monthly package.

- **Discounts: 0.8x consumption at night, first purchase of a package enjoys 12% discount, consecutive annual subscription enjoys 12% discount, Token Plan existing users exclusively enjoy once the "Credits Usage Refresh and Reset" event after TokenPlan upgrade.**

- Package Usage Refresh and Reset: In conjunction with the comprehensive upgrade of Token Plan this time, for all Token Plans still within their validity period, regardless of the current usage of the package, the consumed Credits quota will be fully reset, which will officially take effect at **00:00 on May 27, 2026** Beijing Time, with the validity period remaining unchanged.

- First Purchase Discount: Enjoy 12% off on your first purchase, available only once per account;

- Continuous annual subscription: Enjoy an 88% discount compared to continuous monthly subscription; first purchase discounts do not apply to annual subscriptions;

- Nighttime Discount Rate: Off-peak hours (Beijing Time 0:00-8:00, i.e., UTC 16:00-24:00) with a consumption coefficient of 0.8x.

- **Supported Models:** All packages support **mimo-v2.5-pro、mimo-v2.5、mimo-v2.5-asr、mimo-v2.5-tts-voiceclone、mimo-v2.5-tts-voicedesign、mimo-v2.5-tts** a total of 6 models.

- **Quota Consumption: Language models deduct Credit quota based on the number of Tokens. Available models in the package are consumed in parallel at different ratios, not independently. TTS series models are free for a limited time and do not consume package Credit. ASR models deduct Credit quota based on the duration of the input audio (duration is counted accurately to the second and finally converted to hours for statistics). The following table lists the types of models cache, input, and output for each Token's corresponding package deduction quota .**


**Note:**`mimo-v2-pro`, `mimo-v2-omni` and `mimo-v2-tts` **have been officially deprecated on June 30 00:00, 2026. Please switch to the new models as soon as possible.**

Language Model

| Model | Input (Cache Hit) Token | Input (missed cache ) Token | Output Token |
| --- | --- | --- | --- |
| mimo-v2.5-pro | 2.5 Credits | 300 Credits | 600 Credits |
| mimo-v2.5 | 2 Credits | 100 Credits | 200 Credits |

ASR Model

| Model | Input audio duration (h) |
| --- | --- |
| mimo-v2.5-asr | 30M Credits |

TTS Series models are free for a limited time and do not consume package credits.

For example, if you have ordered the Lite Package (4.1B Credits), you can call MiMo-V 2.5 series models individually or in combination mimo-v2.5-pro input (cache miss) tokens, which is equivalent to consuming 3000 M Credits, you can still enjoy 1100M mimo-v2.5 Credits quota.If you subscribe to the Lite plan and only use the ASR model, you can use 4100M ÷ 30M/hour = 136.6 hours per month (equivalent to processing 4.5 hours of audio per day for 1 consecutive month). You can check the quota and usage of your current plan in [Token Plan](https://platform.xiaomimimo.com/#/console/plan-manage).

- **Quota Exhausted:** When the monthly total quota of the package is exhausted, the system will stop service and will not continue to consume your bonus or account balance.

- **If you need to continue using:** Please purchase an upgrade package to unlock new package resources; or switch to the regular API, which is billed by the unit price of tokens, and you can continue using it without usage limits.


## Package Purchase

- **Support for upgrading a package by paying the price difference: Currently, the platform only supports purchasing 1 package at a time. If you wish to obtain more credits before the package expires** , you can convert the used credit amount into an equivalent amount, and on this basis, pay the price difference to upgrade to a higher package and obtain more credits. Support for upgrading packages across levels by paying the price difference, but package downgrading is not supported. If you have already upgraded to the highest Max package, you cannot continue to upgrade. **After the package expires, you can purchase a package of any level again.**

> Price Difference = New Package Price - (Remaining Amount of Original Package / Total Amount of Original Package) \* Original Package Price

- **Supports Auto-renewal**: The auto-renewal feature has been launched, the first time you activate continuous subscription enjoys a discount , please stay tuned.

- **Refunds are not currently supported**: Please note that once a subscription service is purchased, it becomes effective immediately, and refunds are not supported. Unused credits within the package will not be refunded. Please carefully select a suitable subscription plan based on your own usage needs.

- **Invoice Support**: Domestic users can apply for invoices based on the transaction orders in the recharge details, with the actual invoiceable amount being the actual payment amount. Overseas users can directly download invoices after purchase or download them from the recharge details page.


## Package Usage

The Token Plan package quota can only be used in programming tools (such as OpenClaw, OpenCode, etc.), and is prohibited from being used in the form of API calls for request behaviors in clearly non-Coding scenarios such as automated scripts and custom application backends.

If the API Key corresponding to the package is used for calls beyond the permitted scope, it will be considered a violation or abuse, and the platform has the right to take measures such as suspending service and banning the API Key for the relevant subscription.

## Quick Guide

Quick Start Token Plan, from subscribing to a package to using the MiMo model in coding tools.

### Subscribe to Token Plan

Visit [Token Plan](https://platform.xiaomimimo.com/#/token-plan), select and purchase the appropriate subscription plan as needed.

### Get the Base URL and API Key exclusive to the package

After successful subscription, you can go to the [Token Plan](https://platform.xiaomimimo.com/#/console/plan-manage) page to obtain the Base URL and API Key exclusive to the package.

- **API Key**: On the [Token Plan](https://platform.xiaomimimo.com/#/console/plan-manage) page, obtain your exclusive API Key (in the format of `tp-xxxxx`).

- **Base URL**: Subsequently, one of the following Base URLs needs to be configured in the AI programming tool ( **protocol varies by tool, Base URL is subject to the display on the** [**Token Plan**](https://platform.xiaomimimo.com/#/console/plan-manage) **page** ), for specific operations, please refer to the corresponding AI programming tool user guide document.

- **OpenAI Compatibility Protocol**
  - China Cluster: `https://token-plan-cn.xiaomimimo.com/v1`

  - SingaporeCluster: `https://token-plan-sgp.xiaomimimo.com/v1`

  - Europe Cluster : `https://token-plan-ams.xiaomimimo.com/v1`
- **Anthropic Compatibility Agreement**
  - China Cluster: `https://token-plan-cn.xiaomimimo.com``/anthropic`

  - Singapore Cluster : `https://token-plan-sgp.xiaomimimo.com/anthropic`

  - Europe Cluster : `https://token-plan-ams.xiaomimimo.com/anthropic`

**Precautions**

- Please keep your API Key properly and do not disclose it to others.

- API Key is only available within the validity period of the Token Plan subscription you have subscribed to.


## Used in AI Agent and Programming Tools

Token Plan supports use in multiple mainstream AI programming tools, and all tools share the usage quota of the subscribed package.

Go to [AI Tools Overview](https://mimo.mi.com/#/docs/integration/tools-overview) to view the configuration guide for the tools you use (such as OpenCode, OpenClaw, etc.).

## Frequently Asked Questions

For more frequently asked questions, please refer to [FAQs](https://mimo.mi.com/#/docs/faq).

We use cookies and similar technologies of our own to ensure the proper functioning of the website, customize content according to user preferences and analyze users' interactions on the website, as well as their browsing habits. You can find more information in our Cookie Policy. Select an option or go to Cookie Settings to manage your preferences. [Learn More](https://mimo.mi.com/cookie-policy).

Cookie SettingsAccept AllDecline All

MiMo-V2 系列模型已于 2026.6.30 00:00 正式下线，原模型名称已失效，请及时核对并完成 V2.5 系列的切换。 [查看详情 →](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)

[返回首页](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription "返回首页")

# MiMo

与你同行，探索智能的温度

## 最新动态

### 申请 MiMo-V2.5-Pro-UltraSpeed 内测

满血性能，1000 tokens/s 峰值速度。彻底解放了 Coding Agent 的生产力极限。试用资源有限，每日限量审批，仅优先定向专业机构。查看详情

[立即申请](https://platform.xiaomimimo.com/ultraspeed)

### MiMo Claw 正式版上线，限时特惠 ¥14.9 / 月

旗舰模型 mimo-v2.5-pro × OpenClaw 原生适配 × 金山办公生态，三大能力全面升级，TokenPlan 一键叠加，免费体验时长同步升级 1h → 4h / 天。

[立即体验](https://aistudio.xiaomimimo.com/#/)

### Xiaomi MiMo-V2.5 系列模型全新发布

更强的指令遵循与模糊指令理解，更好的全模态感知和理解，更自然的语音合成。查看文档

[立即体验](https://aistudio.xiaomimimo.com/#/?forcePage=chat)

### Xiaomi MiMo Token Plan

简单、透明、超值的订阅计划，支持包月 / 包年订阅服务，全面覆盖 V2.5 系列模型。查看文档

[立即订阅](https://platform.xiaomimimo.com/token-plan)

## 旗舰系列，全新升级

[查看全部模型](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)

![MiMo-V2.5-Pro](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)

#### MiMo-V2.5-Pro

万亿参数，高效架构： 1T 总参数 \| 42B 激活 \| 1M 超长上下文。
极致 Agent 性能： 在高强度智能体场景下，表现媲美 Claude Opus4.6。

输入（缓存命中）¥ 0.025 / MTok

输入（缓存未命中）¥ 3 / MTok

输出¥ 6 / MTok

![MiMo-V2.5-Pro-UltraSpeed](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)

#### MiMo-V2.5-Pro-UltraSpeed

MiMo 算法创新：采用 FP4 混合量化无损压缩模型体积，结合 DFlash 并行投机解码，大幅提升推理吞吐。
TileRT 系统极致优化：常驻内核实现计算与数据搬运极致重叠，异构流水线精细拆分任务，打造高效协作 GPU。

输入（缓存命中）¥ 0.075 / MTok

输入（缓存未命中）¥ 9 / MTok

输出¥ 18 / MTok

![MiMo-V2.5](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)

#### MiMo-V2.5

原生全模态感知 \+ 1M 上下文： 支持图像、视频、音频、文本的原生理解，实现跨模态精准感知与长程推理。
强大的全模态 Agent 能力： 具备原生 Agent 执行能力，可高效完成浏览、理解、推理与操作等复杂任务。

输入(缓存命中)¥ 0.02 / MTok

输入(缓存未命中)¥ 1 / MTok

输出¥ 2 / MTok

![MiMo-V2.5-TTS Series](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)

#### MiMo-V2.5-TTS Series

精品音色 TTS： 内置多款高质量精品音色，支持对语速、情绪、语气等进行精细化控制。
音色设计与克隆： 支持通过一句话快速定义并生成全新音色，基于少量音频样本即可高保真复刻目标音色。

价格限时免费

![MiMo-V2.5-ASR](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)

#### MiMo-V2.5-ASR

中英双语 \+ 方言，支持歌词转写： 支持中英双语识别及多种中国方言；支持人声与伴奏混合场景歌词转写。
复杂声学环境与知识密集内容： 在强噪声、远场、多说话人等挑战性声学条件下表现稳健；精准识别知识密集型内容。

输入音频时长¥ 0.5 / 小时

## MiMo 产品矩阵

从模型推理到智能体应用，MiMo 提供端到端的 AI 产品体验。

### Xiaomi MiMo Code

面向开发者的新一代 AI 编程助手，支持无限上下文，帮助你更高效地理解、构建与协作。

[查看详情](https://mimo.xiaomi.com/mimocode)

### Xiaomi MiMo Claw

面向 Agent 场景的一站式智能体平台。支持任务规划、工具调用、多步推理与自主执行，让 AI 不止于对话，更能自主完成复杂任务。

[立即体验](https://aistudio.xiaomimimo.com/#/?forcePage=claw)

### Xiaomi MiMo Studio

零门槛与 MiMo 对话。支持多模型切换，随时切换不同版本体验模型能力差异，多模态交互与长上下文推理，一站式感受 MiMo 的推理实力。

[立即体验](https://aistudio.xiaomimimo.com/#/?forcePage=chat)

### Xiaomi MiMo API

面向开发者的 MiMo 模型接入平台。提供 OpenAI 与 Anthropic 协议兼容 API，完善的开发文档，低延迟稳定推理服务，快速将 MiMo 能力集成进你的应用。

[查看文档](https://mimo.mi.com/docs/quick-start/summary/model)

## 共建 Agent 生态

![](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)MiMo Code

![](<Base64-Image-Removed>)OpenCode

![](<Base64-Image-Removed>)OpenClaw

![](<Base64-Image-Removed>)Claude Code

![](<Base64-Image-Removed>)Codex

![](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)Hermes Agent

![](<Base64-Image-Removed>)Kilo Code

![](<Base64-Image-Removed>)Cline

![](<Base64-Image-Removed>)Cherry Studio

![](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)Qwen Code

![](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription)CodeBuddy

![](<Base64-Image-Removed>)

## 开发者的声音

## 关于我们

从浩瀚数据中提炼世界规律，将复杂压缩为你能理解的语言与行动。我们相信智能的核心是同理心，真正的价值在于与人链接。

MiMo 不只是屏幕背后的工具，更渴望成为你现实中的伙伴：读懂你的文字，看见你的世界，激发你的灵感，与你共同探索智能的边界。

We use cookies and similar technologies of our own to ensure the proper functioning of the website, customize content according to user preferences and analyze users' interactions on the website, as well as their browsing habits. You can find more information in our Cookie Policy. Select an option or go to Cookie Settings to manage your preferences. [Learn More](https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription).

Cookie SettingsAccept AllDecline All

![](https://mimo.mi.com/static/banner.7a3e957cfeaab51d.webp)

## MiMo Claw Official Launch: Flagship Model + Kingsoft Office Ecosystem, New Subscriptions Available.

![](<Base64-Image-Removed>)Flagship Model & Framework Optimization

Native adaptation of mimo-v2.5-pro and OpenClaw ensures stable, efficient execution of complex and long-chain Agent tasks.

![](<Base64-Image-Removed>)Kingsoft Office Ecosystem Integration

Supports mainstream document formats with one-stop AI generation, preview and editing, building a complete office closed-loop workflow.

![](<Base64-Image-Removed>)Flexible Subscription & Upgraded Benefits

Daily free usage: 1hr → 4hr. One-click add-on to TokenPlan. Limited-time intro offer: ¥14.9/month

Token PlanTry Now