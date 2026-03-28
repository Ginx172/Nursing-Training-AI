import React, { useState, useEffect, useCallback, useRef } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import {
  ChevronLeft, ChevronRight, Maximize, Minimize, Brain, Shield, WifiOff,
  Volume2, BarChart3, Users, BookOpen, Award, Clock, CheckCircle, XCircle,
  Stethoscope, GraduationCap, TrendingUp, Zap, Lock, Globe, ArrowRight,
  Sparkles, Target, HeartPulse, MonitorSmartphone, Video, Timer,
} from 'lucide-react';

/* =================================================================
   ANIMATED COUNTER HOOK
   ================================================================= */
function useAnimatedNumber(target: number, duration = 1200, active = false) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (!active) { setValue(0); return; }
    let start = 0;
    const step = target / (duration / 16);
    const interval = setInterval(() => {
      start += step;
      if (start >= target) { setValue(target); clearInterval(interval); }
      else setValue(Math.round(start));
    }, 16);
    return () => clearInterval(interval);
  }, [target, duration, active]);
  return value;
}

function AnimatedStat({ value, suffix = '', active }: { value: number; suffix?: string; active: boolean }) {
  const num = useAnimatedNumber(value, 1400, active);
  return <>{num.toLocaleString()}{suffix}</>;
}

/* =================================================================
   PLATFORM DATA
   ================================================================= */
const STATS = {
  questionBanks: 2140, totalQuestions: 42800, specialties: 33,
  nhsBands: 10, sectors: 5, securityScore: 84, penTestVectors: 50,
  penTestPass: 42, penTestFail: 0, apiEndpoints: 72,
};

const NHS_RATES: Record<string, number> = {
  'Band 5': 29, 'Band 6': 36, 'Band 7': 44, 'Band 8a': 52,
};

/* =================================================================
   STAGGERED REVEAL WRAPPER
   ================================================================= */
function Reveal({ children, delay = 0, active }: { children: React.ReactNode; delay?: number; active: boolean }) {
  return (
    <div
      className="transition-all duration-700 ease-out"
      style={{
        opacity: active ? 1 : 0,
        transform: active ? 'translateY(0)' : 'translateY(32px)',
        transitionDelay: active ? `${delay}ms` : '0ms',
      }}
    >
      {children}
    </div>
  );
}

/* =================================================================
   ROI CALCULATOR
   ================================================================= */
