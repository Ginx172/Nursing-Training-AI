import React, { useState, useEffect, FormEvent } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/router';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
import type {
  OverviewData, ActivityDataPoint, BandPerformance, SpecialtyPerformance, DistributionItem,
} from '../components/AnalyticsCharts';

const AnalyticsCharts = dynamic(() => import('../components/AnalyticsCharts').then((mod) => ({
  default: () => null,
  KPICard: mod.KPICard,
  DateRangeSelector: mod.DateRangeSelector,
  ActivityLineChart: mod.ActivityLineChart,
  PerformanceBarChart: mod.PerformanceBarChart,
  DistributionPieChart: mod.DistributionPieChart,
})), { ssr: false }) as any;

// Lazy load chart components (recharts needs browser APIs)
const KPICard = dynamic(() => import('../components/AnalyticsCharts').then((m) => m.KPICard), { ssr: false });
const DateRangeSelector = dynamic(() => import('../components/AnalyticsCharts').then((m) => m.DateRangeSelector), { ssr: false });
const ActivityLineChart = dynamic(() => import('../components/AnalyticsCharts').then((m) => m.ActivityLineChart), { ssr: false });
const PerformanceBarChart = dynamic(() => import('../components/AnalyticsCharts').then((m) => m.PerformanceBarChart), { ssr: false });
const DistributionPieChart = dynamic(() => import('../components/AnalyticsCharts').then((m) => m.DistributionPieChart), { ssr: false });

interface PlatformStats {
  total_users: number;
  active_users: number;
  total_questions_in_db: number;
  total_answers_submitted: number;
  total_training_sessions: number;
  subscriptions_by_tier: Record<string, number>;
  users_by_role: Record<string, number>;
}

interface UserRow {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  nhs_band: string | null;
  subscription_tier: string;
  is_active: boolean;
  is_verified: boolean;
  last_login: string | null;
  created_at: string;
}

interface QuestionRow {
  id: number;
  title: string;
  question_type: string;
  difficulty_level: string;
  nhs_band: string | null;
  specialty: string | null;
  is_active: boolean;
}

interface AuditEntry {
  timestamp: string;
  event_type: string;
  severity: string;
  source_ip: string;
  details: any;
}

type Tab = 'overview' | 'users' | 'questions' | 'audit' | 'analytics' | 'ai-insights' | 'quality';

