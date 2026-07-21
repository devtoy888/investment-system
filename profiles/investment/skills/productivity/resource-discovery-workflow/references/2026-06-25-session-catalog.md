# 资源目录 — 2026-06-25 Session

## AIWriteX
- **URL**: https://github.com/iniwap/AIWriteX
- **License**: Apache 2.0 (with additional file-level restrictions in hotnews.py)
- **Stars**: growing, active
- **Stack**: Python 3.10+, CrewAI 0.102+, AIForge, FastAPI, PyWebView
- **核心功能**: 公众号/小红书/百家号/头条 全自动创作
  - 热搜聚合 (zhiweidata + tophub.today 爬虫)
  - CrewAI 多Agent协作 (研究→写作→审校→设计)
  - 去AI味/反朱雀检测
  - 一键发布多个平台
  - 小说连载引擎 (三层记忆矩阵)
  - 手机控制 (QQ/钉钉/飞书/Telegram)
- **Oracle ARM可行性**: ⚠️ 需要改造
  - ❌ 桌面GUI (PyWebView/PyWinGUIBuilder) — 无头服务器不可用
  - ✅ FastAPI Web后端 — 可跑
  - ✅ CrewAI 写作引擎 — 无平台依赖
  - ✅ 微信发布 — 可用 (需 appid/appsecret)
  - ⚠️ 无Dockerfile，需自写
  - ⚠️ pywin32 是条件依赖 (仅Windows)
- **推荐**: 🟡 推荐先在自己的MacBook试，确认效果再决定是否部署到ARM服务器

## a-stock-data
- **URL**: https://github.com/simonlin1212/a-stock-data
- **License**: (not explicitly checked but likely open)
- **Stack**: Python, pip install mootdx requests pandas stockstats
- **核心功能**: A股全栈数据工具包
  - 28个数据端点，13个数据源
  - 行情(mootdx/腾讯/百度K线)、研报(东方财富/同花顺)、
    资金流、筹码、公告、新闻
  - 数据源优先级: mootdx/腾讯优先(不会被封IP)
  - 原为Claude Code skill格式(SKILL.md)
- **Oracle ARM可行性**: ✅ 纯Python，无平台依赖
- **推荐**: 🟡 适合整合到基金日报系统

## baoyu-skills
- **URL**: https://github.com/JimLiu/baoyu-skills (⭐22.5k)
- **核心技能匹配**:
  - `baoyu-xhs-images` — 小红书卡片图 (12风格×多种布局)
  - `baoyu-cover-image` — 5D封面图 (类型×色调×渲染×文字×情绪)
  - `baoyu-infographic` — 信息图 (21布局×17风格) — **已在Hermes可用**
  - `baoyu-article-illustrator` — 文章智能配图
  - `baoyu-slide-deck` — 幻灯片
  - `baoyu-comic` — 知识漫画
  - `baoyu-diagram` — SVG图表
- **格式**: Claude Code/Codex skill格式，非Hermes原生
  - 但 `baoyu-infographic` 已被适配到Hermes ✅
- **推荐**: 🟡 内容配图场景优先用已有的 `baoyu-infographic`，其他按需适配

## guizang-ppt-skill
- **URL**: https://github.com/op7418/guizang-ppt-skill
- **功能**: HTML幻灯片生成 (杂志风+瑞士风)
  - 支持公众号21:9头图、小红书3:4封面生成
  - WebGL/低功耗演示运行
- **格式**: Claude Code/Codex skill
- **推荐**: ⚪ 适合做PPT/封面时参考

## Illustrated-Agent-Skills
- **URL**: https://github.com/JimLiu/Illustrated-Agent-Skills
- **内容**: 《图解Skill》配套repo
  - 写作workflow模板 (内容分析/大纲/写作/润色/配图)
  - 不是可直接部署的工具
- **推荐**: ⚪ 写作技巧和prompt设计可借鉴

## 当前推荐的实施优先级
1. **AIWriteX** → 公众号内容管线(session中讨论)
2. **a-stock-data** → 基金仪表盘数据源(session中讨论)
3. **baoyu-skills配图** → 内容创作配图(session中讨论)
4. guizang-ppt-skill → 按需
5. Illustrated-Agent-Skills → 参考学习
