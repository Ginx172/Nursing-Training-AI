import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';

interface DashboardData {
  total_events: number;
  high_risk_events: number;
  blocked_ips: number;
  suspicious_ips: number;
  recent_events: any[];
  risk_distribution: Record<string, number>;
  top_threats: any[];
}

function SecurityContent() {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');
  const [msg, setMsg] = useState('');
  const [blockIp, setBlockIp] = useState('');

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true); setErr('');
    try {
      const res = await api.get('/api/security-monitoring/dashboard');
      setDashboard(res.data);
    } catch (e: any) {
      // Endpoint may use different auth - try alternative
      try {
        const res = await api.get('/api/admin/audit-log', { params: { limit: 50 } });
        const logs = res.data.logs || res.data.entries || [];
        const riskDist: Record<string, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
        let highRisk = 0;
        for (const log of logs) {
          const sev = log.severity || 'LOW';
          riskDist[sev] = (riskDist[sev] || 0) + 1;
          if (sev === 'HIGH' || sev === 'CRITICAL') highRisk++;
        }
        setDashboard({
          total_events: logs.length,
          high_risk_events: highRisk,
          blocked_ips: 0,
          suspicious_ips: 0,
          recent_events: logs.slice(0, 20),
          risk_distribution: riskDist,
          top_threats: [],
        });
      } catch {
        setErr('Failed to load security data');
      }
    }
    setLoading(false);
  }

  async function handleBlockIp() {
    if (!blockIp.trim()) return;
    setMsg(''); setErr('');
    try {
      await api.post('/api/security-monitoring/ip/block', { ip: blockIp, action: 'block' });
      setMsg(`IP ${blockIp} blocked`);
      setBlockIp('');
      loadDashboard();
    } catch { setErr('Failed to block IP'); }
  }

  const cardStyle: React.CSSProperties = {
    background: '#f8fafc', borderRadius: 12, padding: 20,
    border: '1px solid #e2e8f0',
  };
  const kpiStyle: React.CSSProperties = {
    ...cardStyle, textAlign: 'center', flex: '1 1 150px', minWidth: 140,
  };
  const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', fontSize: 13 };
  const thStyle: React.CSSProperties = {
    textAlign: 'left', padding: '10px 8px', borderBottom: '2px solid #e2e8f0',
    color: '#64748b', fontWeight: 600, fontSize: 12, textTransform: 'uppercase',
  };
  const tdStyle: React.CSSProperties = { padding: '10px 8px', borderBottom: '1px solid #f1f5f9' };

  const sevColor = (sev: string) => {
    if (sev === 'CRITICAL' || sev === 'security') return { bg: '#fef2f2', color: '#991b1b' };
    if (sev === 'HIGH' || sev === 'critical') return { bg: '#fef2f2', color: '#991b1b' };
    if (sev === 'MEDIUM' || sev === 'warning') return { bg: '#fefce8', color: '#854d0e' };
    return { bg: '#f0fdf4', color: '#166534' };
  };

  const riskColors: Record<string, string> = {
    LOW: '#10b981', MEDIUM: '#f59e0b', HIGH: '#ef4444', CRITICAL: '#991b1b',
    info: '#10b981', warning: '#f59e0b', critical: '#ef4444', security: '#991b1b',
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 16px', fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      <Head><title>Security Dashboard - Nursing Training AI</title></Head>

      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 0', borderBottom: '1px solid #e2e8f0', marginBottom: 20 }}>
        <span style={{ fontWeight: 'bold', fontSize: 18, color: '#dc2626' }}>Security Dashboard</span>
        <div style={{ display: 'flex', gap: 12 }}>
          <Link href="/admin" style={{ padding: '8px 16px', border: '1px solid #4338ca', color: '#4338ca', borderRadius: 8, textDecoration: 'none', fontSize: 14 }}>Admin</Link>
          <Link href="/dashboard" style={{ padding: '8px 16px', border: '1px solid #ddd', color: '#666', borderRadius: 8, textDecoration: 'none', fontSize: 14 }}>Dashboard</Link>
        </div>
      </nav>

      {msg && <div style={{ background: '#ecfdf5', border: '1px solid #10b981', padding: 10, borderRadius: 8, marginBottom: 12, color: '#065f46', fontSize: 14 }}>{msg}</div>}
      {err && <div style={{ background: '#fef2f2', border: '1px solid #ef4444', padding: 10, borderRadius: 8, marginBottom: 12, color: '#991b1b', fontSize: 14 }}>{err}</div>}

      {loading ? <p>Loading security data...</p> : dashboard && (
        <>
          {/* KPI Cards */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
            <div style={kpiStyle}>
              <div style={{ fontSize: 32, fontWeight: 800, color: '#4338ca' }}>{dashboard.total_events}</div>
              <div style={{ color: '#64748b', fontSize: 13 }}>Total Events</div>
            </div>
            <div style={kpiStyle}>
              <div style={{ fontSize: 32, fontWeight: 800, color: '#ef4444' }}>{dashboard.high_risk_events}</div>
              <div style={{ color: '#64748b', fontSize: 13 }}>High Risk</div>
            </div>
            <div style={kpiStyle}>
              <div style={{ fontSize: 32, fontWeight: 800, color: '#dc2626' }}>{dashboard.blocked_ips}</div>
              <div style={{ color: '#64748b', fontSize: 13 }}>Blocked IPs</div>
            </div>
            <div style={kpiStyle}>
              <div style={{ fontSize: 32, fontWeight: 800, color: '#f59e0b' }}>{dashboard.suspicious_ips}</div>
              <div style={{ color: '#64748b', fontSize: 13 }}>Suspicious IPs</div>
            </div>
          </div>

          {/* Risk Distribution + IP Management */}
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
            {/* Risk Distribution */}
            <div style={{ ...cardStyle, flex: '1 1 400px' }}>
              <h3 style={{ margin: '0 0 16px', fontSize: 16, color: '#334155' }}>Risk Distribution</h3>
              {Object.entries(dashboard.risk_distribution).map(([level, count]) => (
                <div key={level} style={{ marginBottom: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: riskColors[level] || '#64748b' }}>{level}</span>
                    <span style={{ fontSize: 13, fontWeight: 700 }}>{count as number}</span>
                  </div>
                  <div style={{ background: '#e2e8f0', borderRadius: 6, height: 8, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%', borderRadius: 6,
                      width: `${Math.min(100, ((count as number) / Math.max(dashboard.total_events, 1)) * 100)}%`,
                      background: riskColors[level] || '#94a3b8',
                    }} />
                  </div>
                </div>
              ))}
            </div>

            {/* IP Management */}
            <div style={{ ...cardStyle, flex: '1 1 300px' }}>
              <h3 style={{ margin: '0 0 16px', fontSize: 16, color: '#334155' }}>IP Management</h3>
              <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                <input
                  type="text"
                  placeholder="IP address to block..."
                  value={blockIp}
                  onChange={(e) => setBlockIp(e.target.value)}
                  style={{ flex: 1, padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6, fontSize: 13 }}
                />
                <button
                  onClick={handleBlockIp}
                  style={{ padding: '8px 16px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: 6, fontSize: 13, cursor: 'pointer' }}
                >
                  Block
                </button>
              </div>
              {/* Top Threats */}
              {dashboard.top_threats.length > 0 && (
                <>
                  <h4 style={{ margin: '16px 0 8px', fontSize: 14, color: '#475569' }}>Top Threats</h4>
                  {dashboard.top_threats.map((t, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <span style={{ fontSize: 12, color: '#475569' }}>{t.threat_type}</span>
                      <span style={{ fontSize: 12, fontWeight: 700, color: '#ef4444' }}>{t.count}</span>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>

          {/* Recent Events Table */}
          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <h3 style={{ margin: 0, fontSize: 16, color: '#334155' }}>Recent Security Events</h3>
              <button
                onClick={loadDashboard}
                style={{ padding: '6px 14px', border: '1px solid #ddd', borderRadius: 6, fontSize: 13, cursor: 'pointer', background: '#fff' }}
              >
                Refresh
              </button>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Time</th>
                    <th style={thStyle}>Event</th>
                    <th style={thStyle}>Severity</th>
                    <th style={thStyle}>Source IP</th>
                    <th style={thStyle}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboard.recent_events.map((ev, i) => {
                    const sev = sevColor(ev.severity || ev.event_type || '');
                    return (
                      <tr key={i}>
                        <td style={{ ...tdStyle, fontSize: 12, whiteSpace: 'nowrap' }}>
                          {ev.timestamp ? new Date(ev.timestamp).toLocaleString() : '-'}
                        </td>
                        <td style={tdStyle}>{ev.event_type || ev.action || '-'}</td>
                        <td style={tdStyle}>
                          <span style={{
                            padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 600,
                            background: sev.bg, color: sev.color,
                          }}>
                            {ev.severity || '-'}
                          </span>
                        </td>
                        <td style={{ ...tdStyle, fontSize: 12, fontFamily: 'monospace' }}>{ev.source_ip || '-'}</td>
                        <td style={{ ...tdStyle, fontSize: 12, maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {typeof ev.details === 'object' ? JSON.stringify(ev.details).substring(0, 80) : String(ev.details || '').substring(0, 80)}
                        </td>
                      </tr>
                    );
                  })}
                  {dashboard.recent_events.length === 0 && (
                    <tr><td colSpan={5} style={{ ...tdStyle, textAlign: 'center', color: '#94a3b8' }}>No security events recorded</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default function SecurityDashboardPage() {
  return (
    <ProtectedRoute>
      <SecurityContent />
    </ProtectedRoute>
  );
}
