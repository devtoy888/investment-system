# Fund Dashboard · 开发规范手册

> 与本项目所有开发任务前，必须先加载本手册中列出的所有技能。
> 开发模式：全自动化——你给我指令，我评估→规划→开发→测试→审查→部署。

---

## 1. 必须加载的技能

每次开发任务前，加载以下技能以保持开发方式一致性：

| 技能 | 作用 | 强制阶段 |
|------|------|---------|
| `test-driven-development` | TDD红绿重构循环，测试先行 | 开发阶段 |
| `requesting-code-review` | 独立审查+安全扫描+自动修复 | 提交前 |
| `plan` | 规划模式：任务拆解+完整代码 | 开发前 |
| `cloudflare-r2` | R2上传+部署 | 部署阶段 |
| `fund-evolution-engine` | 投资系统知识库 | 全阶段参考 |
| `fund-decision-verify` | 决策系统知识库 | 全阶段参考 |
| `investment-assistant` | 系统全貌知识库 | 全阶段参考 |

---

## 2. 开发流程（每轮迭代）

### Step 1: 任务接收
你发指令 → 我评估可行性 + 关联方案文档

### Step 2: 规划（Plan模式）
```markdown
加载 plan skill
- 拆解为2-5分钟的子任务
- 每个任务包含：文件路径、完整代码、测试命令
- 写入 .hermes/plans/ 存档
```

### Step 3: TDD开发（每个子任务）
```markdown
加载 test-driven-development skill
对每个子任务:
  1. RED: 写失败的测试
  2. 验证测试确实失败（必须看到失败输出）
  3. GREEN: 写最少代码通过测试
  4. 验证测试通过
  5. REFACTOR: 重构（保持测试通过）
```

### Step 4: 代码审查
```markdown
加载 requesting-code-review skill
  1. git diff 获取变更
  2. 静态安全扫描
  3. 基线测试对比（无回归）
  4. 独立审查者subagent审查
  5. 自动修复（最多2轮）
  6. 通过后 commit [verified]
```

### Step 5: 部署
```markdown
加载 cloudflare-r2 skill
  1. npm run build（本地测试构建通过）
  2. git push → Cloudflare Pages自动部署
  3. curl验证线上URL 200
```

---

## 3. 测试策略

### 3.1 测试层级

| 层级 | 工具 | 覆盖范围 | 运行频率 |
|------|------|---------|---------|
| 单元测试 | Vitest | 每个函数/组件 | 每次commit |
| 组件测试 | Vitest + Testing Library | React组件渲染+交互 | 每次commit |
| **E2E测试** | Playwright | 完整页面加载+数据展示 | 每次部署前 |
| **UI快照测试** | Vitest + storyshots | 组件视觉一致性 | 每次commit |

### 3.2 测试文件结构

```
dashboard/src/
├── components/
│   ├── GlassCard.tsx
│   ├── GlassCard.test.tsx     ← 单元+组件测试
│   ├── PieChart.tsx
│   ├── PieChart.test.tsx
│   └── DateNav.tsx
│       └── DateNav.test.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── Dashboard.test.tsx     ← 页面级测试
│   └── ...
├── hooks/
│   ├── useDashboardData.ts
│   └── useDashboardData.test.ts
├── lib/
│   ├── api.ts
│   └── api.test.ts            ← API层测试（mock fetch）
└── e2e/                        ← Playwright E2E测试
    ├── dashboard.spec.ts
    └── portfolio.spec.ts
```

### 3.3 测试准则（不为了通过而写）

```
✅ 正确测试:
  - 测试行为，不测试实现
  - 每个测试测一个行为（测试名含"and"就拆分）
  - 使用真实数据，不mock（除非无法避免）
  - 测试边界条件：空数据、错误状态、加载状态

❌ 错误测试:
  - 测试通过只是因为mock正确
  - 测试覆盖了实现细节（改成函数内部重命名就挂了）
  - "为覆盖率而写"的测试
  - 没有验证失败路径的测试

覆盖率目标:
  组件: ≥80%
  utils/lib: ≥90%
  页面: ≥70%（通过组件测试覆盖）
  E2E: 每个主要用户流程至少1条
```

### 3.4 测试命令

```bash
# 单元+组件测试
npx vitest run          # 一次运行
npx vitest              # watch模式（开发时）

# 带覆盖率
npx vitest run --coverage

# E2E测试（需要先构建）
npm run build
npx playwright test

# 测试特定文件
npx vitest run src/components/GlassCard.test.tsx
```

---

## 4. UI/UX 规范（参考Vibe-Research）

### 4.1 设计原则

```markdown
- 暗色优先：深蓝(#0a0e1a) + 暖橙(#f59e0b) 品牌色
- 玻璃卡片：background: rgba(17,24,39,0.8) + border: 1px solid rgba(255,255,255,0.06)
- 涨跌色：涨=#22c55e(绿) 跌=#ef4444(红) 平=#6b7280(灰)
- Metric卡片：2列网格，大号数字+小字标签
- 表格：紧凑、右对齐数字、涨跌色标注
- 手机优先：320px~430px宽度完美展示
- 每个页面右下角💬问AI按钮
```

