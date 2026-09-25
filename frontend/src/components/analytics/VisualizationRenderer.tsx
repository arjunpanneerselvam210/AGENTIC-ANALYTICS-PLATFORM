import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import type { VisualizationHint } from '../../types/analytics';

interface VisualizationRendererProps {
  hint?: VisualizationHint;
  columns: string[];
  rows: Record<string, any>[];
}

const PALETTE = ['#10B981', '#06B6D4', '#6366F1', '#F59E0B', '#EC4899', '#8B5CF6', '#14B8A6'];

export const VisualizationRenderer: React.FC<VisualizationRendererProps> = ({
  hint,
  columns,
  rows,
}) => {
  if (!rows || rows.length === 0) {
    return (
      <div className="py-8 text-center text-xs text-slate-500">
        No records returned for visualization.
      </div>
    );
  }

  // 1. Resolve Hint Type and Custom Axes if specified as an object
  let hintType = 'table';
  let customX: string | undefined;
  let customY: string | undefined;
  let customTitle: string | undefined;

  if (typeof hint === 'object' && hint !== null) {
    hintType = hint.type || 'table';
    customX = hint.x_axis;
    customY = hint.y_axis;
    customTitle = hint.title;
  } else if (typeof hint === 'string') {
    hintType = hint;
  }

  // Normalize hintType
  if (hintType === 'line_chart') hintType = 'line';
  if (hintType === 'bar_chart') hintType = 'bar';
  if (hintType === 'pie_chart') hintType = 'pie';
  if (hintType === 'metric_card') hintType = 'kpi';

  // 2. Identify Dimensions (X-Axis) and Numeric Metrics (Y-Axis)
  const xKey = customX || columns[0] || 'category';
  const numericColumns = columns.filter((col) => {
    return col !== xKey && rows.some((r) => typeof r[col] === 'number');
  });

  const yKey = customY || numericColumns[0] || columns[1] || columns[0];

  // 3. Automatic Fallback Logic if Hint is Missing or Generic
  if (!hint || hintType === 'table') {
    if (rows.length === 1 && numericColumns.length === 1) {
      hintType = 'kpi';
    } else {
      const xKeyLower = xKey.toLowerCase();
      if (xKeyLower.includes('month') || xKeyLower.includes('date') || xKeyLower.includes('year')) {
        hintType = 'line';
      } else if (numericColumns.length >= 1 && rows.length <= 6) {
        hintType = 'donut';
      } else if (numericColumns.length >= 1) {
        hintType = 'bar';
      }
    }
  }

  // Helper: Format values nicely with rupee sign and magnitude
  const formatValue = (v: any) => {
    if (typeof v === 'number') {
      if (Math.abs(v) >= 10000000) return `₹${(v / 10000000).toFixed(2)}Cr`;
      if (Math.abs(v) >= 100000) return `₹${(v / 100000).toFixed(1)}L`;
      if (Math.abs(v) >= 1000) return `₹${(v / 1000).toFixed(1)}k`;
      return v.toLocaleString();
    }
    return String(v ?? '-');
  };

  const renderTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#0B0F19] border border-slate-700 rounded-lg p-2.5 text-xs shadow-2xl z-50">
          <p className="font-semibold text-white mb-1.5 border-b border-slate-800 pb-1">{label}</p>
          {payload.map((p: any, idx: number) => (
            <div key={idx} className="flex items-center justify-between gap-3 text-xs font-mono py-0.5">
              <span className="text-slate-400 capitalize">{p.name.replace(/_/g, ' ')}:</span>
              <span style={{ color: p.color || '#10B981' }} className="font-semibold">
                {formatValue(p.value)}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  // Case A: KPI / Metric Card
  if (hintType === 'kpi' || (rows.length === 1 && numericColumns.length === 1)) {
    const valKey = numericColumns[0] || columns[1] || columns[0];
    const val = rows[0][valKey];
    return (
      <div className="p-6 bg-[#080C14] border border-slate-800 rounded-xl text-center shadow-lg">
        {customTitle && <p className="text-xs text-slate-400 font-medium mb-1">{customTitle}</p>}
        <span className="text-xs uppercase font-bold text-slate-400 tracking-wider">
          {valKey.replace(/_/g, ' ')}
        </span>
        <div className="text-3xl sm:text-4xl font-extrabold text-emerald-400 font-mono mt-2 tracking-tight">
          {formatValue(val)}
        </div>
      </div>
    );
  }

  // Case B: Donut / Pie Chart
  if (hintType === 'pie' || hintType === 'donut') {
    const isDonut = hintType === 'donut';
    const pieData = rows.slice(0, 10).map((r, i) => ({
      name: String(r[xKey] ?? `Item ${i + 1}`),
      value: Number(r[yKey] ?? 1),
    }));

    return (
      <div className="space-y-2">
        {customTitle && <h6 className="text-xs font-semibold text-slate-300">{customTitle}</h6>}
        <div className="h-64 w-full relative flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Tooltip
                content={({ active, payload }: any) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-[#0B0F19] border border-slate-700 rounded-lg p-2.5 text-xs shadow-xl">
                        <p className="font-semibold text-white">{payload[0].name}</p>
                        <p className="text-emerald-400 font-mono font-semibold">{formatValue(payload[0].value)}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={isDonut ? 55 : 0}
                outerRadius={85}
                paddingAngle={isDonut ? 3 : 1}
                dataKey="value"
              >
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                ))}
              </Pie>
              <Legend
                formatter={(val) => <span className="text-xs text-slate-300">{val}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // Case C: Area Chart
  if (hintType === 'area') {
    return (
      <div className="space-y-2">
        {customTitle && <h6 className="text-xs font-semibold text-slate-300">{customTitle}</h6>}
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={rows} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey={xKey} stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={formatValue} />
              <Tooltip content={renderTooltip} />
              <Area type="monotone" dataKey={yKey} stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#areaGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // Case D: Line Chart
  if (hintType === 'line') {
    return (
      <div className="space-y-2">
        {customTitle && <h6 className="text-xs font-semibold text-slate-300">{customTitle}</h6>}
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={rows} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey={xKey} stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={formatValue} />
              <Tooltip content={renderTooltip} />
              {numericColumns.length > 1 && numericColumns.length <= 3 ? (
                numericColumns.map((col, idx) => (
                  <Line
                    key={col}
                    type="monotone"
                    dataKey={col}
                    stroke={PALETTE[idx % PALETTE.length]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                ))
              ) : (
                <Line
                  type="monotone"
                  dataKey={yKey}
                  stroke="#10B981"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#10B981' }}
                  activeDot={{ r: 6 }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // Case E: Bar Chart (Supports multi-series e.g. July vs August comparison or category rankings)
  return (
    <div className="space-y-2">
      {customTitle && <h6 className="text-xs font-semibold text-slate-300">{customTitle}</h6>}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows.slice(0, 15)} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis dataKey={xKey} stroke="#64748B" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={formatValue} />
            <Tooltip content={renderTooltip} />
            {numericColumns.length > 1 && numericColumns.length <= 4 ? (
              numericColumns.map((col, idx) => (
                <Bar
                  key={col}
                  dataKey={col}
                  fill={PALETTE[idx % PALETTE.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))
            ) : (
              <Bar dataKey={yKey} fill="#10B981" radius={[4, 4, 0, 0]} />
            )}
            {numericColumns.length > 1 && <Legend formatter={(val) => <span className="text-xs text-slate-300 capitalize">{val.replace(/_/g, ' ')}</span>} />}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
