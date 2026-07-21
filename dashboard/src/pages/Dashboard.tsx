import { useEffect, useState, useRef } from 'react';
import { PageHeader } from '../components/PageHeader';
import { GlassCard } from '../components/GlassCard';
import { fetchDashboard, pctColor, formatPct } from '../lib/api';
import type { DashboardData } from '../types';
import * as echarts from 'echarts';

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const flowChartRef = useRef<HTMLDivElement>(null);
  const gaugeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchDashboard().then(d => {
      if (cancelled) return;
      setData(d);
      setLoading(false);
    }).catch(() => {
      if (cancelled) return;
      setError('数据加载失败');
      setLoading(false);
    });
    return () => { cancelled = true; };
  }, []);

  // ECharts: 板块资金流柱状图
  useEffect(() => {
    if (!data?.sectors?.fund_flow?.length || !flowChartRef.current) return;
    const chart = echarts.init(flowChartRef.current);
    const top5 = data.sectors.fund_flow.slice(0, 5);
    chart.setOption({
      backgroundColor: 'transparent',
      grid: { left: 100, right: 20, top: 10, bottom: 30 },
      xAxis: { type: 'value', axisLabel: { color: '#9ca3af', fontSize: 10 } },
      yAxis: {
        type: 'category', data: top5.map(s => s.name).reverse(),
        axisLabel: { color: '#d1d5db', fontSize: 10 },
      },
      series: [{
        type: 'bar', data: top5.map(s => s.net_inflow_yi).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#f59e0b' }, { offset: 1, color: '#f97316' }
          ]),
          borderRadius: [0, 4, 4, 0],
        },
        label: { show: true, position: 'right', color: '#9ca3af', fontSize: 10,
          formatter: (p: any) => `${p.value.toFixed(1)}亿` },
      }],
      tooltip: { trigger: 'axis' },
    });
    return () => chart.dispose();
  }, [data]);

  // ECharts: 偏离度仪表盘
  useEffect(() => {
    if (!data?.portfolio?.tech_deviation_pct === undefined || !gaugeRef.current) return;
    const dev = data!.portfolio.tech_deviation_pct;
    const chart = echarts.init(gaugeRef.current);
    chart.setOption({
      backgroundColor: 'transparent',
      series: [{
        type: 'gauge', center: ['50%', '60%'], radius: '80%',
        startAngle: 220, endAngle: -40,
        min: -30, max: 30,
        splitNumber: 6,
        axisLine: {
          lineStyle: {
            width: 12,
            color: [
              [0.25, '#22c55e'],   // 0~25% → green (under-allocated)
              [0.5, '#f59e0b'],    // 25~50% → yellow (balanced)
              [0.75, '#f97316'],   // 50~75% → orange
              [1, '#ef4444'],      // 75~100% → red (over-allocated)
            ]
          }
        },
        axisTick: { show: false },
        splitLine: { length: 8, lineStyle: { color: '#4b5563' } },
        axisLabel: { color: '#9ca3af', fontSize: 9,
          formatter: (v: number) => `${v > 0 ? '+' : ''}${v}%` },
        pointer: { length: '60%', width: 4, itemStyle: { color: '#f59e0b' } },
        detail: {
          valueAnimation: true,
          formatter: `{value}%\n偏离度`,
          color: dev > 15 ? '#ef4444' : dev > 5 ? '#f59e0b' : '#22c55e',
          fontSize: 14, fontWeight: 'bold',
        },
        data: [{ value: Math.round(dev * 10) / 10 }],
      }],
    });
    return () => chart.dispose();
  }, [data]);

  // ── 加载态 ──
  if (loading) return (
    <div>
      <PageHeader title="📊 投资看板" subtitle="加载中..." />
      <div className="grid grid-cols-2 gap-4">
        {[1,2,3,4].map(i => (
          <GlassCard key={i}><div className="h-20 bg-white/5 animate-pulse rounded" /></GlassCard>
        ))}
      </div>
    </div>
  );

  if (error || !data) return (
    <div>
      <PageHeader title="📊 投资看板" subtitle={new Date().toLocaleDateString('zh-CN')} />
      <GlassCard className="text-center py-8">
        <p className="text-red-400 text-lg">⚠️ {error || '暂无数据'}</p>
        <p className="text-gray-500 text-sm mt-2">数据源可能尚未更新，请稍后再试</p>
      </GlassCard>
    </div>
  );

  // ── 正常渲染 ──
  const pf = data.portfolio;
  const mv = data.market_overview;

  return (
    <div>
      <PageHeader
        title="📊 投资看板"
        subtitle={`${data.date} ${data.time} · 数据每4h更新`}
      />

      {/* 大盘指数 */}
      <section className="mb-6">
        <h2 className="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-wider">大盘指数</h2>
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
          {data.indices.map(idx => (
            <GlassCard key={idx.code} className="text-center p-2">
              <p className="text-xs text-gray-500 truncate">{idx.name}</p>
              <p className="text-sm font-bold text-white mt-0.5 font-mono">{idx.price.toFixed(2)}</p>
              <p className={`text-xs font-medium ${pctColor(idx.change_pct)}`}>
                {formatPct(idx.change_pct)}
              </p>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* 组合速览 */}
      <section className="mb-6">
        <h2 className="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-wider">组合速览</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <GlassCard>
            <p className="text-xs text-gray-400">总市值</p>
            <p className="text-lg font-bold text-white font-mono mt-1">¥{pf.total_value.toFixed(0)}</p>
          </GlassCard>
          <GlassCard>
            <p className="text-xs text-gray-400">总盈亏</p>
            <p className={`text-lg font-bold font-mono mt-1 ${pctColor(pf.total_profit_pct)}`}>
              {formatPct(pf.total_profit_pct)}
            </p>
          </GlassCard>
          <GlassCard>
            <p className="text-xs text-gray-400">总成本</p>
            <p className="text-lg font-bold text-white font-mono mt-1">¥{pf.total_cost.toFixed(0)}</p>
          </GlassCard>
          <GlassCard>
            <p className="text-xs text-gray-400">科技偏离度</p>
            <p className={`text-lg font-bold font-mono mt-1 ${pctColor(pf.tech_deviation_pct)}`}>
              {pf.tech_deviation_pct > 0 ? '+' : ''}{pf.tech_deviation_pct}%
            </p>
          </GlassCard>
        </div>
      </section>

      {/* 中部: 板块资金流 + 偏离度仪表 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        {/* 板块资金流TOP5 */}
        <GlassCard>
          <h3 className="text-xs font-semibold text-gray-400 mb-2">板块资金流 TOP5</h3>
          <div ref={flowChartRef} style={{ height: 200 }} />
        </GlassCard>

        {/* 偏离度仪表盘 */}
        <GlassCard>
          <h3 className="text-xs font-semibold text-gray-400 mb-2">科技偏离度</h3>
          <div ref={gaugeRef} style={{ height: 180 }} />
        </GlassCard>
      </div>

      {/* 涨跌家数 + 建仓进度 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <GlassCard>
          <h3 className="text-xs font-semibold text-gray-400 mb-2">涨跌家数</h3>
          <div className="flex items-center gap-4 mt-1">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-400 font-mono">{mv.advance}</p>
              <p className="text-xs text-gray-500">上涨</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-400 font-mono">{mv.decline}</p>
              <p className="text-xs text-gray-500">下跌</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-400 font-mono">{mv.flat}</p>
              <p className="text-xs text-gray-500">平盘</p>
            </div>
            <div className="text-xs text-gray-600 ml-auto">
              共{mv.total || mv.advance + mv.decline + mv.flat}只
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <h3 className="text-xs font-semibold text-gray-400 mb-2">建仓进度</h3>
          {pf.building_funds?.length > 0 ? pf.building_funds.map(b => (
            <div key={b.code} className="mt-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-300">{b.name || b.code}</span>
                <span className="text-gray-400">¥{b.current.toFixed(0)}/{b.target}</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2 mt-1">
                <div className="bg-brand-accent h-2 rounded-full transition-all"
                     style={{ width: `${Math.min(b.progress_pct, 100)}%` }} />
              </div>
            </div>
          )) : <p className="text-gray-500 text-xs mt-2">暂无建仓数据</p>}
        </GlassCard>
      </div>

      {/* 最新分析 */}
      {data.latest_analysis?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-wider">最新分析</h2>
          <div className="space-y-2">
            {data.latest_analysis.map((a: any, i: number) => (
              <GlassCard key={i}>
                <div className="flex items-start gap-2">
                  <span className="text-xs px-1.5 py-0.5 rounded bg-brand-accent/20 text-brand-accent font-medium mt-0.5">
                    {a.type === 'morning' ? '晨报' : a.type === 'noon' ? '午报' : a.type === 'closing' ? '收盘' : a.type}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-400">{a.date}</p>
                    <p className="text-sm text-gray-300 mt-0.5 line-clamp-2">{a.summary || '无摘要'}</p>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </section>
      )}

      {/* 操作记录 */}
      {data.operations?.length > 0 && (
        <GlassCard>
          <h3 className="text-xs font-semibold text-gray-400 mb-2">最近操作</h3>
          <div className="space-y-1">
            {data.operations.map((op: any) => (
              <div key={op.date} className="flex items-center gap-2 text-xs">
                <span className="text-gray-500">{op.date}</span>
                <span className="text-gray-300">📝 操作记录</span>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      <div className="text-center text-gray-600 text-xs mt-6">
        投资看板 v0.2.0 · 数据来源: fund_tools · 每交易日更新
      </div>
    </div>
  );
}