### 4.2 从Vibe-Research直接复用的组件模式

```tsx
// GlassCard — 所有卡片容器
// 来源: Vibe-Research GlassCard.tsx
<GlassCard className="p-3">
  <p className="text-xs text-muted-foreground">标签</p>
  <p className="mt-1 font-mono text-lg font-bold">数值</p>
</GlassCard>

// PageHeader — 页面标题
// 来源: Vibe-Research PageHeader.tsx
<PageHeader
  title="页面标题"
  subtitle="描述文字"
  actions={<button>操作按钮</button>}
/>

// 指数卡片网格
// 来源: Vibe-Research DailyReview.tsx
<div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
  {indices.map(i => (
    <GlassCard key={i.code}>
      <p>{i.name}</p>
      <p className={pctColor(i.change_pct)}>{i.price}</p>
      <p className={pctColor(i.change_pct)}>{i.change_pct > 0 ? '+' : ''}{i.change_pct}%</p>
    </GlassCard>
  ))}
</div>

// 涨跌色函数
// 来源: Vibe-Research DailyReview.tsx
const pctColor = (p: number) => 
  p > 0 ? 'text-green-400' : p < 0 ? 'text-red-400' : 'text-gray-400';
```

### 4.3 ECharts图表规范

```tsx
// 所有图表使用同一模式
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

function Chart({ data, style }: { data: any; style?: React.CSSProperties }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const chart = echarts.init(ref.current!);
    chart.setOption({
      // 暗色主题配色
      backgroundColor: 'transparent',
      textStyle: { color: '#9ca3af' },
      // ... 具体配置
    });
    return () => chart.dispose();
  }, [data]);
  return <div ref={ref} style={{ height: 300, ...style }} />;
}

// 统一配色
const CHART_COLORS = {
  primary: '#f59e0b',   // 暖橙 - 主色
  up: '#22c55e',        // 绿色 - 涨
  down: '#ef4444',      // 红色 - 跌
  grid: 'rgba(255,255,255,0.06)',  // 网格线
  text: '#9ca3af',      // 文字
};
```

---

## 5. 项目结构（最终版）

```
investment-system/
├── .hermes/
│   └── plans/           ← 开发计划存档
├── dashboard/            ← React + TypeScript 项目
│   ├── package.json     ← 依赖清单
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── _redirects       ← SPA路由 (/* /index.html 200)
│   ├── _worker.js       ← API层（D1查询+DeepSeek代理）
│   ├── wrangler.toml    ← Cloudflare Pages配置
│   ├── tailwind.config.ts
│   ├── playwright.config.ts  ← E2E测试配置
│   ├── src/
│   │   ├── main.tsx     ← React入口
│   │   ├── App.tsx      ← 路由配置
│   │   ├── index.css    ← Tailwind + 全局样式
│   │   ├── components/  ← 通用组件
│   │   ├── pages/       ← 8个页面
│   │   ├── hooks/       ← 数据层
│   │   ├── types/       ← TypeScript类型
│   │   └── lib/         ← 工具函数
│   └── e2e/             ← Playwright测试
└── schema.sql           ← D1表结构
```

---

## 6. 进度追踪

### 6.1 任务面板

使用 `todo` 工具追踪每轮迭代的任务列表：

```markdown
每次开发会话开始时:
  1. todo → 查看当前任务列表
  2. 完成一个任务 → todo 标记完成
  3. 遇到阻塞 → todo 标记in_progress + 记录原因
```

### 6.2 阶段看板

| 阶段 | 状态 | 任务 |
|------|------|------|
| 阶段一: 基础设施 | 🔴 未开始 | Git初始化 / D1创建 / schema.sql / sync_to_d1.py |
| 阶段二: core SPA | 🔴 未开始 | 项目脚手架 / GlassCard / 路由 / 总览页 |
| 阶段三: 持仓+板块 | 🔴 未开始 | Portfolio / Sectors / ECharts |
| 阶段四: 行情+资讯 | 🔴 未开始 | MarketOverview / Intel / KOL |
| 阶段五: 历史+操作 | 🔴 未开始 | History / Operations / Signals |
| 阶段六: 交互式LLM | 🔴 未开始 | POST /api/ask / 问AI组件 |
| 阶段七: 测试+打磨 | 🔴 未开始 | E2E / 弱网处理 / 手机适配 |
| 阶段八: 部署上线 | 🔴 未开始 | Git push / Pages / 域名 |

### 6.3 验收清单（每个阶段）

```
[ ] 所有组件有单元测试（TDD红绿验证）
[ ] 独立代码审查通过（无安全/逻辑问题）
[ ] E2E测试通过（页面加载+数据展示）
[ ] curl验证线上URL 200
[ ] 手机浏览器实测（320px宽度）
[ ] 无控制台错误
[ ] CDN缓存刷新验证
```

---

## 7. 自动化所需Token

### 7.1 Token清单