function AdminContent() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<Tab>('overview');

  // Overview
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // Users
  const [users, setUsers] = useState<UserRow[]>([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [usersSearch, setUsersSearch] = useState('');
  const [usersLoading, setUsersLoading] = useState(false);

  // Questions
  const [questions, setQuestions] = useState<QuestionRow[]>([]);
  const [questionsTotal, setQuestionsTotal] = useState(0);
  const [questionsSearch, setQuestionsSearch] = useState('');
  const [questionsLoading, setQuestionsLoading] = useState(false);

  // Audit
  const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);
  const [auditLoading, setAuditLoading] = useState(false);

  // Analytics
  const [analyticsDays, setAnalyticsDays] = useState(30);
  const [analyticsOverview, setAnalyticsOverview] = useState<OverviewData | null>(null);
  const [activityData, setActivityData] = useState<ActivityDataPoint[]>([]);
  const [bandPerformance, setBandPerformance] = useState<BandPerformance[]>([]);
  const [specialtyPerformance, setSpecialtyPerformance] = useState<SpecialtyPerformance[]>([]);
  const [questionDistribution, setQuestionDistribution] = useState<any>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);

  // Question Quality
  const [qualityReport, setQualityReport] = useState<any>(null);
  const [qualityLoading, setQualityLoading] = useState(false);
  const [dedupRunning, setDedupRunning] = useState(false);
  const [improveRunning, setImproveRunning] = useState(false);

  // AI Insights
  const [ollamaHealth, setOllamaHealth] = useState<any>(null);
  const [aiInsights, setAiInsights] = useState<any[]>([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiRunning, setAiRunning] = useState(false);
  const [expandedInsight, setExpandedInsight] = useState<number | null>(null);

  // Messages
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  // Redirect non-admin
  useEffect(() => {
    if (user && user.role !== 'admin') {
      router.push('/dashboard');
    }
  }, [user, router]);

  // Load stats
  useEffect(() => {
    if (tab === 'overview') loadStats();
  }, [tab]);

  // Load users
  useEffect(() => {
    if (tab === 'users') loadUsers();
  }, [tab]);

  // Load questions
  useEffect(() => {
    if (tab === 'questions') loadQuestions();
  }, [tab]);

  // Load audit
  useEffect(() => {
    if (tab === 'audit') loadAudit();
  }, [tab]);

  // Load analytics
  useEffect(() => {
    if (tab === 'analytics') loadAnalytics();
  }, [tab, analyticsDays]);

  // Load Question Quality
  useEffect(() => {
    if (tab === 'quality') loadQualityReport();
  }, [tab]);

  // Load AI Insights
  useEffect(() => {
    if (tab === 'ai-insights') { loadOllamaHealth(); loadAiInsights(); }
  }, [tab]);

  async function loadStats() {
    setStatsLoading(true);
    try {
      const res = await api.get('/api/admin/stats');
      setStats(res.data);
    } catch { setErr('Failed to load stats'); }
    setStatsLoading(false);
  }

  async function loadUsers() {
    setUsersLoading(true);
    try {
      const params: any = { limit: 50, offset: 0 };
      if (usersSearch) params.search_term = usersSearch;
      const res = await api.get('/api/admin/users/search', { params });
      setUsers(res.data.users || []);
      setUsersTotal(res.data.total || 0);
    } catch { setErr('Failed to load users'); }
    setUsersLoading(false);
  }

  async function loadQuestions() {
    setQuestionsLoading(true);
    try {
      const params: any = { limit: 50, offset: 0 };
      if (questionsSearch) params.search_term = questionsSearch;
      const res = await api.get('/api/admin/questions/search', { params });
      setQuestions(res.data.questions || []);
      setQuestionsTotal(res.data.total || 0);
    } catch { setErr('Failed to load questions'); }
    setQuestionsLoading(false);
  }

  async function loadAudit() {
    setAuditLoading(true);
    try {
      const res = await api.get('/api/admin/audit-log', { params: { limit: 50 } });
      setAuditLogs(res.data.entries || res.data || []);
    } catch { setErr('Failed to load audit log'); }
    setAuditLoading(false);
  }

  async function toggleUserActive(userId: number, currentlyActive: boolean) {
    setMsg(''); setErr('');
    try {
      await api.put(`/api/admin/users/${userId}`, { is_active: !currentlyActive });
      setMsg(`User ${currentlyActive ? 'deactivated' : 'activated'}`);
      loadUsers();
    } catch { setErr('Failed to update user'); }
  }

  async function changeUserRole(userId: number, newRole: string) {
    setMsg(''); setErr('');
    try {
      await api.put(`/api/admin/users/${userId}`, { role: newRole });
      setMsg('Role updated');
      loadUsers();
    } catch { setErr('Failed to update role'); }
  }

  async function loadAnalytics() {
    setAnalyticsLoading(true);
    setErr('');
    try {
      const params = { days: analyticsDays };
      const [overviewRes, activityRes, bandRes, specialtyRes, distRes] = await Promise.all([
        api.get('/api/admin/analytics/overview', { params }),
        api.get('/api/admin/analytics/activity-over-time', { params }),
        api.get('/api/admin/analytics/performance-by-band', { params }),
        api.get('/api/admin/analytics/performance-by-specialty', { params }),
        api.get('/api/admin/analytics/question-difficulty'),
      ]);
      setAnalyticsOverview(overviewRes.data);
      setActivityData(activityRes.data.data || []);
      setBandPerformance(bandRes.data.data || []);
      setSpecialtyPerformance(specialtyRes.data.data || []);
      setQuestionDistribution(distRes.data);
    } catch {
      setErr('Failed to load analytics data');
    }
    setAnalyticsLoading(false);
  }

  async function handleExportCSV(dataType: string) {
    setExportLoading(true);
    try {
      const res = await api.get('/api/admin/analytics/export/csv', {
        params: { days: analyticsDays, data_type: dataType },
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analytics_${dataType}_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      setErr('Failed to export CSV');
    }
    setExportLoading(false);
  }

  async function loadQualityReport() {
    setQualityLoading(true);
    try {
      const res = await api.get('/api/admin/question-quality/quality-report');
      setQualityReport(res.data);
    } catch { setErr('Failed to load quality report'); }
    setQualityLoading(false);
  }

  async function runDeduplication() {
    setDedupRunning(true); setMsg(''); setErr('');
    try {
      const res = await api.post('/api/admin/question-quality/deduplicate');
      setMsg(`Deduplication complete: ${res.data.deactivated} duplicates removed, ${res.data.remaining_active} questions remaining`);
      loadQualityReport();
    } catch { setErr('Deduplication failed'); }
    setDedupRunning(false);
  }

  async function runImproveBatch(target: string, batchSize: number) {
    setImproveRunning(true); setMsg(''); setErr('');
    try {
      const res = await api.post(`/api/admin/question-quality/improve-batch?batch_size=${batchSize}&target=${target}`);
      setMsg(`AI Improvement: ${res.data.improved} improved, ${res.data.failed} failed out of ${res.data.processed}`);
      loadQualityReport();
    } catch { setErr('AI improvement failed'); }
    setImproveRunning(false);
  }

  async function loadOllamaHealth() {
    try {
      const res = await api.get('/api/ai-brain/health');
      setOllamaHealth(res.data);
    } catch { setOllamaHealth({ status: 'error', message: 'Cannot reach API' }); }
  }

  async function loadAiInsights() {
    setAiLoading(true);
    try {
      const res = await api.get('/api/ai-brain/insights', { params: { limit: 20 } });
      setAiInsights(res.data.insights || []);
    } catch { setErr('Failed to load AI insights'); }
    setAiLoading(false);
  }

  async function runAiAnalysis(days: number) {
    setAiRunning(true); setErr(''); setMsg('');
    try {
      const res = await api.post(`/api/ai-brain/run-analysis?days=${days}`);
      if (res.data.success) {
        setMsg(`Analysis completed in ${res.data.generation_time_seconds}s - ${res.data.insights_count} insights generated`);
        loadAiInsights();
      } else {
        setErr(`Analysis failed: ${res.data.error || 'Unknown error'}`);
      }
    } catch (e: any) {
      setErr(e?.response?.data?.detail || 'Failed to run AI analysis');
    }
    setAiRunning(false);
  }

  const tabStyle = (t: Tab) => ({
    padding: '10px 20px',
    cursor: 'pointer',
    borderBottom: tab === t ? '3px solid #4338ca' : '3px solid transparent',
    color: tab === t ? '#4338ca' : '#666',
    fontWeight: tab === t ? 700 : 400,
    background: 'none',
    border: 'none',
    fontSize: 15,
  });

  const cardStyle: React.CSSProperties = {
    background: '#f8fafc', borderRadius: 12, padding: 20,
    border: '1px solid #e2e8f0',
  };

  const kpiStyle: React.CSSProperties = {
    ...cardStyle, textAlign: 'center', flex: '1 1 150px',
  };

  const tableStyle: React.CSSProperties = {
    width: '100%', borderCollapse: 'collapse', fontSize: 13,
  };

  const thStyle: React.CSSProperties = {
    textAlign: 'left', padding: '10px 8px', borderBottom: '2px solid #e2e8f0',
    color: '#64748b', fontWeight: 600, fontSize: 12, textTransform: 'uppercase',
  };

  const tdStyle: React.CSSProperties = {
    padding: '10px 8px', borderBottom: '1px solid #f1f5f9',
  };

  const btnSmall: React.CSSProperties = {
    padding: '4px 10px', fontSize: 12, borderRadius: 6, cursor: 'pointer',
    border: '1px solid #ddd', background: '#fff',
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 16px', fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      <Head><title>Admin Panel - Nursing Training AI</title></Head>

      {/* Nav */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 0', borderBottom: '1px solid #e2e8f0', marginBottom: 16 }}>
        <span style={{ fontWeight: 'bold', fontSize: 18, color: '#4338ca' }}>Admin Panel</span>
        <div style={{ display: 'flex', gap: 12 }}>
          <Link href="/dashboard" style={{ padding: '8px 16px', border: '1px solid #4338ca', color: '#4338ca', borderRadius: 8, textDecoration: 'none', fontSize: 14 }}>Dashboard</Link>
          <Link href="/" style={{ padding: '8px 16px', border: '1px solid #ddd', color: '#666', borderRadius: 8, textDecoration: 'none', fontSize: 14 }}>Home</Link>
        </div>
      </nav>

      {/* Messages */}
      {msg && <div style={{ background: '#ecfdf5', border: '1px solid #10b981', padding: 10, borderRadius: 8, marginBottom: 12, color: '#065f46', fontSize: 14 }}>{msg}</div>}
      {err && <div style={{ background: '#fef2f2', border: '1px solid #ef4444', padding: 10, borderRadius: 8, marginBottom: 12, color: '#991b1b', fontSize: 14 }}>{err}</div>}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 0, borderBottom: '1px solid #e2e8f0', marginBottom: 24 }}>
        <button style={tabStyle('overview')} onClick={() => setTab('overview')}>Overview</button>
        <button style={tabStyle('users')} onClick={() => setTab('users')}>Users</button>
        <button style={tabStyle('questions')} onClick={() => setTab('questions')}>Questions</button>
        <button style={tabStyle('audit')} onClick={() => setTab('audit')}>Audit Log</button>
        <button style={tabStyle('analytics')} onClick={() => setTab('analytics')}>Analytics</button>
        <button style={tabStyle('ai-insights')} onClick={() => setTab('ai-insights')}>AI Insights</button>
        <button style={tabStyle('quality')} onClick={() => setTab('quality')}>Quality</button>
      </div>

      {/* ============ OVERVIEW TAB ============ */}
      {tab === 'overview' && (
        <div>
          {statsLoading && <p>Loading stats...</p>}
          {stats && (
            <>
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
                <div style={kpiStyle}>
                  <div style={{ fontSize: 32, fontWeight: 800, color: '#4338ca' }}>{stats.total_users}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Total Users</div>
                </div>
                <div style={kpiStyle}>
                  <div style={{ fontSize: 32, fontWeight: 800, color: '#0d9488' }}>{stats.active_users}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Active Users</div>
                </div>
                <div style={kpiStyle}>
                  <div style={{ fontSize: 32, fontWeight: 800, color: '#7c3aed' }}>{stats.total_questions_in_db}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Questions</div>
                </div>
                <div style={kpiStyle}>
                  <div style={{ fontSize: 32, fontWeight: 800, color: '#ea580c' }}>{stats.total_answers_submitted}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Answers Submitted</div>
                </div>
                <div style={kpiStyle}>
                  <div style={{ fontSize: 32, fontWeight: 800, color: '#2563eb' }}>{stats.total_training_sessions}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Training Sessions</div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <div style={{ ...cardStyle, flex: '1 1 300px' }}>
                  <h3 style={{ margin: '0 0 12px', fontSize: 16, color: '#334155' }}>Subscriptions by Tier</h3>
                  {Object.entries(stats.subscriptions_by_tier || {}).map(([tier, count]) => (
                    <div key={tier} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <span style={{ textTransform: 'capitalize' }}>{tier}</span>
                      <span style={{ fontWeight: 700 }}>{count as number}</span>
                    </div>
                  ))}
                </div>
                <div style={{ ...cardStyle, flex: '1 1 300px' }}>
                  <h3 style={{ margin: '0 0 12px', fontSize: 16, color: '#334155' }}>Users by Role</h3>
                  {Object.entries(stats.users_by_role || {}).map(([role, count]) => (
                    <div key={role} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <span style={{ textTransform: 'capitalize' }}>{role}</span>
                      <span style={{ fontWeight: 700 }}>{count as number}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* ============ USERS TAB ============ */}
      {tab === 'users' && (
        <div>
          <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Search users (email, name)..."
              value={usersSearch}
              onChange={(e) => setUsersSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && loadUsers()}
              style={{ flex: 1, padding: '10px 14px', border: '1px solid #ddd', borderRadius: 8, fontSize: 14 }}
            />
            <button onClick={loadUsers} style={{ ...btnSmall, padding: '10px 20px', background: '#4338ca', color: '#fff', border: 'none' }}>Search</button>
            <span style={{ color: '#64748b', fontSize: 13 }}>{usersTotal} total</span>
          </div>

          {usersLoading ? <p>Loading...</p> : (
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Email</th>
                    <th style={thStyle}>Name</th>
                    <th style={thStyle}>Role</th>
                    <th style={thStyle}>Band</th>
                    <th style={thStyle}>Tier</th>
                    <th style={thStyle}>Status</th>
                    <th style={thStyle}>Last Login</th>
                    <th style={thStyle}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td style={tdStyle}>{u.email}</td>
                      <td style={tdStyle}>{u.first_name} {u.last_name}</td>
                      <td style={tdStyle}>
                        <select
                          value={u.role}
                          onChange={(e) => changeUserRole(u.id, e.target.value)}
                          style={{ padding: '2px 6px', borderRadius: 4, border: '1px solid #ddd', fontSize: 12 }}
                        >
                          <option value="student">Student</option>
                          <option value="trainer">Trainer</option>
                          <option value="admin">Admin</option>
                          <option value="demo">Demo</option>
                        </select>
                      </td>
                      <td style={tdStyle}>{u.nhs_band || '-'}</td>
                      <td style={tdStyle}>
                        <span style={{
                          padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 600,
                          background: u.subscription_tier === 'enterprise' ? '#dbeafe' : u.subscription_tier === 'professional' ? '#fae8ff' : '#f1f5f9',
                          color: u.subscription_tier === 'enterprise' ? '#1e40af' : u.subscription_tier === 'professional' ? '#7e22ce' : '#64748b',
                        }}>
                          {u.subscription_tier}
                        </span>
                      </td>
                      <td style={tdStyle}>
                        <span style={{
                          width: 8, height: 8, borderRadius: '50%', display: 'inline-block', marginRight: 6,
                          background: u.is_active ? '#10b981' : '#ef4444',
                        }} />
                        {u.is_active ? 'Active' : 'Inactive'}
                      </td>
                      <td style={{ ...tdStyle, fontSize: 12, color: '#94a3b8' }}>
                        {u.last_login ? new Date(u.last_login).toLocaleDateString() : 'Never'}
                      </td>
                      <td style={tdStyle}>
                        <button
                          onClick={() => toggleUserActive(u.id, u.is_active)}
                          style={{
                            ...btnSmall,
                            color: u.is_active ? '#ef4444' : '#10b981',
                            borderColor: u.is_active ? '#fecaca' : '#a7f3d0',
                          }}
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    </tr>
                  ))}
                  {users.length === 0 && (
                    <tr><td colSpan={8} style={{ ...tdStyle, textAlign: 'center', color: '#94a3b8' }}>No users found</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ============ QUESTIONS TAB ============ */}
      {tab === 'questions' && (
        <div>
          <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Search questions..."
              value={questionsSearch}
              onChange={(e) => setQuestionsSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && loadQuestions()}
              style={{ flex: 1, padding: '10px 14px', border: '1px solid #ddd', borderRadius: 8, fontSize: 14 }}
            />
            <button onClick={loadQuestions} style={{ ...btnSmall, padding: '10px 20px', background: '#4338ca', color: '#fff', border: 'none' }}>Search</button>
            <span style={{ color: '#64748b', fontSize: 13 }}>{questionsTotal} total</span>
          </div>

          {questionsLoading ? <p>Loading...</p> : (
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>ID</th>
                    <th style={thStyle}>Title</th>
                    <th style={thStyle}>Type</th>
                    <th style={thStyle}>Difficulty</th>
                    <th style={thStyle}>Band</th>
                    <th style={thStyle}>Specialty</th>
                    <th style={thStyle}>Active</th>
                  </tr>
                </thead>
                <tbody>
                  {questions.map((q) => (
                    <tr key={q.id}>
                      <td style={tdStyle}>{q.id}</td>
                      <td style={{ ...tdStyle, maxWidth: 300 }}>{q.title}</td>
                      <td style={tdStyle}>{q.question_type}</td>
                      <td style={tdStyle}>
                        <span style={{
                          padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 600,
                          background: q.difficulty_level === 'expert' ? '#fef2f2' : q.difficulty_level === 'advanced' ? '#fefce8' : '#f0fdf4',
                          color: q.difficulty_level === 'expert' ? '#991b1b' : q.difficulty_level === 'advanced' ? '#854d0e' : '#166534',
                        }}>
                          {q.difficulty_level}
                        </span>
                      </td>
                      <td style={tdStyle}>{q.nhs_band || '-'}</td>
                      <td style={tdStyle}>{q.specialty || '-'}</td>
                      <td style={tdStyle}>{q.is_active ? 'Yes' : 'No'}</td>
                    </tr>
                  ))}
                  {questions.length === 0 && (
                    <tr><td colSpan={7} style={{ ...tdStyle, textAlign: 'center', color: '#94a3b8' }}>No questions found</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ============ AUDIT TAB ============ */}
      {tab === 'audit' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3 style={{ margin: 0, fontSize: 16, color: '#334155' }}>Security Audit Log</h3>
            <button onClick={loadAudit} style={{ ...btnSmall, background: '#4338ca', color: '#fff', border: 'none' }}>Refresh</button>
          </div>

          {auditLoading ? <p>Loading...</p> : (
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Timestamp</th>
                    <th style={thStyle}>Event</th>
                    <th style={thStyle}>Severity</th>
                    <th style={thStyle}>Source IP</th>
                    <th style={thStyle}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log, i) => (
                    <tr key={i}>
                      <td style={{ ...tdStyle, fontSize: 12, whiteSpace: 'nowrap' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td style={tdStyle}>{log.event_type}</td>
                      <td style={tdStyle}>
                        <span style={{
                          padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 600,
                          background: log.severity === 'HIGH' || log.severity === 'CRITICAL' ? '#fef2f2' : log.severity === 'MEDIUM' ? '#fefce8' : '#f0fdf4',
                          color: log.severity === 'HIGH' || log.severity === 'CRITICAL' ? '#991b1b' : log.severity === 'MEDIUM' ? '#854d0e' : '#166534',
                        }}>
                          {log.severity}
                        </span>
                      </td>
                      <td style={{ ...tdStyle, fontSize: 12, fontFamily: 'monospace' }}>{log.source_ip}</td>
                      <td style={{ ...tdStyle, fontSize: 12, maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {typeof log.details === 'object' ? JSON.stringify(log.details).substring(0, 100) : String(log.details || '').substring(0, 100)}
                      </td>
                    </tr>
                  ))}
                  {auditLogs.length === 0 && (
                    <tr><td colSpan={5} style={{ ...tdStyle, textAlign: 'center', color: '#94a3b8' }}>No audit entries</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ============ ANALYTICS TAB ============ */}
      {tab === 'analytics' && (
        <div>
          {/* Header: date range + export */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <DateRangeSelector value={analyticsDays} onChange={setAnalyticsDays} />
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                onClick={() => handleExportCSV('activity')}
                disabled={exportLoading}
                style={{ ...btnSmall, padding: '8px 14px', background: '#0d9488', color: '#fff', border: 'none' }}
              >
                Export Activity CSV
              </button>
              <button
                onClick={() => handleExportCSV('users')}
                disabled={exportLoading}
                style={{ ...btnSmall, padding: '8px 14px', background: '#7c3aed', color: '#fff', border: 'none' }}
              >
                Export Users CSV
              </button>
              <button
                onClick={() => handleExportCSV('performance')}
                disabled={exportLoading}
                style={{ ...btnSmall, padding: '8px 14px', background: '#4338ca', color: '#fff', border: 'none' }}
              >
                Export Performance CSV
              </button>
            </div>
          </div>

          {analyticsLoading ? <p>Loading analytics...</p> : (
            <>
              {/* KPI Cards */}
              {analyticsOverview?.kpis && (
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
                  <KPICard label="New Users" kpi={analyticsOverview.kpis.new_users} />
                  <KPICard label="Active Users" kpi={analyticsOverview.kpis.active_users} />
                  <KPICard label="Questions Answered" kpi={analyticsOverview.kpis.questions_answered} />
                  <KPICard label="Avg Accuracy" kpi={analyticsOverview.kpis.avg_accuracy_pct} suffix="%" />
                  <KPICard label="Training Sessions" kpi={analyticsOverview.kpis.training_sessions} />
                  <KPICard label="Avg Session Score" kpi={analyticsOverview.kpis.avg_session_score} suffix="%" />
                </div>
              )}

              {/* Line Chart: Activity over time */}
              {activityData.length > 0 && (
                <div style={{ marginBottom: 24 }}>
                  <ActivityLineChart data={activityData} />
                </div>
              )}

              {/* Bar Charts row */}
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
                {bandPerformance.length > 0 && (
                  <PerformanceBarChart
                    data={bandPerformance}
                    dataKey="accuracy_pct"
                    nameKey="band"
                    title="Performance by NHS Band"
                  />
                )}
                {specialtyPerformance.length > 0 && (
                  <PerformanceBarChart
                    data={specialtyPerformance}
                    dataKey="accuracy_pct"
                    nameKey="specialty"
                    title="Performance by Specialty"
                  />
                )}
              </div>

              {/* Pie Charts row */}
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
                {questionDistribution?.by_type && (
                  <DistributionPieChart
                    data={questionDistribution.by_type.map((d: any) => ({ name: d.type, value: d.count }))}
                    title="Questions by Type"
                  />
                )}
                {questionDistribution?.subscription_distribution && (
                  <DistributionPieChart
                    data={questionDistribution.subscription_distribution.map((d: any) => ({ name: d.tier, value: d.count }))}
                    title="Subscriptions by Tier"
                  />
                )}
              </div>

              {/* Difficulty stats table */}
              {questionDistribution?.by_difficulty && (
                <div style={{ ...cardStyle, marginBottom: 24 }}>
                  <h3 style={{ margin: '0 0 12px', fontSize: 16, color: '#334155' }}>Performance by Difficulty</h3>
                  <table style={tableStyle}>
                    <thead>
                      <tr>
                        <th style={thStyle}>Difficulty</th>
                        <th style={thStyle}>Questions</th>
                        <th style={thStyle}>Total Attempts</th>
                        <th style={thStyle}>Accuracy %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {questionDistribution.by_difficulty.map((d: any) => (
                        <tr key={d.difficulty}>
                          <td style={tdStyle}>
                            <span style={{
                              padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 600, textTransform: 'capitalize',
                              background: d.difficulty === 'expert' ? '#fef2f2' : d.difficulty === 'advanced' ? '#fefce8' : '#f0fdf4',
                              color: d.difficulty === 'expert' ? '#991b1b' : d.difficulty === 'advanced' ? '#854d0e' : '#166534',
                            }}>
                              {d.difficulty}
                            </span>
                          </td>
                          <td style={tdStyle}>{d.count}</td>
                          <td style={tdStyle}>{d.total_attempts.toLocaleString()}</td>
                          <td style={tdStyle}>
                            <span style={{ fontWeight: 700, color: d.accuracy_pct >= 70 ? '#10b981' : d.accuracy_pct >= 50 ? '#f59e0b' : '#ef4444' }}>
                              {d.accuracy_pct}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Empty state */}
              {!analyticsOverview && !analyticsLoading && (
                <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>
                  No analytics data available. Users need to answer questions to generate analytics.
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* ============ QUALITY TAB ============ */}
      {tab === 'quality' && (
        <div>
          {/* Actions */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <h3 style={{ margin: 0, fontSize: 16, color: '#334155' }}>Question Quality Management</h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                onClick={runDeduplication}
                disabled={dedupRunning}
                style={{ ...btnSmall, padding: '8px 16px', background: dedupRunning ? '#94a3b8' : '#ef4444', color: '#fff', border: 'none' }}
              >
                {dedupRunning ? 'Running...' : 'Remove Duplicates'}
              </button>
              <button
                onClick={() => runImproveBatch('generic', 10)}
                disabled={improveRunning}
                style={{ ...btnSmall, padding: '8px 16px', background: improveRunning ? '#94a3b8' : '#4338ca', color: '#fff', border: 'none' }}
              >
                {improveRunning ? 'Improving...' : 'AI Improve (10 generic)'}
              </button>
              <button
                onClick={() => runImproveBatch('short', 10)}
                disabled={improveRunning}
                style={{ ...btnSmall, padding: '8px 16px', background: improveRunning ? '#94a3b8' : '#0d9488', color: '#fff', border: 'none' }}
              >
                {improveRunning ? 'Improving...' : 'AI Improve (10 short)'}
              </button>
              <button onClick={loadQualityReport} style={{ ...btnSmall, padding: '8px 16px' }}>Refresh</button>
            </div>
          </div>

          {qualityLoading ? <p>Loading quality report...</p> : qualityReport && (
            <>
              {/* KPI Cards */}
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
                <div style={{ ...kpiStyle }}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: '#4338ca' }}>{qualityReport.total_active?.toLocaleString()}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Active Questions</div>
                </div>
                <div style={{ ...kpiStyle }}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: '#94a3b8' }}>{qualityReport.total_inactive?.toLocaleString()}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Inactive (deduped)</div>
                </div>
                <div style={{ ...kpiStyle }}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: '#ef4444' }}>{qualityReport.generic_answers?.toLocaleString()}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Generic Answers ({qualityReport.generic_pct}%)</div>
                </div>
                <div style={{ ...kpiStyle }}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: '#10b981' }}>{qualityReport.good_answers?.toLocaleString()}</div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Good Answers ({qualityReport.good_pct}%)</div>
                </div>
              </div>

              {/* Distribution */}
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
                <div style={{ ...cardStyle, flex: '1 1 300px' }}>
                  <h3 style={{ margin: '0 0 12px', fontSize: 16, color: '#334155' }}>By Band</h3>
                  {qualityReport.by_band?.map((b: any) => (
                    <div key={b.band} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <span style={{ fontSize: 13 }}>{b.band}</span>
                      <span style={{ fontWeight: 700, fontSize: 13 }}>{b.count}</span>
                    </div>
                  ))}
                </div>
                <div style={{ ...cardStyle, flex: '1 1 300px' }}>
                  <h3 style={{ margin: '0 0 12px', fontSize: 16, color: '#334155' }}>By Specialty</h3>
                  {qualityReport.by_specialty?.map((s: any) => (
                    <div key={s.specialty} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <span style={{ fontSize: 13, textTransform: 'capitalize' }}>{s.specialty}</span>
                      <span style={{ fontWeight: 700, fontSize: 13 }}>{s.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Generic samples */}
              {qualityReport.generic_samples?.length > 0 && (
                <div style={{ ...cardStyle }}>
                  <h3 style={{ margin: '0 0 12px', fontSize: 16, color: '#334155' }}>Sample Generic Answers (need improvement)</h3>
                  {qualityReport.generic_samples.map((q: any) => (
                    <div key={q.id} style={{ padding: '8px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                        <span style={{ fontSize: 12, color: '#94a3b8' }}>#{q.id}</span>
                        <span style={{ fontSize: 13, fontWeight: 600 }}>{q.title}</span>
                        <span style={{ padding: '1px 6px', borderRadius: 8, fontSize: 10, background: '#f1f5f9', color: '#64748b' }}>{q.band}</span>
                        <span style={{ padding: '1px 6px', borderRadius: 8, fontSize: 10, background: '#eff6ff', color: '#1e40af' }}>{q.specialty}</span>
                      </div>
                      <div style={{ fontSize: 12, color: '#ef4444', fontStyle: 'italic' }}>{q.answer_preview}</div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* ============ AI INSIGHTS TAB ============ */}
      {tab === 'ai-insights' && (
        <div>
          {/* Ollama Status + Actions */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{
                width: 10, height: 10, borderRadius: '50%', display: 'inline-block',
                background: ollamaHealth?.status === 'online' ? '#10b981'
                  : ollamaHealth?.status === 'disabled' ? '#94a3b8'
                  : '#ef4444',
              }} />
              <span style={{ fontSize: 14, color: '#334155' }}>
                Ollama: <strong>{ollamaHealth?.status || 'checking...'}</strong>
                {ollamaHealth?.target_model && ` (${ollamaHealth.target_model})`}
              </span>
              {ollamaHealth?.status === 'offline' && (
                <span style={{ fontSize: 12, color: '#94a3b8' }}>Run: ollama serve</span>
              )}
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                onClick={() => runAiAnalysis(7)}
                disabled={aiRunning || ollamaHealth?.status !== 'online'}
                style={{
                  ...btnSmall, padding: '8px 16px',
                  background: aiRunning ? '#94a3b8' : '#4338ca', color: '#fff', border: 'none',
                  opacity: (aiRunning || ollamaHealth?.status !== 'online') ? 0.6 : 1,
                }}
              >
                {aiRunning ? 'Running...' : 'Analyze Last 7 Days'}
              </button>
              <button
                onClick={() => runAiAnalysis(14)}
                disabled={aiRunning || ollamaHealth?.status !== 'online'}
                style={{
                  ...btnSmall, padding: '8px 16px',
                  background: aiRunning ? '#94a3b8' : '#0d9488', color: '#fff', border: 'none',
                  opacity: (aiRunning || ollamaHealth?.status !== 'online') ? 0.6 : 1,
                }}
              >
                {aiRunning ? 'Running...' : 'Analyze Last 14 Days'}
              </button>
              <button
                onClick={() => { loadOllamaHealth(); loadAiInsights(); }}
                style={{ ...btnSmall, padding: '8px 16px' }}
              >
                Refresh
              </button>
            </div>
          </div>

          {aiRunning && (
            <div style={{ background: '#eff6ff', border: '1px solid #3b82f6', padding: 12, borderRadius: 8, marginBottom: 16, color: '#1e40af', fontSize: 14 }}>
              AI analysis in progress... This may take 1-5 minutes depending on data volume and model speed.
            </div>
          )}

          {aiLoading ? <p>Loading insights...</p> : (
            <>
              {aiInsights.length === 0 && !aiLoading && (
                <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>
                  No AI insights generated yet. Click "Analyze" to generate the first report.
                </div>
              )}

              {aiInsights.map((insight) => (
                <div key={insight.id} style={{
                  background: '#f8fafc', borderRadius: 12, padding: 16, border: '1px solid #e2e8f0', marginBottom: 12,
                }}>
                  {/* Header */}
                  <div
                    style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                    onClick={() => setExpandedInsight(expandedInsight === insight.id ? null : insight.id)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{
                        padding: '3px 10px', borderRadius: 12, fontSize: 11, fontWeight: 600,
                        background: insight.status === 'completed' ? '#ecfdf5' : insight.status === 'failed' ? '#fef2f2' : '#eff6ff',
                        color: insight.status === 'completed' ? '#065f46' : insight.status === 'failed' ? '#991b1b' : '#1e40af',
                      }}>
                        {insight.status}
                      </span>
                      <span style={{ fontSize: 14, fontWeight: 600, color: '#334155' }}>
                        {insight.report_type.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}
                      </span>
                      <span style={{ fontSize: 12, color: '#94a3b8' }}>
                        {insight.generated_at ? new Date(insight.generated_at).toLocaleString() : ''}
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {insight.generation_time_seconds && (
                        <span style={{ fontSize: 11, color: '#94a3b8' }}>{insight.generation_time_seconds}s</span>
                      )}
                      <span style={{ fontSize: 12, color: '#64748b' }}>{expandedInsight === insight.id ? '\u25B2' : '\u25BC'}</span>
                    </div>
                  </div>

                  {/* Expanded content */}
                  {expandedInsight === insight.id && insight.status === 'completed' && (
                    <div style={{ marginTop: 16 }}>
                      {/* Summary */}
                      {insight.insights?.find((i: any) => i.category === 'summary' || i.finding) && (
                        <div style={{ background: '#fff', borderRadius: 8, padding: 12, marginBottom: 12, border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: '#334155', marginBottom: 6 }}>Summary</div>
                          {/* Try to find summary from raw insights */}
                        </div>
                      )}

                      {/* Insights */}
                      {insight.insights && insight.insights.length > 0 && (
                        <div style={{ marginBottom: 12 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: '#334155', marginBottom: 8 }}>Insights</div>
                          {insight.insights.map((ins: any, idx: number) => (
                            <div key={idx} style={{
                              display: 'flex', gap: 8, alignItems: 'flex-start', padding: '8px 12px',
                              background: '#fff', borderRadius: 6, marginBottom: 4, border: '1px solid #f1f5f9',
                            }}>
                              <span style={{
                                padding: '2px 6px', borderRadius: 8, fontSize: 10, fontWeight: 600, flexShrink: 0,
                                background: ins.severity === 'critical' ? '#fef2f2' : ins.severity === 'warning' ? '#fefce8' : '#f0fdf4',
                                color: ins.severity === 'critical' ? '#991b1b' : ins.severity === 'warning' ? '#854d0e' : '#166534',
                              }}>
                                {ins.severity}
                              </span>
                              <span style={{
                                padding: '2px 6px', borderRadius: 8, fontSize: 10, fontWeight: 600, flexShrink: 0,
                                background: '#eff6ff', color: '#1e40af',
                              }}>
                                {ins.category}
                              </span>
                              <span style={{ fontSize: 13, color: '#475569' }}>{ins.finding}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Recommendations */}
                      {insight.recommendations && insight.recommendations.length > 0 && (
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 600, color: '#334155', marginBottom: 8 }}>Recommendations</div>
                          {insight.recommendations.map((rec: any, idx: number) => (
                            <div key={idx} style={{
                              display: 'flex', gap: 8, alignItems: 'flex-start', padding: '8px 12px',
                              background: '#fff', borderRadius: 6, marginBottom: 4, border: '1px solid #f1f5f9',
                            }}>
                              <span style={{
                                padding: '2px 6px', borderRadius: 8, fontSize: 10, fontWeight: 700, flexShrink: 0,
                                background: rec.priority === 'high' ? '#fef2f2' : rec.priority === 'medium' ? '#fefce8' : '#f0fdf4',
                                color: rec.priority === 'high' ? '#991b1b' : rec.priority === 'medium' ? '#854d0e' : '#166534',
                              }}>
                                {rec.priority}
                              </span>
                              <span style={{
                                padding: '2px 6px', borderRadius: 8, fontSize: 10, fontWeight: 600, flexShrink: 0,
                                background: '#f5f3ff', color: '#6d28d9',
                              }}>
                                {rec.category}
                              </span>
                              <span style={{ fontSize: 13, color: '#475569' }}>{rec.action}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Error message */}
                  {expandedInsight === insight.id && insight.status === 'failed' && (
                    <div style={{ marginTop: 12, padding: 10, background: '#fef2f2', borderRadius: 6, fontSize: 13, color: '#991b1b' }}>
                      {insight.error_message || 'Unknown error'}
                    </div>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default function AdminPage() {
  return (
    <ProtectedRoute>
      <AdminContent />
    </ProtectedRoute>
  );
}
