import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import ProtectedRoute from '../components/ProtectedRoute';
import api from '../lib/api';
import {
  Clock, Trophy, Target, ArrowLeft, ChevronDown, ChevronUp, BarChart3, Loader2,
} from 'lucide-react';

interface Session {
  id: number;
  session_name: string;
  nhs_band: string;
  specialization: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  duration_minutes: number;
  started_at: string;
  completed_at: string | null;
  is_completed: boolean;
  is_demo: boolean;
}

interface Summary {
  total_sessions: number;
  completed_sessions: number;
  average_score: number;
  total_answers: number;
  correct_answers: number;
  accuracy: number;
}

function HistoryContent() {
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [sessionDetail, setSessionDetail] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sessionsRes, summaryRes] = await Promise.all([
          api.get('/api/training/sessions?limit=50'),
          api.get('/api/training/summary'),
        ]);
        setSessions(sessionsRes.data.sessions || []);
        setSummary(summaryRes.data.summary || null);
      } catch {
        // Silently handle - show empty state
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const toggleSession = async (sessionId: number) => {
    if (expandedId === sessionId) {
      setExpandedId(null);
      setSessionDetail(null);
      return;
    }
    setExpandedId(sessionId);
    setDetailLoading(true);
    try {
      const res = await api.get(`/api/training/sessions/${sessionId}`);
      setSessionDetail(res.data);
    } catch {
      setSessionDetail(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <>
      <Head>
        <title>History - Nursing Training AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Top bar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-5xl mx-auto flex items-center gap-4">
            <button onClick={() => router.push('/dashboard')} className="text-gray-400 hover:text-gray-600">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-bold text-gray-900">Training History</h1>
          </div>
        </div>

        <div className="max-w-5xl mx-auto px-6 py-8">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
          ) : (
            <>
              {/* Summary cards */}
              {summary && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  <div className="bg-white rounded-xl p-4 border border-gray-200">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
                      <BarChart3 className="w-4 h-4" />
                      Sessions
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{summary.completed_sessions}</p>
                  </div>
                  <div className="bg-white rounded-xl p-4 border border-gray-200">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
                      <Target className="w-4 h-4" />
                      Avg Score
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{summary.average_score}%</p>
                  </div>
                  <div className="bg-white rounded-xl p-4 border border-gray-200">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
                      <Trophy className="w-4 h-4" />
                      Accuracy
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{summary.accuracy}%</p>
                  </div>
                  <div className="bg-white rounded-xl p-4 border border-gray-200">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
                      <Clock className="w-4 h-4" />
                      Questions
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{summary.total_answers}</p>
                  </div>
                </div>
              )}

              {/* Sessions list */}
              {sessions.length === 0 ? (
                <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                  <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">No Training Sessions Yet</h2>
                  <p className="text-gray-500 mb-6">Complete an interview practice to see your results here.</p>
                  <button
                    onClick={() => router.push('/interview')}
                    className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition"
                  >
                    Start Interview
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.map((s) => (
                    <div key={s.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                      <button
                        onClick={() => toggleSession(s.id)}
                        className="w-full px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition"
                      >
                        <div className="flex items-center gap-4">
                          <div className={`px-3 py-1.5 rounded-lg text-sm font-bold ${scoreColor(s.score_percentage || 0)}`}>
                            {s.score_percentage != null ? `${s.score_percentage}%` : '--'}
                          </div>
                          <div className="text-left">
                            <p className="font-medium text-gray-900">
                              {s.specialization?.toUpperCase() || 'General'} - {s.nhs_band?.replace('_', ' ').toUpperCase() || 'N/A'}
                            </p>
                            <p className="text-sm text-gray-500">
                              {s.started_at ? formatDate(s.started_at) : 'N/A'}
                              {s.total_questions ? ` \u00b7 ${s.total_questions} questions` : ''}
                              {s.duration_minutes ? ` \u00b7 ${s.duration_minutes} min` : ''}
                              {s.is_demo && <span className="ml-2 text-xs bg-gray-100 px-2 py-0.5 rounded">DEMO</span>}
                            </p>
                          </div>
                        </div>
                        {expandedId === s.id ? (
                          <ChevronUp className="w-5 h-5 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-400" />
                        )}
                      </button>

                      {/* Expanded detail */}
                      {expandedId === s.id && (
                        <div className="px-5 pb-5 border-t border-gray-100">
                          {detailLoading ? (
                            <div className="flex justify-center py-6">
                              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                            </div>
                          ) : sessionDetail?.answers?.length > 0 ? (
                            <div className="mt-4 space-y-3">
                              {sessionDetail.answers.map((a: any, idx: number) => (
                                <div key={a.id} className="p-3 bg-gray-50 rounded-lg">
                                  <div className="flex items-start justify-between mb-1">
                                    <p className="text-sm font-medium text-gray-700">Question {idx + 1}</p>
                                    <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                                      a.is_correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                    }`}>
                                      {a.is_correct ? 'Correct' : 'Incorrect'}
                                    </span>
                                  </div>
                                  {a.user_answer && (
                                    <p className="text-sm text-gray-600 mb-1">
                                      <span className="font-medium">Your answer:</span> {a.user_answer}
                                    </p>
                                  )}
                                  {a.ai_feedback && (
                                    <p className="text-sm text-gray-500 italic">{a.ai_feedback}</p>
                                  )}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-gray-400 py-4 text-center">No detailed answers available for this session.</p>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}

export default function HistoryPage() {
  return (
    <ProtectedRoute>
      <HistoryContent />
    </ProtectedRoute>
  );
}
