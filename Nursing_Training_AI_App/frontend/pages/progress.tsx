import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';

interface LearningProfile {
  exists: boolean;
  message?: string;
  baseline?: {
    established: boolean;
    accuracy_pct: number | null;
    established_at: string | null;
    questions_needed: number;
  };
  current?: {
    accuracy_pct: number;
    total_questions: number;
    total_correct: number;
  };
  improvement: number | null;
  trend: string;
  learning_velocity: number;
  strengths?: { specialty: string | null; competency: string | null };
  weaknesses?: { specialty: string | null; competency: string | null };
  specialty_scores: Record<string, number>;
  competency_scores: Record<string, number>;
  recommendations: any[];
}

interface TimelinePoint {
  week: string;
  questions: number;
  correct: number;
  accuracy_pct: number;
}

function ProgressContent() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<LearningProfile | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');

  useEffect(() => {
    if (user) loadAll();
  }, [user]);

  async function loadAll() {
    setLoading(true);
    setErr('');
    try {
      const [profileRes, timelineRes, recsRes] = await Promise.all([
        api.get('/api/learning-tracker/profile'),
        api.get('/api/learning-tracker/timeline', { params: { days: 90 } }),
        api.get('/api/learning-tracker/recommendations'),
      ]);
      setProfile(profileRes.data);
      setTimeline(timelineRes.data.data || []);
      setRecommendations(recsRes.data.recommendations || []);
    } catch {
      setErr('Failed to load learning data');
    }
    setLoading(false);
  }

  const cardStyle: React.CSSProperties = {
    background: '#f8fafc', borderRadius: 12, padding: 20,
    border: '1px solid #e2e8f0',
  };

  const kpiStyle: React.CSSProperties = {
    ...cardStyle, textAlign: 'center', flex: '1 1 150px', minWidth: 140,
  };

  const trendColor = profile?.trend === 'improving' ? '#10b981'
    : profile?.trend === 'declining' ? '#ef4444' : '#94a3b8';
  const trendArrow = profile?.trend === 'improving' ? '\u25B2'
    : profile?.trend === 'declining' ? '\u25BC' : '\u25CF';

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 16px', fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      <Head><title>My Progress - Nursing Training AI</title></Head>

      {/* Nav */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 0', borderBottom: '1px solid #e2e8f0', marginBottom: 20 }}>
        <span style={{ fontWeight: 'bold', fontSize: 18, color: '#4338ca' }}>My Learning Progress</span>
        <div style={{ display: 'flex', gap: 12 }}>
          <Link href="/dashboard" style={{ padding: '8px 16px', border: '1px solid #4338ca', color: '#4338ca', borderRadius: 8, textDecoration: 'none', fontSize: 14 }}>Dashboard</Link>
          <Link href="/admin" style={{ padding: '8px 16px', border: '1px solid #ddd', color: '#666', borderRadius: 8, textDecoration: 'none', fontSize: 14 }}>Admin</Link>
        </div>
      </nav>

      {err && <div style={{ background: '#fef2f2', border: '1px solid #ef4444', padding: 10, borderRadius: 8, marginBottom: 12, color: '#991b1b', fontSize: 14 }}>{err}</div>}

      {loading ? <p>Loading your learning profile...</p> : (
        <>
          {/* Baseline progress bar */}
          {profile?.exists && profile.baseline && !profile.baseline.established && (
            <div style={{ ...cardStyle, marginBottom: 20, background: '#eff6ff', borderColor: '#3b82f6' }}>
              <div style={{ fontSize: 15, fontWeight: 600, color: '#1e40af', marginBottom: 8 }}>
                Building Your Baseline
              </div>
              <div style={{ fontSize: 13, color: '#1e40af', marginBottom: 10 }}>
                Answer {profile.baseline.questions_needed} more questions to establish your baseline level.
              </div>
              <div style={{ background: '#dbeafe', borderRadius: 8, height: 12, overflow: 'hidden' }}>
                <div style={{
                  background: '#3b82f6', height: '100%', borderRadius: 8,
                  width: `${((20 - profile.baseline.questions_needed) / 20) * 100}%`,
                  transition: 'width 0.3s',
                }} />
              </div>
              <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>
                {20 - profile.baseline.questions_needed} / 20 questions completed
              </div>
            </div>
          )}

          {/* KPI Cards */}
          {profile?.exists && (
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
              <div style={kpiStyle}>
                <div style={{ fontSize: 28, fontWeight: 800, color: '#4338ca' }}>
                  {profile.current?.accuracy_pct || 0}%
                </div>
                <div style={{ color: '#64748b', fontSize: 13 }}>Current Accuracy</div>
                {profile.baseline?.established && (
                  <div style={{ fontSize: 12, color: trendColor, fontWeight: 600 }}>
                    {profile.improvement !== null && profile.improvement > 0 ? '+' : ''}{profile.improvement}% from baseline
                  </div>
                )}
              </div>

              <div style={kpiStyle}>
                <div style={{ fontSize: 28, fontWeight: 800, color: trendColor }}>
                  {trendArrow}
                </div>
                <div style={{ color: '#64748b', fontSize: 13 }}>Trend</div>
                <div style={{ fontSize: 12, color: trendColor, fontWeight: 600, textTransform: 'capitalize' }}>
                  {profile.trend}
                </div>
              </div>

              <div style={kpiStyle}>
                <div style={{ fontSize: 28, fontWeight: 800, color: '#7c3aed' }}>
                  {profile.current?.total_questions || 0}
                </div>
                <div style={{ color: '#64748b', fontSize: 13 }}>Questions Answered</div>
              </div>

              <div style={kpiStyle}>
                <div style={{ fontSize: 28, fontWeight: 800, color: '#0d9488' }}>
                  {profile.learning_velocity || 0}
                </div>
                <div style={{ color: '#64748b', fontSize: 13 }}>Questions / Day</div>
              </div>

              {profile.baseline?.established && (
                <div style={kpiStyle}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: '#94a3b8' }}>
                    {profile.baseline.accuracy_pct}%
                  </div>
                  <div style={{ color: '#64748b', fontSize: 13 }}>Baseline</div>
                </div>
              )}
            </div>
          )}

          {/* Strengths & Weaknesses */}
          {profile?.exists && (profile.strengths?.specialty || profile.weaknesses?.specialty) && (
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
              <div style={{ ...cardStyle, flex: '1 1 300px' }}>
                <h3 style={{ margin: '0 0 12px', fontSize: 16, color: '#10b981' }}>Strengths</h3>
                {profile.strengths?.specialty && (
                  <div style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
                    <span style={{ padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 600, background: '#ecfdf5', color: '#065f46' }}>
                      {profile.strengths.specialty}
                    </span>
                    {profile.specialty_scores[profile.strengths.specialty] !== undefined && (
                      <span style={{ fontSize: 12, color: '#10b981', fontWeight: 600 }}>
                        {profile.specialty_scores[profile.strengths.specialty]}%
                      </span>
                    )}
                  </div>
                )}
                {profile.strengths?.competency && (
                  <div>
                    <span style={{ padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 600, background: '#f0fdf4', color: '#166534' }}>
                      {profile.strengths.competency}
                    </span>
                  </div>
                )}
              </div>

              <div style={{ ...cardStyle, flex: '1 1 300px' }}>
                <h3 style={{ margin: '0 0 12px', fontSize: 16, color: '#ef4444' }}>Areas to Improve</h3>
                {profile.weaknesses?.specialty && (
                  <div style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
                    <span style={{ padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 600, background: '#fef2f2', color: '#991b1b' }}>
                      {profile.weaknesses.specialty}
                    </span>
                    {profile.specialty_scores[profile.weaknesses.specialty] !== undefined && (
                      <span style={{ fontSize: 12, color: '#ef4444', fontWeight: 600 }}>
                        {profile.specialty_scores[profile.weaknesses.specialty]}%
                      </span>
                    )}
                  </div>
                )}
                {profile.weaknesses?.competency && (
                  <div>
                    <span style={{ padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 600, background: '#fef2f2', color: '#991b1b' }}>
                      {profile.weaknesses.competency}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Specialty Scores Bar */}
          {profile?.exists && profile.specialty_scores && Object.keys(profile.specialty_scores).length > 0 && (
            <div style={{ ...cardStyle, marginBottom: 24 }}>
              <h3 style={{ margin: '0 0 16px', fontSize: 16, color: '#334155' }}>Performance by Specialty</h3>
              {Object.entries(profile.specialty_scores)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .map(([spec, score]) => (
                <div key={spec} style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 13, color: '#475569', textTransform: 'capitalize' }}>{spec}</span>
                    <span style={{ fontSize: 13, fontWeight: 700, color: (score as number) >= 70 ? '#10b981' : (score as number) >= 50 ? '#f59e0b' : '#ef4444' }}>
                      {score as number}%
                    </span>
                  </div>
                  <div style={{ background: '#e2e8f0', borderRadius: 6, height: 8, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%', borderRadius: 6, transition: 'width 0.3s',
                      width: `${score}%`,
                      background: (score as number) >= 70 ? '#10b981' : (score as number) >= 50 ? '#f59e0b' : '#ef4444',
                    }} />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Timeline Chart */}
          {timeline.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <div style={{ ...cardStyle }}>
                <h3 style={{ margin: '0 0 16px', fontSize: 16, color: '#334155' }}>Weekly Progress</h3>
                <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                  {timeline.map((t) => (
                    <div key={t.week} style={{ textAlign: 'center', minWidth: 70 }}>
                      <div style={{ fontSize: 18, fontWeight: 700, color: t.accuracy_pct >= 70 ? '#10b981' : t.accuracy_pct >= 50 ? '#f59e0b' : '#ef4444' }}>
                        {t.accuracy_pct}%
                      </div>
                      <div style={{ fontSize: 11, color: '#94a3b8' }}>{t.questions} Q</div>
                      <div style={{ fontSize: 10, color: '#cbd5e1' }}>{t.week?.slice(5)}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div style={{ ...cardStyle, marginBottom: 24 }}>
              <h3 style={{ margin: '0 0 16px', fontSize: 16, color: '#334155' }}>Personalized Recommendations</h3>
              {recommendations.map((rec, idx) => (
                <div key={idx} style={{
                  display: 'flex', gap: 8, alignItems: 'flex-start', padding: '10px 12px',
                  background: '#fff', borderRadius: 8, marginBottom: 6, border: '1px solid #f1f5f9',
                }}>
                  <span style={{
                    padding: '2px 8px', borderRadius: 8, fontSize: 10, fontWeight: 700, flexShrink: 0,
                    background: rec.priority === 'high' ? '#fef2f2' : rec.priority === 'medium' ? '#fefce8' : '#f0fdf4',
                    color: rec.priority === 'high' ? '#991b1b' : rec.priority === 'medium' ? '#854d0e' : '#166534',
                  }}>
                    {rec.priority}
                  </span>
                  <span style={{
                    padding: '2px 8px', borderRadius: 8, fontSize: 10, fontWeight: 600, flexShrink: 0,
                    background: '#eff6ff', color: '#1e40af',
                  }}>
                    {rec.category}
                  </span>
                  <span style={{ fontSize: 13, color: '#475569' }}>{rec.action}</span>
                </div>
              ))}
            </div>
          )}

          {/* Empty state */}
          {!profile?.exists && (
            <div style={{ textAlign: 'center', padding: 60, color: '#94a3b8' }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>?</div>
              <div style={{ fontSize: 16, marginBottom: 8 }}>No learning data yet</div>
              <div style={{ fontSize: 14 }}>Start answering questions to build your personalized learning profile.</div>
              <Link href="/dashboard" style={{ display: 'inline-block', marginTop: 16, padding: '10px 24px', background: '#4338ca', color: '#fff', borderRadius: 8, textDecoration: 'none' }}>
                Start Learning
              </Link>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function ProgressPage() {
  return (
    <ProtectedRoute>
      <ProgressContent />
    </ProtectedRoute>
  );
}