function ROICalculator({ active }: { active: boolean }) {
  const [nurses, setNurses] = useState(3000);
  const [hours, setHours] = useState(40);
  const [band, setBand] = useState('Band 6');

  const rate = NHS_RATES[band] || 36;
  const efficiency = 0.30;
  const hoursSaved = Math.round(nurses * hours * efficiency);
  const costSaved = hoursSaved * rate;
  const fte = Math.round(hoursSaved / 1575);

  const animHours = useAnimatedNumber(hoursSaved, 800, active);
  const animCost = useAnimatedNumber(costSaved, 800, active);
  const animFte = useAnimatedNumber(fte, 800, active);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 w-full max-w-6xl">
      {/* Controls - 2 cols */}
      <div className="lg:col-span-2 bg-white/[0.04] backdrop-blur-md rounded-3xl p-8 border border-white/[0.08] shadow-2xl">
        <h3 className="text-lg font-semibold text-teal-300 mb-8 tracking-wide uppercase">Trust Parameters</h3>
        <div className="space-y-8">
          <div>
            <div className="flex justify-between mb-3">
              <span className="text-sm text-slate-400">Nursing Staff</span>
              <span className="text-teal-300 font-bold tabular-nums">{nurses.toLocaleString()}</span>
            </div>
            <input type="range" min={200} max={15000} step={100} value={nurses}
              onChange={(e) => setNurses(+e.target.value)}
              className="w-full h-1.5 rounded-full appearance-none bg-white/10 accent-teal-400 cursor-pointer" />
            <div className="flex justify-between text-[11px] text-slate-600 mt-1"><span>200</span><span>15,000</span></div>
          </div>
          <div>
            <div className="flex justify-between mb-3">
              <span className="text-sm text-slate-400">Training Hours / Year</span>
              <span className="text-teal-300 font-bold tabular-nums">{hours}h</span>
            </div>
            <input type="range" min={10} max={120} step={5} value={hours}
              onChange={(e) => setHours(+e.target.value)}
              className="w-full h-1.5 rounded-full appearance-none bg-white/10 accent-teal-400 cursor-pointer" />
            <div className="flex justify-between text-[11px] text-slate-600 mt-1"><span>10h</span><span>120h</span></div>
          </div>
          <div>
            <span className="text-sm text-slate-400 block mb-3">NHS Agenda for Change Band</span>
            <div className="grid grid-cols-4 gap-2">
              {Object.keys(NHS_RATES).map((b) => (
                <button key={b} onClick={() => setBand(b)}
                  className={`py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                    band === b ? 'bg-teal-500 text-white shadow-lg shadow-teal-500/30 scale-105' : 'bg-white/[0.06] text-slate-400 hover:bg-white/10'
                  }`}>{b}</button>
              ))}
            </div>
            <p className="text-[11px] text-slate-600 mt-3">{band} hourly rate: &pound;{rate}/hr (AfC 2025/26 mid-point)</p>
          </div>
        </div>
      </div>

      {/* Results - 3 cols */}
      <div className="lg:col-span-3 flex flex-col gap-4">
        <div className="flex-1 bg-gradient-to-br from-teal-500/[0.12] to-cyan-600/[0.08] backdrop-blur-md rounded-3xl p-8 border border-teal-400/[0.15] shadow-2xl">
          <p className="text-slate-400 text-sm mb-2 uppercase tracking-wider">Hours Returned to Wards</p>
          <p className="text-6xl font-black text-white tabular-nums">{animHours.toLocaleString()}</p>
          <p className="text-teal-300 text-lg mt-2">clinical hours per year</p>
        </div>
        <div className="flex-1 bg-gradient-to-br from-emerald-500/[0.12] to-green-600/[0.08] backdrop-blur-md rounded-3xl p-8 border border-emerald-400/[0.15] shadow-2xl">
          <p className="text-slate-400 text-sm mb-2 uppercase tracking-wider">Estimated Annual Saving</p>
          <p className="text-6xl font-black text-white tabular-nums">&pound;{animCost.toLocaleString()}</p>
          <p className="text-emerald-300 text-lg mt-2">based on {band} AfC rates</p>
        </div>
        <div className="bg-white/[0.04] backdrop-blur-md rounded-3xl p-6 border border-white/[0.08]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-500 text-sm uppercase tracking-wider">FTE Nurses Released</p>
              <p className="text-4xl font-black text-white mt-1 tabular-nums">{animFte}</p>
            </div>
            <p className="text-xs text-slate-600 text-right max-w-[200px]">Based on 1,575 working hours/year<br/>(AfC full-time equivalent)</p>
          </div>
        </div>
      </div>
    </div>
  );
}

/* =================================================================
   PROGRESS BAR
   ================================================================= */
function ProgressBar({ current, total }: { current: number; total: number }) {
  const pct = ((current + 1) / total) * 100;
  return (
    <div className="fixed top-0 left-0 right-0 h-[3px] z-50 bg-white/[0.06]">
      <div className="h-full bg-gradient-to-r from-teal-400 to-cyan-400 transition-all duration-500 ease-out" style={{ width: `${pct}%` }} />
    </div>
  );
}

/* =================================================================
   MAIN PRESENTATION
   ================================================================= */