| Token | 用途 | 创建链接 |
|-------|------|---------|
| `GITHUB_TOKEN` | 创建仓库、push代码、管理分支 | https://github.com/settings/tokens/new → 勾选 `repo` |
| `CLOUDFLARE_API_TOKEN` | 创建Pages、管理D1、配置binding | https://dash.cloudflare.com/profile/api-tokens → 权限: Pages Edit + D1 Edit + Workers Scripts Edit |

### 7.2 写入位置

```bash
# ~/.hermes/profiles/investment/.env
GITHUB_TOKEN=***  
CLOUDFLARE_API_TOKEN=***
```

### 7.3 有Token后全自动的管线

```
你: "开始阶段一"
↓
我(服务器端):
  git init → 第一次commit → git push到GitHub
  npm create vite → 装依赖 → 第一次build

我(Cloudflare端 - API全自动):
  创建D1数据库 → 执行schema.sql建表
  创建Pages项目 → 配置构建命令(build:dist) → 绑定D1
  触发首次部署

我(验证):
  curl https://investment-system.pages.dev → 200 ✅
  D1查询 → 空表可查 ✅

我(报告):
  进度 → 线上URL → 下一步
```

---

## 8. UI/UX 设计工作流

### 8.1 Logo和Favicon

我不会设计精美图标，但可以生成**简洁可用的版本**：

```markdown
Logo: SVG文字标志 "FD"（Fund Dashboard缩写）
  配色: 深蓝底(#0a0e1a) + 暖橙字(#f59e0b)
  字体: 无衬线粗体
  用途: 浏览器tab图标、页面左上角

Favicon: 从SVG导出为.ico/.png
  尺寸: 32x32 / 192x192
```

**生成方式**：Python Pillow或直接写SVG → 上传R2 → 引用到index.html。

### 8.2 设计迭代流程

```
我: 生成页面 → git push → Pages自动部署 → 给你预览URL
你: 手机上打开 → 看效果 → 说哪里不对
我: 修改 → git push → Pages重新部署(~30秒)
你: 再次预览 → 确认或继续提修改
```

预期每个页面需要2-3轮迭代定型。

### 8.3 视觉参考源

| 来源 | 参考内容 | 使用方式 |
|------|---------|---------|
| Vibe-Research GlassCard.tsx | 暗色卡片样式 | 直接复用组件模式 |
| Vibe-Research DailyReview.tsx | 指数网格布局 | 直接复用布局模式 |
| Vibe-Research PageHeader.tsx | 页头+操作按钮 | 直接复用 |
| Vibe-Research Portfolio.tsx | 表格+表单逻辑 | 参考思路，数据改为基金 |
| Vibe-Research Intel.tsx | Tab切换+AI提炼 | 参考思路，数据改为KOL |
| Vibe-Research echarts用法 | package.json版本+初始化模式 | 直接复用 |
| Vibe-Research 涨跌色函数 | pctColor() | 直接复用 |

---

## 9. 部署管线

```mermaid
git push → GitHub
  → Cloudflare Pages检测到push
  → npm install
  → npm run build (tsc + vite build)
  → dist/ 部署到CDN
  → _worker.js 部署为API层
  → D1 binding生效
  → CDN全球分发 (~30秒)
```

**首次部署只需：**
```bash
# 在Cloudflare Pages控制台操作（一次性的）
1. 连接GitHub仓库
2. 框架预设: React
3. 构建命令: npm run build
4. 输出目录: dist/
5. 配置D1数据库绑定
6. 设置DEEPSEEK_API_KEY环境变量
```

**日常部署：**
```bash
git add -A && git commit -m "[verified] 功能描述"
git push
# 等待~30秒，Pages自动构建上线
```

---

## 10. 补充说明

### 10.1 错误处理规范

```tsx
// 所有数据加载使用三层次降级
async function loadData() {
  // 第一层: Worker API（最快）
  try { return await fetch('/api/data').then(r.json()); }
  catch {
    // 第二层: R2 JSON（一定读得到）
    try { return await fetch(CDN_URL + '/data.json').then(r.json()); }
    catch {
      // 第三层: localStorage缓存
      const cached = localStorage.getItem('cache');
      if (cached) return { ...JSON.parse(cached), stale: true };
      return { error: '无法加载', stale: true };
    }
  }
}

// 加载状态: 每个独立数据块有自己的loading/error
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

### 10.2 版本命名

```
v0.1.0 - 管线就绪（GitHub+Pages+D1）
v0.2.0 - SPA骨架+总览页（MVP）
v0.3.0 - 持仓+板块页面
v0.4.0 - 行情+资讯页面
v0.5.0 - 历史趋势+操作+信号
v0.6.0 - 交互式LLM
v0.7.0 - 测试+打磨+部署
v1.0.0 - 正式上线
```

### 10.3 沟通约定

- 你发指令：如"开发总览页"
- 我回复：评估→计划→开发→测试→审查→部署
- 每个步骤完成后更新进度
- 遇到阻塞立即反馈（不自行决策绕过问题）
