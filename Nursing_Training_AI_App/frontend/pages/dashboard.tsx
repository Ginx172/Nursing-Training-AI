import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import SystemHealth from '../components/SystemHealth';
import VideoAnalysis from '../components/VideoAnalysis';
import StudyZone from '../components/StudyZone';
import KnowledgeGraph from '../components/KnowledgeGraph';
import InterviewMode from '../components/InterviewMode';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard,
    BookOpen,
    MessageSquare,
    Users,
    Mic,
    Activity,
    Trophy,
    Calendar,
    Settings,
    LogOut,
    Bell,
    Search,
    Zap,
    ChevronRight,
} from 'lucide-react';

export default function Dashboard() {
    const { user, logout } = useAuth();
    const router = useRouter();
    const [greeting, setGreeting] = useState('Good Morning');
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        const hour = new Date().getHours();
        if (hour >= 12 && hour < 17) setGreeting('Good Afternoon');
        else if (hour >= 17) setGreeting('Good Evening');
    }, []);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const { default: api } = await import('../lib/api');
                const res = await api.get('/api/dashboard/stats');
                setStats(res.data);
            } catch {
                // Stats optional - dashboard functioneaza si fara
            }
        };
        fetchStats();
    }, []);

    const handleLogout = () => {
        logout();
        router.push('/login');
    };

    const displayName = user ? `${user.first_name} ${user.last_name}` : 'User';

    return (
        <ProtectedRoute>
        <div className="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-900">
            <Head>
                <title>Dashboard | Nursing Training AI</title>
            </Head>

            {/* Premium Sidebar */}
            <div className="fixed inset-y-0 left-0 w-72 bg-white/80 backdrop-blur-xl border-r border-slate-200/60 z-50 hidden xl:flex flex-col shadow-[4px_0_24px_-12px_rgba(0,0,0,0.05)]">
                <div className="p-8">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
                            <Activity className="text-white h-6 w-6" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-900 to-slate-800 bg-clip-text text-transparent">
                                NursingAI
                            </h1>
                            <p className="text-[10px] text-slate-400 font-bold tracking-[0.2em] uppercase">Enterprise</p>
                        </div>
                    </div>

                    <div className="space-y-1">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 px-4">Menu</p>
                        <NavItem icon={<LayoutDashboard />} label="Dashboard" active />
                        <NavItem icon={<BookOpen />} label="Knowledge Base" />
                        <Link href="/interview" className="flex items-center gap-3 px-4 py-3.5 rounded-xl font-medium transition-all duration-200 group text-slate-500 hover:text-slate-800 hover:bg-slate-50">
                            <span className="text-slate-400 group-hover:text-slate-600 transition-colors">
                                <Mic size={20} />
                            </span>
                            Interview Practice
                        </Link>
                        <NavItem icon={<MessageSquare />} label="Question Bank" />
                        <NavItem icon={<Users />} label="Students" />
                    </div>
                </div>

                <div className="mt-auto p-6 border-t border-slate-100">
                    <button onClick={handleLogout} className="flex items-center gap-3 w-full px-4 py-3 text-slate-500 hover:text-slate-800 hover:bg-slate-50 rounded-xl transition-all duration-200 font-medium">
                        <LogOut className="w-5 h-5" />
                        Sign Out
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <main className="xl:ml-72 min-h-screen">
                {/* Top Navigation Bar */}
                <header className="sticky top-0 z-40 bg-white/70 backdrop-blur-md border-b border-white/50 px-8 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-4 text-slate-400">
                        <Search className="w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Type to search..."
                            className="bg-transparent border-none focus:ring-0 text-sm w-64 text-slate-800 placeholder:text-slate-400"
                        />
                    </div>

                    <div className="flex items-center gap-6">
                        <button className="relative text-slate-400 hover:text-indigo-600 transition">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
                        </button>
                        <div className="h-8 w-px bg-slate-200"></div>
                        <div className="flex items-center gap-3">
                            <div className="text-right hidden sm:block">
                                <p className="text-sm font-bold text-slate-700">{displayName}</p>
                                <p className="text-xs text-slate-500">Clinical Supervisor</p>
                            </div>
                            <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-indigo-100 to-purple-100 border-2 border-white shadow-sm flex items-center justify-center text-indigo-700 font-bold">
                                SJ
                            </div>
                        </div>
                    </div>
                </header>

                <div className="p-6 md:p-10 max-w-[1920px] mx-auto space-y-10">
                    {/* Welcome Section */}
                    <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-indigo-600 to-violet-600 rounded-3xl p-8 md:p-12 shadow-2xl shadow-indigo-200 text-white">
                        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
                        <div className="absolute bottom-0 left-0 w-64 h-64 bg-black/10 rounded-full blur-2xl translate-y-1/2 -translate-x-1/2"></div>

                        <div className="relative z-10 max-w-2xl">
                            <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-medium mb-4 border border-white/20">
                                <Zap className="w-3 h-3 text-yellow-300" />
                                <span>AI Systems Operational</span>
                            </div>
                            <h2 className="text-3xl md:text-4xl font-bold mb-4 leading-tight">
                                {greeting}, {user?.first_name || 'there'}! <br />
                                <span className="text-indigo-200">Ready to train the next generation?</span>
                            </h2>
                            <p className="text-indigo-100 text-lg mb-8 max-w-xl leading-relaxed">
                                {stats?.platform?.sessions_today
                                    ? `${stats.platform.sessions_today} training sessions completed today.`
                                    : 'Your training platform is ready.'}
                                {' '}Start a new session to improve your clinical skills.
                            </p>
                            <div className="flex flex-wrap gap-4">
                                <button className="bg-white text-indigo-700 px-6 py-3 rounded-xl font-bold shadow-lg hover:shadow-xl hover:bg-slate-50 transition transform hover:-translate-y-0.5 active:translate-y-0">
                                    Review Flagged Videos
                                </button>
                                <button className="bg-indigo-700/50 backdrop-blur-md border border-white/20 text-white px-6 py-3 rounded-xl font-bold hover:bg-indigo-700/70 transition">
                                    View Analytics
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Interview CTA */}
                    <Link
                        href="/interview"
                        className="group relative overflow-hidden bg-gradient-to-r from-teal-600 to-emerald-600 rounded-2xl p-6 flex items-center justify-between text-white shadow-lg shadow-teal-100 hover:shadow-xl hover:from-teal-500 hover:to-emerald-500 transition-all duration-300"
                    >
                        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
                        <div className="relative z-10 flex items-center gap-5">
                            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                                <Mic className="w-7 h-7" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold">Start Full Interview Practice</h3>
                                <p className="text-teal-100 text-sm mt-0.5">Select your band &amp; specialty → Answer questions → Get AI feedback</p>
                            </div>
                        </div>
                        <ChevronRight className="relative z-10 w-6 h-6 text-white/80 group-hover:translate-x-1 transition-transform" />
                    </Link>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <StatCard
                            icon={<Users className="text-blue-600" />}
                            label="Active Users"
                            value={stats?.platform?.active_users?.toLocaleString() ?? '...'}
                            trend="live"
                            trendUp
                            color="bg-blue-50"
                        />
                        <StatCard
                            icon={<Trophy className="text-amber-600" />}
                            label="Avg. Competency"
                            value={stats?.platform?.avg_competency != null ? `${stats.platform.avg_competency}%` : '...'}
                            trend="platform"
                            trendUp
                            color="bg-amber-50"
                        />
                        <StatCard
                            icon={<MessageSquare className="text-emerald-600" />}
                            label="Questions Answered"
                            value={stats?.platform?.total_questions_answered?.toLocaleString() ?? '...'}
                            trend="total"
                            trendUp
                            color="bg-emerald-50"
                        />
                        <StatCard
                            icon={<Activity className="text-indigo-600" />}
                            label="My Accuracy"
                            value={stats?.personal?.accuracy != null ? `${stats.personal.accuracy}%` : '...'}
                            trend="personal"
                            color="bg-indigo-50"
                        />
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Left Column - System Health & Interview */}
                        <div className="space-y-8">
                            <SectionHeader title="System Status" subtitle="Infrastructure Health" />
                            <SystemHealth />

                            <SectionHeader title="AI Interview Mode" subtitle="Quick-try widget — Voice & Text Simulation" />
                            <div className="text-xs text-slate-400 mb-2 flex items-center gap-1.5">
                                <Mic className="w-3.5 h-3.5" />
                                <span>For the full end-to-end interview flow with band/specialty selection and results, </span>
                                <Link href="/interview" className="text-teal-600 font-semibold hover:underline">go to /interview</Link>.
                            </div>
                            <InterviewMode />
                        </div>

                        {/* Middle & Right Column - Main Work Areas */}
                        <div className="lg:col-span-2 space-y-8">
                            <SectionHeader title="AI Video Analysis" subtitle="Multimodal Clinical Feedback" />
                            <VideoAnalysis />

                            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                                <div className="space-y-8">
                                    <SectionHeader title="Study Zone" subtitle="RAG Knowledge Base" />
                                    <StudyZone />
                                </div>
                                <div className="space-y-8">
                                    <SectionHeader title="Knowledge Graph" subtitle="Topic Relationships" />
                                    <div className="h-[400px] xl:h-[700px]">
                                        <KnowledgeGraph />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
        </ProtectedRoute>
    );
}

