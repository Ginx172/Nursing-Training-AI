import React from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

// ---- Types ----

export interface KPI {
  value: number;
  previous: number;
  trend_pct: number;
}

export interface OverviewData {
  period_days: number;
  kpis: {
    new_users: KPI;
    active_users: KPI;
    questions_answered: KPI;
    avg_accuracy_pct: KPI;
    training_sessions: KPI;
    avg_session_score: KPI;
  };
}

export interface ActivityDataPoint {
  date: string;
  answers: number;
  correct_answers: number;
  accuracy_pct: number;
  sessions: number;
  new_users: number;
}

export interface BandPerformance {
  band: string;
  total_answers: number;
  correct_answers: number;
  accuracy_pct: number;
  avg_time_seconds: number;
  sessions_completed: number;
  avg_session_score: number;
}

export interface SpecialtyPerformance {
  specialty: string;
  total_answers: number;
  correct_answers: number;
  accuracy_pct: number;
  avg_time_seconds: number;
}

export interface DistributionItem {
  name: string;
  value: number;
}

// ---- Colors ----

const COLORS = ['#4338ca', '#0d9488', '#7c3aed', '#ea580c', '#2563eb', '#dc2626', '#16a34a', '#854d0e'];

// ---- KPI Card ----

export function KPICard({ label, kpi, suffix }: { label: string; kpi: KPI; suffix?: string }) {
  const isUp = kpi.trend_pct > 0;
  const isDown = kpi.trend_pct < 0;
  const arrow = isUp ? 'up' : isDown ? 'down' : '';
  const trendColor = isUp ? '#10b981' : isDown ? '#ef4444' : '#94a3b8';

  return (
    <div style={{
      background: '#f8fafc', borderRadius: 12, padding: 20,
      border: '1px solid #e2e8f0', textAlign: 'center', flex: '1 1 150px', minWidth: 140,
    }}>
      <div style={{ fontSize: 28, fontWeight: 800, color: '#4338ca' }}>
        {typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}{suffix || ''}
      </div>
      <div style={{ color: '#64748b', fontSize: 13, marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 12, color: trendColor, fontWeight: 600 }}>
        {arrow === 'up' && '\u25B2 '}
        {arrow === 'down' && '\u25BC '}
        {kpi.trend_pct > 0 ? '+' : ''}{kpi.trend_pct}% vs prev
      </div>
    </div>
  );
}

// ---- Date Range Selector ----

export function DateRangeSelector({ value, onChange }: { value: number; onChange: (d: number) => void }) {
  const options = [7, 30, 90];
  return (
    <div style={{ display: 'flex', gap: 4 }}>
      {options.map((d) => (
        <button
          key={d}
          onClick={() => onChange(d)}
          style={{
            padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600, cursor: 'pointer',
            border: '1px solid #e2e8f0',
            background: value === d ? '#4338ca' : '#fff',
            color: value === d ? '#fff' : '#64748b',
          }}
        >
          {d}d
        </button>
      ))}
    </div>
  );
}

// ---- Activity Line Chart ----

export function ActivityLineChart({ data }: { data: ActivityDataPoint[] }) {
  const formatted = data.map((d) => ({
    ...d,
    date: d.date.slice(5), // MM-DD
  }));

  return (
    <div style={{ background: '#f8fafc', borderRadius: 12, padding: 20, border: '1px solid #e2e8f0' }}>
      <h3 style={{ margin: '0 0 16px', fontSize: 16, color: '#334155' }}>Activity Over Time</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formatted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="answers" stroke="#4338ca" name="Answers" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="sessions" stroke="#0d9488" name="Sessions" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="new_users" stroke="#7c3aed" name="New Users" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// ---- Performance Bar Chart ----

export function PerformanceBarChart({ data, dataKey, nameKey, title }: {
  data: any[];
  dataKey: string;
  nameKey: string;
  title: string;
}) {
  return (
    <div style={{ background: '#f8fafc', borderRadius: 12, padding: 20, border: '1px solid #e2e8f0', flex: '1 1 400px' }}>
      <h3 style={{ margin: '0 0 16px', fontSize: 16, color: '#334155' }}>{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey={nameKey} tick={{ fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
          <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Bar dataKey={dataKey} fill="#4338ca" name="Accuracy %" radius={[4, 4, 0, 0]} />
          <Bar dataKey="total_answers" fill="#0d9488" name="Total Answers" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// ---- Distribution Pie Chart ----

export function DistributionPieChart({ data, title }: { data: DistributionItem[]; title: string }) {
  return (
    <div style={{ background: '#f8fafc', borderRadius: 12, padding: 20, border: '1px solid #e2e8f0', flex: '1 1 400px' }}>
      <h3 style={{ margin: '0 0 16px', fontSize: 16, color: '#334155' }}>{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={100}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((_, idx) => (
              <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