export default function PresentationPage() {
  const router = useRouter();
  const [current, setCurrent] = useState(0);
  const [fs, setFs] = useState(false);
  const total = 10;

  const go = useCallback((dir: 1 | -1) => setCurrent((c) => Math.max(0, Math.min(total - 1, c + dir))), []);
  const toggleFs = useCallback(() => {
    if (!document.fullscreenElement) { document.documentElement.requestFullscreen(); setFs(true); }
    else { document.exitFullscreen(); setFs(false); }
  }, []);

  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); go(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
      if (e.key === 'f' || e.key === 'F') toggleFs();
      if (e.key === 'Escape' && !document.fullscreenElement) router.push('/');
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [go, toggleFs, router]);

  const vis = (i: number) => i === current;
  const sc = (i: number) =>
    `absolute inset-0 flex flex-col items-center justify-center px-6 md:px-16 lg:px-24 transition-all duration-700 ease-out ${
      i === current ? 'opacity-100 scale-100' : i < current ? 'opacity-0 scale-95 -translate-x-8' : 'opacity-0 scale-95 translate-x-8'
    } ${i !== current ? 'pointer-events-none' : ''}`;

  return (
    <>
      <Head>
        <title>Nursing Training AI - Executive Presentation</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
        <style>{`body { font-family: 'Inter', system-ui, -apple-system, sans-serif !important; }`}</style>
      </Head>

      <div className="relative w-screen h-screen overflow-hidden text-white select-none"
        style={{ background: 'radial-gradient(ellipse at 20% 50%, #0d2a5c 0%, #0A1C40 40%, #071530 100%)' }}>

        {/* Subtle mesh gradient overlay */}
        <div className="absolute inset-0 opacity-30"
          style={{ background: 'radial-gradient(circle at 80% 20%, rgba(15,118,110,0.15) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(59,130,246,0.1) 0%, transparent 50%)' }} />

        <ProgressBar current={current} total={total} />

        {/* Nav */}
        <div className="fixed top-5 right-5 z-50 flex items-center gap-2">
          <span className="text-[11px] text-slate-500 mr-2 tabular-nums">{current + 1}/{total}</span>
          <button onClick={toggleFs} className="p-2.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] transition backdrop-blur-sm" title="Fullscreen (F)">
            {fs ? <Minimize className="w-4 h-4" /> : <Maximize className="w-4 h-4" />}
          </button>
        </div>
        {current > 0 && (
          <button onClick={() => go(-1)} className="fixed left-5 top-1/2 -translate-y-1/2 z-50 p-3 rounded-2xl bg-white/[0.04] hover:bg-white/[0.1] transition backdrop-blur-sm border border-white/[0.06]">
            <ChevronLeft className="w-5 h-5" />
          </button>
        )}
        {current < total - 1 && (
          <button onClick={() => go(1)} className="fixed right-5 top-1/2 -translate-y-1/2 z-50 p-3 rounded-2xl bg-white/[0.04] hover:bg-white/[0.1] transition backdrop-blur-sm border border-white/[0.06]">
            <ChevronRight className="w-5 h-5" />
          </button>
        )}

        {/* ============ SLIDE 0: TITLE ============ */}
        <div className={sc(0)}>
          <Reveal active={vis(0)} delay={0}>
            <div className="relative inline-flex items-center justify-center w-28 h-28 mb-8">
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-teal-400 to-blue-500 blur-2xl opacity-40" />
              <div className="relative w-28 h-28 rounded-full bg-gradient-to-br from-teal-400 to-blue-500 flex items-center justify-center shadow-2xl">
                <HeartPulse className="w-14 h-14 text-white" />
              </div>
            </div>
          </Reveal>
          <Reveal active={vis(0)} delay={200}>
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tight">
              <span className="bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">Nursing Training</span>
              <span className="bg-gradient-to-r from-teal-300 to-cyan-300 bg-clip-text text-transparent"> AI</span>
            </h1>
          </Reveal>
          <Reveal active={vis(0)} delay={400}>
            <p className="text-lg md:text-xl text-slate-400 mt-6 font-light tracking-wide">
              The Future of Clinical Education
            </p>
          </Reveal>
          <Reveal active={vis(0)} delay={600}>
            <div className="flex items-center gap-1 mt-3">
              {['Hyper-personalised', 'Secure', 'Scalable'].map((w, i) => (
                <React.Fragment key={w}>
                  {i > 0 && <span className="text-teal-600 mx-2">&middot;</span>}
                  <span className="text-teal-300 font-semibold">{w}</span>
                </React.Fragment>
              ))}
            </div>
          </Reveal>
          <Reveal active={vis(0)} delay={900}>
            <div className="flex items-center gap-8 mt-14 text-sm text-slate-500">
              <span className="flex items-center gap-2"><BookOpen className="w-4 h-4 text-teal-500" /> 42,800+ Questions</span>
              <span className="flex items-center gap-2"><Stethoscope className="w-4 h-4 text-teal-500" /> 33 Specialties</span>
              <span className="flex items-center gap-2"><Shield className="w-4 h-4 text-teal-500" /> 84/100 Security</span>
            </div>
          </Reveal>
        </div>

        {/* ============ SLIDE 1: PROBLEM ============ */}
        <div className={sc(1)}>
          <Reveal active={vis(1)} delay={0}>
            <h2 className="text-4xl md:text-6xl font-extrabold mb-14 text-center">
              The Status Quo is <span className="text-red-400">Broken</span>
            </h2>
          </Reveal>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl w-full">
            {[
              { icon: Clock, title: 'Cognitive Fatigue', desc: 'Current LMS platforms are clunky, outdated, and increase screen fatigue after 12-hour shifts. Nurses disengage from mandatory training.' },
              { icon: Users, title: 'Senior Staff Burnout', desc: 'Band 7 and Band 8 nurses lose thousands of critical clinical hours mentoring juniors with repetitive, generic, static scenarios.' },
              { icon: BookOpen, title: 'Static Content', desc: 'NICE guidelines and clinical protocols evolve frequently, but updating traditional eLearning modules takes months of manual work.' },
            ].map((item, i) => (
              <Reveal key={i} active={vis(1)} delay={200 + i * 200}>
                <div className="bg-white/[0.04] backdrop-blur-md rounded-3xl p-8 border border-white/[0.06] hover:border-red-400/20 transition-all duration-300 h-full shadow-xl">
                  <div className="w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center mb-5">
                    <item.icon className="w-6 h-6 text-red-400" />
                  </div>
                  <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                  <p className="text-slate-400 leading-relaxed text-[15px]">{item.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        {/* ============ SLIDE 2: SOLUTION ============ */}
        <div className={sc(2)}>
          <Reveal active={vis(2)} delay={0}>
            <h2 className="text-4xl md:text-6xl font-extrabold mb-3 text-center">
              The <span className="text-teal-300">AI Clinical Mentor</span>
            </h2>
          </Reveal>
          <Reveal active={vis(2)} delay={150}>
            <p className="text-lg text-slate-400 text-center mb-12">
              Artificial Intelligence trained on <span className="text-teal-300 font-semibold">your</span> clinical standards
            </p>
          </Reveal>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5 max-w-6xl w-full">
            {[
              { icon: Brain, title: 'Generative AI', desc: 'Reads NICE guidelines via RAG and creates unique clinical scenarios. Zero repetition, infinite variety.', grad: 'from-purple-500/10 to-purple-700/10 border-purple-400/10' },
              { icon: WifiOff, title: 'True Offline Mode', desc: 'Works flawlessly in hospital WiFi dead zones. AES-256 encrypted cache with automatic sync.', grad: 'from-blue-500/10 to-blue-700/10 border-blue-400/10' },
              { icon: Volume2, title: 'Voice Assistant', desc: 'Native British English Text-to-Speech. Adjustable speed 0.5x-2x. Post-shift accessibility.', grad: 'from-teal-500/10 to-teal-700/10 border-teal-400/10' },
              { icon: Target, title: 'Band-Adaptive', desc: 'Tailored difficulty from Band 2 to 8d. AI adjusts complexity based on performance and progression.', grad: 'from-amber-500/10 to-amber-700/10 border-amber-400/10' },
            ].map((item, i) => (
              <Reveal key={i} active={vis(2)} delay={200 + i * 150}>
                <div className={`bg-gradient-to-br ${item.grad} backdrop-blur-md rounded-3xl p-7 border transition-all duration-300 hover:scale-[1.03] h-full shadow-xl`}>
                  <div className="w-11 h-11 rounded-2xl bg-white/[0.06] flex items-center justify-center mb-4">
                    <item.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold mb-2">{item.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{item.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        {/* ============ SLIDE 3: PLATFORM SCALE ============ */}
        <div className={sc(3)}>
          <Reveal active={vis(3)} delay={0}>
            <h2 className="text-4xl md:text-6xl font-extrabold mb-14 text-center">
              Platform at <span className="text-teal-300">Scale</span>
            </h2>
          </Reveal>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5 max-w-5xl w-full">
            {[
              { value: STATS.questionBanks, label: 'Question Banks', icon: BookOpen },
              { value: STATS.totalQuestions, label: 'Total Questions', icon: Zap },
              { value: STATS.specialties, label: 'Clinical Specialties', icon: Stethoscope },
              { value: STATS.nhsBands, label: 'NHS Bands (2-8d)', icon: Award },
              { value: STATS.sectors, label: 'Healthcare Sectors', icon: Globe },
              { value: STATS.apiEndpoints, label: 'API Endpoints', icon: TrendingUp },
              { value: 0, label: 'Multi-Factor Auth', icon: Lock, text: '2FA / TOTP' },
              { value: 0, label: 'Full Compliance', icon: Shield, text: 'GDPR + DSPT' },
            ].map((item, i) => (
              <Reveal key={i} active={vis(3)} delay={100 + i * 100}>
                <div className="bg-white/[0.04] backdrop-blur-md rounded-3xl p-6 border border-white/[0.06] text-center hover:border-teal-400/20 transition-all duration-300 shadow-xl h-full">
                  <item.icon className="w-7 h-7 text-teal-400 mx-auto mb-4" />
                  <p className="text-3xl md:text-4xl font-black text-white tabular-nums">
                    {item.text || <AnimatedStat value={item.value} suffix={item.value > 100 ? '+' : ''} active={vis(3)} />}
                  </p>
                  <p className="text-sm text-slate-500 mt-2">{item.label}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        {/* ============ SLIDE 4: COMPETITIVE ADVANTAGE ============ */}
        <div className={sc(4)}>
          <Reveal active={vis(4)} delay={0}>
            <h2 className="text-4xl md:text-6xl font-extrabold mb-12 text-center">
              Why <span className="text-teal-300">Us</span>
            </h2>
          </Reveal>
          <Reveal active={vis(4)} delay={200}>
            <div className="bg-white/[0.03] backdrop-blur-md rounded-3xl border border-white/[0.06] overflow-hidden max-w-5xl w-full shadow-2xl">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/[0.08]">
                    <th className="p-5 text-sm text-slate-500 font-semibold uppercase tracking-wider">Feature</th>
                    <th className="p-5 text-sm text-slate-500 font-semibold uppercase tracking-wider text-center">Traditional LMS</th>
                    <th className="p-5 text-sm text-teal-400 font-semibold uppercase tracking-wider text-center">Nursing Training AI</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ['Question Generation', 'Static banks (rote learning)', 'AI-generated unique scenarios'],
                    ['Connectivity', 'Requires constant internet', 'Full offline mode + auto-sync'],
                    ['Accessibility', 'Text-only modules', 'Native British English TTS'],
                    ['Personalisation', 'One-size-fits-all', 'Band-adaptive (Band 2 to 8d)'],
                    ['Content Refresh', 'Manual (takes months)', 'AI reads new guidelines instantly'],
                    ['Security', 'Basic login', '2FA, JWT, DSPT, pen-tested (84/100)'],
                    ['Data Sovereignty', 'Cloud-dependent', 'On-premise capable, zero data leak'],
                  ].map(([f, old, ours], i) => (
                    <tr key={i} className="border-b border-white/[0.04] hover:bg-white/[0.03] transition">
                      <td className="p-4 font-medium text-[15px]">{f}</td>
                      <td className="p-4 text-center text-red-300/70 text-sm"><XCircle className="w-4 h-4 inline mr-1.5 mb-0.5 opacity-60" />{old}</td>
                      <td className="p-4 text-center text-teal-300 text-sm"><CheckCircle className="w-4 h-4 inline mr-1.5 mb-0.5" />{ours}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Reveal>
        </div>

        {/* ============ SLIDE 5: SECURITY ============ */}
        <div className={sc(5)}>
          <Reveal active={vis(5)} delay={0}>
            <h2 className="text-4xl md:text-6xl font-extrabold mb-12 text-center">
              Security & <span className="text-teal-300">NHS Compliance</span>
            </h2>
          </Reveal>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl w-full">
            <Reveal active={vis(5)} delay={200}>
              <div className="bg-white/[0.04] backdrop-blur-md rounded-3xl p-8 border border-white/[0.06] shadow-2xl h-full">
                <h3 className="text-xl font-bold mb-6 text-slate-300">Automated Penetration Test</h3>
                <div className="flex items-end gap-4 mb-8">
                  <span className="text-8xl font-black text-teal-300 leading-none tabular-nums">
                    <AnimatedStat value={84} active={vis(5)} />
                  </span>
                  <span className="text-2xl text-slate-500 mb-2">/100</span>
                  <span className="ml-auto px-4 py-2 bg-teal-500/15 text-teal-300 rounded-full font-bold text-sm tracking-wide">GOOD</span>
                </div>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="bg-emerald-500/10 rounded-2xl p-4">
                    <p className="text-3xl font-bold text-emerald-400 tabular-nums"><AnimatedStat value={42} active={vis(5)} /></p>
                    <p className="text-xs text-slate-500 mt-1">PASS</p>
                  </div>
                  <div className="bg-emerald-500/10 rounded-2xl p-4">
                    <p className="text-3xl font-bold text-emerald-400 tabular-nums">0</p>
                    <p className="text-xs text-slate-500 mt-1">FAIL</p>
                  </div>
                  <div className="bg-amber-500/10 rounded-2xl p-4">
                    <p className="text-3xl font-bold text-amber-400 tabular-nums">8</p>
                    <p className="text-xs text-slate-500 mt-1">WARN</p>
                  </div>
                </div>
                <p className="text-[11px] text-slate-600 mt-5">50 attack vectors: OWASP Top 10, JWT forgery, IDOR, SSRF, XSS, SQLi, CSRF, brute force</p>
              </div>
            </Reveal>
            <Reveal active={vis(5)} delay={400}>
              <div className="space-y-4 h-full flex flex-col">
                {[
                  { title: 'NHS DSPT v8', desc: 'Data Security and Protection Toolkit alignment. Full audit trail.', icon: Shield },
                  { title: 'GDPR Article 15 & 17', desc: 'Complete data export and right-to-erasure with confirmation.', icon: Lock },
                  { title: 'NHS DCB0129', desc: 'Clinical risk management standard for health IT systems.', icon: CheckCircle },
                  { title: 'DTAC Assessment', desc: 'Digital Technology Assessment Criteria across 5 domains.', icon: Award },
                ].map((item, i) => (
                  <div key={i} className="bg-white/[0.04] backdrop-blur-md rounded-2xl p-5 border border-white/[0.06] flex items-start gap-4 hover:border-teal-400/20 transition flex-1 shadow-lg">
                    <div className="w-10 h-10 rounded-xl bg-teal-500/10 flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-5 h-5 text-teal-400" />
                    </div>
                    <div>
                      <h4 className="font-bold">{item.title}</h4>
                      <p className="text-sm text-slate-500 mt-0.5">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Reveal>
          </div>
        </div>

        {/* ============ SLIDE 6: ROI ============ */}
        <div className={sc(6)}>
          <Reveal active={vis(6)} delay={0}>
            <h2 className="text-4xl md:text-5xl font-extrabold mb-2 text-center">
              Return on <span className="text-teal-300">Investment</span>
            </h2>
          </Reveal>
          <Reveal active={vis(6)} delay={100}>
            <p className="text-slate-500 text-center mb-10 text-sm">
              Interactive simulator &middot; NHS Agenda for Change 2025/26 mid-point rates
            </p>
          </Reveal>
          <Reveal active={vis(6)} delay={200}>
            <ROICalculator active={vis(6)} />
          </Reveal>
        </div>

        {/* ============ SLIDE 7: LIVE DEMO ============ */}
        <div className={sc(7)}>
          <Reveal active={vis(7)} delay={0}>
            <h2 className="text-4xl md:text-6xl font-extrabold mb-3 text-center">
              See It <span className="text-teal-300">Live</span>
            </h2>
          </Reveal>
          <Reveal active={vis(7)} delay={100}>
            <p className="text-lg text-slate-400 text-center mb-12">Click any module to open the live application</p>
          </Reveal>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-5 max-w-4xl w-full">
            {[
              { label: 'Dashboard', path: '/dashboard', icon: BarChart3, desc: 'Real-time analytics from database' },
              { label: 'Interview Practice', path: '/interview', icon: Brain, desc: '15 AI questions + voice TTS' },
              { label: 'Registration Flow', path: '/register?demo=1', icon: Users, desc: 'NHS password policy enforced' },
              { label: 'Training History', path: '/history', icon: Clock, desc: 'Session results and progress' },
              { label: 'Settings & 2FA', path: '/settings', icon: Lock, desc: 'Profile, security, TOTP setup' },
              { label: 'Password Reset', path: '/forgot-password', icon: Shield, desc: 'Secure JWT-based email flow' },
            ].map((item, i) => (
              <Reveal key={i} active={vis(7)} delay={200 + i * 100}>
                <button onClick={() => window.open(item.path, '_blank')}
                  className="bg-white/[0.04] backdrop-blur-md rounded-3xl p-6 border border-white/[0.06] hover:border-teal-400/30 hover:bg-white/[0.08] transition-all duration-300 text-left group w-full shadow-xl">
                  <div className="w-11 h-11 rounded-2xl bg-teal-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition">
                    <item.icon className="w-6 h-6 text-teal-400" />
                  </div>
                  <h3 className="font-bold mb-1">{item.label}</h3>
                  <p className="text-sm text-slate-500">{item.desc}</p>
                  <ArrowRight className="w-4 h-4 text-teal-400 mt-3 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                </button>
              </Reveal>
            ))}
          </div>
        </div>

        {/* ============ SLIDE 8: ROADMAP ============ */}
        <div className={sc(8)}>
          <Reveal active={vis(8)} delay={0}>
            <h2 className="text-4xl md:text-6xl font-extrabold mb-3 text-center">
              Development <span className="text-teal-300">Roadmap</span>
            </h2>
          </Reveal>
          <Reveal active={vis(8)} delay={100}>
            <p className="text-lg text-slate-400 text-center mb-12">What's coming next to the platform</p>
          </Reveal>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 max-w-6xl w-full">
            {[
              {
                icon: Video,
                title: 'Video Clinical Scenarios',
                desc: 'Short video clips presenting real ward situations. "You walk into the bay and find this patient \u2014 what do you do?" AI evaluates the response against the correct protocol.',
                phase: 'Phase 1',
                color: 'from-rose-500/10 to-rose-700/10 border-rose-400/15',
                phaseColor: 'bg-rose-500/20 text-rose-300',
              },
              {
                icon: BarChart3,
                title: 'AI Peer Benchmarking',
                desc: 'Anonymous performance dashboard showing how you compare to peers at the same Band and Specialty. Identify Trust-wide knowledge gaps in real time.',
                phase: 'Phase 2',
                color: 'from-blue-500/10 to-blue-700/10 border-blue-400/15',
                phaseColor: 'bg-blue-500/20 text-blue-300',
              },
              {
                icon: Users,
                title: 'Mentor Matching & Digital Preceptorship',
                desc: 'Connect Band 5/6 nurses with Band 7/8 mentors within the Trust. Digital competency sign-off replaces paper-based supervision logs.',
                phase: 'Phase 2',
                color: 'from-purple-500/10 to-purple-700/10 border-purple-400/15',
                phaseColor: 'bg-purple-500/20 text-purple-300',
              },
              {
                icon: Shield,
                title: 'Incident Debrief Simulator',
                desc: 'Train on anonymised Datix-style incident reports. Walk through root cause analysis, Duty of Candour, and correct escalation pathways.',
                phase: 'Phase 3',
                color: 'from-amber-500/10 to-amber-700/10 border-amber-400/15',
                phaseColor: 'bg-amber-500/20 text-amber-300',
              },
              {
                icon: Timer,
                title: 'Shift-Ready Micro-Learning',
                desc: '60-second modules before each shift. "Today\'s focus: recognising sepsis in elderly patients." AI-selected topics based on season and epidemiology.',
                phase: 'Phase 3',
                color: 'from-teal-500/10 to-teal-700/10 border-teal-400/15',
                phaseColor: 'bg-teal-500/20 text-teal-300',
              },
            ].map((item, i) => (
              <Reveal key={i} active={vis(8)} delay={200 + i * 150}>
                <div className={`bg-gradient-to-br ${item.color} backdrop-blur-md rounded-3xl p-6 border transition-all duration-300 hover:scale-[1.03] h-full shadow-xl flex flex-col`}>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-2xl bg-white/[0.06] flex items-center justify-center">
                      <item.icon className="w-5 h-5 text-white" />
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase ${item.phaseColor}`}>
                      {item.phase}
                    </span>
                  </div>
                  <h3 className="text-[15px] font-bold mb-2 leading-snug">{item.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed flex-1">{item.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        {/* ============ SLIDE 9: CTA ============ */}
        <div className={sc(9)}>
          <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(15,118,110,0.12) 0%, transparent 60%)' }} />
          <div className="relative z-10 text-center max-w-3xl">
            <Reveal active={vis(9)} delay={0}>
              <div className="relative inline-flex items-center justify-center w-24 h-24 mb-10">
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-teal-400 to-cyan-400 blur-2xl opacity-30" />
                <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-teal-400 to-blue-500 flex items-center justify-center shadow-2xl">
                  <Sparkles className="w-12 h-12 text-white" />
                </div>
              </div>
            </Reveal>
            <Reveal active={vis(9)} delay={200}>
              <h2 className="text-5xl md:text-7xl font-black leading-tight">
                Ready to Transform<br />
                <span className="bg-gradient-to-r from-teal-300 to-cyan-300 bg-clip-text text-transparent">Clinical Education?</span>
              </h2>
            </Reveal>
            <Reveal active={vis(9)} delay={400}>
              <p className="text-xl text-slate-400 mt-8 leading-relaxed font-light">
                A Band 8 mentor in every nurse's pocket.<br />
                Secure. Offline-ready. DSPT-aligned. Production-ready.
              </p>
            </Reveal>
            <Reveal active={vis(9)} delay={600}>
              <div className="flex items-center justify-center gap-8 mt-12 text-sm text-slate-500">
                <span className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-teal-400" /> 42,800+ questions</span>
                <span className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-teal-400" /> 33 specialties</span>
                <span className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-teal-400" /> 84/100 security</span>
              </div>
            </Reveal>
            <Reveal active={vis(9)} delay={900}>
              <div className="mt-14 text-xs text-slate-600">
                <kbd className="px-2 py-1 bg-white/[0.06] rounded-md border border-white/[0.08] text-slate-500">F</kbd> fullscreen
                <span className="mx-3 text-slate-700">&middot;</span>
                <kbd className="px-2 py-1 bg-white/[0.06] rounded-md border border-white/[0.08] text-slate-500">&larr;</kbd>{' '}
                <kbd className="px-2 py-1 bg-white/[0.06] rounded-md border border-white/[0.08] text-slate-500">&rarr;</kbd> navigate
                <span className="mx-3 text-slate-700">&middot;</span>
                <kbd className="px-2 py-1 bg-white/[0.06] rounded-md border border-white/[0.08] text-slate-500">Esc</kbd> exit
              </div>
            </Reveal>
          </div>
        </div>

      </div>
    </>
  );
}