// Sub-components for cleaner code
function NavItem({ icon, label, active = false }: { icon: React.ReactNode, label: string, active?: boolean }) {
    return (
        <a href="#" className={`flex items-center gap-3 px-4 py-3.5 rounded-xl font-medium transition-all duration-200 group
            ${active
                ? 'bg-gradient-to-r from-indigo-50 to-white text-indigo-700 shadow-sm border border-indigo-100'
                : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'}`}>
            <span className={`transition-colors ${active ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600'}`}>
                {React.cloneElement(icon as React.ReactElement, { size: 20 })}
            </span>
            {label}
        </a>
    );
}

function StatCard({ icon, label, value, trend, trendUp, color }: any) {
    return (
        <div className="bg-white p-6 rounded-2xl shadow-[0_2px_10px_-2px_rgba(0,0,0,0.05)] border border-slate-100 hover:shadow-lg transition-all duration-300 group">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-xl ${color} transition-transform group-hover:scale-110`}>
                    {React.cloneElement(icon, { size: 24 })}
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded-full ${trendUp ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
                    {trend}
                </span>
            </div>
            <h3 className="text-3xl font-bold text-slate-800 mb-1">{value}</h3>
            <p className="text-sm text-slate-500 font-medium">{label}</p>
        </div>
    );
}

function SectionHeader({ title, subtitle }: { title: string, subtitle: string }) {
    return (
        <div className="mb-2">
            <h3 className="text-lg font-bold text-slate-800">{title}</h3>
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{subtitle}</p>
        </div>
    );
}
