import React, { useState, useEffect, FormEvent } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';

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

type Tab = 'overview' | 'users' | 'questions' | 'audit';

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
