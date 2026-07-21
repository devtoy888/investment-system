import { PageHeader } from '../components/PageHeader';
import { GlassCard } from '../components/GlassCard';

export default function Dashboard() {
  const dateStr = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
  });

  return (
    <div>
      <PageHeader
        title="📊 投资看板"
        subtitle={dateStr}
      />

      <div className="grid grid-cols-2 gap-4 mb-6">
        <GlassCard className="text-center">
          <p className="text-xs text-gray-400">系统状态</p>
          <p className="text-lg font-bold text-green-400 mt-2">✅ 管线就绪</p>
          <p className="text-xs text-gray-500 mt-1">v0.1.0 · Pages + D1</p>
        </GlassCard>
        <GlassCard className="text-center">
          <p className="text-xs text-gray-400">数据仓库</p>
          <p className="text-lg font-bold text-brand-accent mt-2">255+ 文件</p>
          <p className="text-xs text-gray-500 mt-1">GitHub版本控制</p>
        </GlassCard>
      </div>

      <GlassCard className="mb-6">
        <h2 className="text-sm font-semibold text-gray-300 mb-3">🚀 开发路线</h2>
        <div className="space-y-2">
          {[
            { stage: 'v0.1.0 管线就绪', status: '✅', desc: 'GitHub + D1 + Pages + SPA骨架' },
            { stage: 'v0.2.0 总览页MVP', status: '🔴', desc: '大盘指数 + 组合速览 + 板块资金流' },
            { stage: 'v0.3.0 持仓+板块', status: '🔴', desc: '14基金表 + ECharts图表' },
            { stage: 'v0.4.0 行情+资讯', status: '🔴', desc: '指数 + KOL + RSS' },
            { stage: 'v0.5.0 历史+交互', status: '🔴', desc: '净值曲线 + 问AI' },
          ].map(item => (
            <div key={item.stage} className="flex items-center gap-3 text-sm">
              <span>{item.status}</span>
              <span className="text-white font-medium">{item.stage}</span>
              <span className="text-gray-500 text-xs">{item.desc}</span>
            </div>
          ))}
        </div>
      </GlassCard>

      <div className="text-center text-gray-600 text-xs mt-8">
        investment-system · v0.1.0 · Cloudflare Pages
      </div>
    </div>
  );
}
