import { useEffect, useState, useRef, useCallback } from 'react';
import { PageHeader } from '../components/PageHeader';
import { GlassCard } from '../components/GlassCard';
import { fetchDashboard, pctColor, formatPct } from '../lib/api';
import type { DashboardData } from '../types';
import * as echarts from 'echarts';

type DetailItem = {
  title: string;
  url: string;
  date: string;
} | null;

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<DetailItem>(null);
  const [detailContent, setDetailContent] = useState('');
  const [detailLoading, setDetailLoading] = useState(false);
  const flowChartRef = useRef<HTMLDivElement>(null);
  const gaugeRef = useRef<HTMLDivElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);

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

  // 点击详情 → 从R2 fetch完整markdown
  const openDetail = useCallback(async (item: DetailItem) => {
    if (!item) return;
    setDetail(item);
    setDetailContent('');
    setDetailLoading(true);
    try {
      const resp = await fetch(item.url);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const text = await resp.text();
      setDetailContent(text);
    } catch {
      setDetailContent('**加载失败** — R2文件暂不可用');
    }
    setDetailLoading(false);
  }, []);

  const closeDetail = useCallback(() => {
    setDetail(null);
    setDetailContent('');
  }, []);

  // ESC／点击遮罩关闭
  useEffect(() => {
    if (!detail) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') closeDetail(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [detail, closeDetail]);

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
            { offset: 0, color: '#f43f5e' }, { offset: 1, color: '#fb7185' },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
        label: { show: true, position: 'right', color: '#9ca3af', fontSize: 10,
                 formatter: (p: any) => `${p.value.toFixed(0)}亿` },
      }],
    });
    return () => chart.dispose();
  }, [data]);

  // ECharts: 科技偏离度仪表盘
  useEffect(() => {
    if (!data?.portfolio?.tech_deviation_pct || !gaugeRef.current) return;
    const chart = echarts.init(gaugeRef.current);
    const dev = data.portfolio.tech_deviation_pct;
    chart.setOption({
      backgroundColor: 'transparent',
      series: [{
        type: 'gauge', center: ['50%', '55%'], radius: '85%',
        min: -50, max: 50, splitNumber: 5,
        axisLine: {
          lineStyle: {
            width: 8, color: [
              [0.3, '#22c55e'], [0.5, '#eab308'], [1, '#ef4444'],
            ],
          },
        },
        axisTick: { show: false },
        splitLine: { length: 8, lineStyle: { width: 2, color: '#4b5563' } },
        axisLabel: { color: '#9ca3af', fontSize: 9, distance: 15 },
        pointer: { length: '50%', width: 3, itemStyle: { color: '#f43f5e' } },
        detail: {
          valueAnimation: true,
          formatter: `{value}%`, color: '#f43f5e', fontSize: 14,
          fontFamily: 'monospace', offsetCenter: [0, '65%'],
        },
        data: [{ value: dev, name: '' }],
        title: { show: false },
      }],
    });
    return () => chart.dispose();
  }, [data]);

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">加载中...</div>;
  if (error) return <div className="flex items-center justify-center h-64 text-red-400">{error}</div>;
  if (!data) return <div className="flex items-center justify-center h-64 text-gray-500">暂无数据</div>;

  const pf = data.portfolio;
  const mv = data.market_overview;
  const typeLabel: Record<string, string> = { morning: '晨报', noon: '午报', closing: '收盘' };

  return (
    <div className="relative min-h-screen">
      <PageHeader title="📊 投资看板" />

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
              {formatPct(pf.tech_deviation_pct)}
            </p>
          </GlassCard>
        </div>
      </section>

      {/* 板块资金流 + 偏离度仪表盘 */}
      <section className="mb-6">
        <h2 className="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-wider">板块资金流</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <GlassCard className="sm:col-span-2">
            <div ref={flowChartRef} style={{ height: 160 }} />
          </GlassCard>
          <GlassCard className="flex flex-col items-center">
            <div ref={gaugeRef} style={{ height: 120, width: '100%' }} className="pointer-events-none" />
            <p className="text-[10px] text-gray-500 text-center mt-1 px-2 leading-relaxed">
              科技板块市值占比偏离基准配置的比例<br/>正值=超配 负值=低配
            </p>
          </GlassCard>
        </div>
      </section>

      {/* 涨跌家数 */}
      <section className="mb-6">
        <h2 className="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-wider">市场总览</h2>
        <GlassCard>
          <div className="flex flex-wrap gap-4 text-sm">
            <span>涨 <span className="text-green-400 font-bold">{mv.advance}</span></span>
            <span>跌 <span className="text-red-400 font-bold">{mv.decline}</span></span>
            <span>平 <span className="text-gray-400">{mv.flat}</span></span>
            <span>涨停 <span className="text-purple-400 font-bold">{data.indices.length > 0 ? '—' : '—'}</span></span>
            <span>合计 <span className="text-gray-300">{mv.total || mv.advance + mv.decline + (mv.flat || 0)}</span></span>
          </div>
        </GlassCard>
      </section>

      {/* 网格: 分析摘要 + 操作记录 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        {/* 分析摘要 — 可点击 */}
        <GlassCard>
          <h3 className="text-xs font-semibold text-gray-400 mb-2">最新分析</h3>
          <div className="space-y-2">
            {data.latest_analysis?.map((a, i) => (
              <button key={i}
                   type="button"
                   className="w-full text-left text-xs border-b border-white/5 pb-2 last:border-0 cursor-pointer hover:bg-white/5 rounded p-1 -mx-1 transition-colors"
                   onClick={() => openDetail({
                     title: `${typeLabel[a.type] || a.type} · ${a.date}`,
                     url: a.detail_url, date: a.date
                   })}>
                <div className="flex items-center gap-2">
                  <span className="text-gray-300 font-medium">{typeLabel[a.type] || a.type}</span>
                  <span className="text-gray-500 text-[10px]">{a.date}</span>
                </div>
                {a.summary && (
                  <p className="text-gray-400 mt-1 leading-relaxed">{a.summary}</p>
                )}
              </button>
            ))}
          </div>
        </GlassCard>

        {/* 操作记录 — 可点击 */}
        <GlassCard>
          <h3 className="text-xs font-semibold text-gray-400 mb-2">最近操作</h3>
          <div className="space-y-2">
            {data.operations?.map((op, i) => (
              <button key={i}
                   type="button"
                   className="w-full text-left text-sm border-b border-white/5 pb-2 last:border-0 cursor-pointer hover:bg-white/5 rounded p-1 -mx-1 transition-colors"
                   onClick={() => openDetail({
                     title: op.title || `操作 ${op.date}`,
                     url: op.detail_url, date: op.date
                   })}>
                <div className="flex justify-between items-start">
                  <span className="font-medium text-gray-200 text-xs">
                    {op.title || '📝 操作记录'}
                  </span>
                  <span className="text-xs text-gray-500 ml-2 shrink-0">{op.date}</span>
                </div>
                {op.summary && (
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{op.summary}</p>
                )}
              </button>
            ))}
          </div>
        </GlassCard>
      </div>

      <div className="text-center text-gray-600 text-xs mt-6">
        投资看板 v0.2.0 · 数据来源: fund_tools · 每交易日更新
      </div>

      {/* 详情弹窗 */}
      {detail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
             onClick={closeDetail}>
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
          <div ref={modalRef}
               className="relative bg-gray-900 border border-white/10 rounded-xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl"
               onClick={e => e.stopPropagation()}>
            {/* 弹窗头 */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <div>
                <h2 className="text-sm font-bold text-white">{detail.title}</h2>
                <p className="text-[10px] text-gray-500 mt-0.5">{detail.date}</p>
              </div>
              <button onClick={closeDetail}
                      className="text-gray-500 hover:text-white text-lg leading-none p-1">
                ✕
              </button>
            </div>
            {/* 弹窗内容 — 检测HTML/MD渲染 */}
            <div className="overflow-y-auto p-4 flex-1">
              {detailLoading ? (
                <div className="text-gray-400 text-sm">加载中...</div>
              ) : detail?.url.endsWith('.html') ? (
                <div className="text-sm text-gray-300 leading-relaxed"
                     dangerouslySetInnerHTML={{ __html: detailContent }} />
              ) : (
                <pre className="text-xs text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">{detailContent}</pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
