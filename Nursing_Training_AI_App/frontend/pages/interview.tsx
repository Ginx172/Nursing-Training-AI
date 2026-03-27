import React, { useState, useEffect, useRef, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import {
    ChevronRight,
    ChevronLeft,
    LayoutDashboard,
    Mic,
    MicOff,
    CheckCircle,
    AlertCircle,
    Loader2,
    Trophy,
    BookOpen,
    RotateCcw,
    Send,
    Clock,
    Activity,
    Volume2,
    VolumeX,
} from 'lucide-react';

const API_URL =
    typeof window !== 'undefined'
        ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        : 'http://localhost:8000';

// ─── Types ───────────────────────────────────────────────────────────────────

interface BandOption {
    id: string;
    name: string;
    description: string;
}

interface SpecialtyOption {
    id: string;
    name: string;
    description: string;
}

interface Question {
    id: number;
    title: string;
    question_text: string;
    question_type: string;
    options?: string[] | null;
    correct_answer?: string | null;
    difficulty?: string | null;
    competencies?: string[];
    expected_points?: string[];
}

interface QuestionBank {
    band: string;
    specialty: string;
    version: string;
    questions: Question[];
}

interface PerQuestionResult {
    question_id: number;
    is_correct: boolean;
    feedback: string;
    recommendations: { title: string; summary: string; url?: string | null }[];
}

interface BatchResult {
    total_questions: number;
    correct: number;
    score_percentage: number;
    per_question: PerQuestionResult[];
    study_plan: { title: string; items: string[] }[];
    next_steps: string;
}

type Step = 'setup' | 'questions' | 'results';

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
}

function difficultyColor(d?: string | null) {
    switch (d?.toLowerCase()) {
        case 'easy': return 'text-emerald-600 bg-emerald-50';
        case 'intermediate': return 'text-amber-600 bg-amber-50';
        case 'hard':
        case 'advanced': return 'text-red-600 bg-red-50';
        default: return 'text-slate-600 bg-slate-50';
    }
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function InterviewPage() {
    const [step, setStep] = useState<Step>('setup');

    // Setup state
    const [bands, setBands] = useState<BandOption[]>([]);
    const [specialties, setSpecialties] = useState<SpecialtyOption[]>([]);
    const [selectedBand, setSelectedBand] = useState('');
    const [selectedSpecialty, setSelectedSpecialty] = useState('');
    const [setupLoading, setSetupLoading] = useState(true);
    const [setupError, setSetupError] = useState('');

    // Question state
    const [bank, setBank] = useState<QuestionBank | null>(null);
    const [bankLoading, setBankLoading] = useState(false);
    const [bankError, setBankError] = useState('');
    const [currentIndex, setCurrentIndex] = useState(0);
    const [answers, setAnswers] = useState<Record<number, string>>({});

    // Timer
    const [elapsed, setElapsed] = useState(0);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // Speech recognition (STT)
    const recognitionRef = useRef<any>(null);
    const [isListening, setIsListening] = useState(false);
    const canListen = typeof window !== 'undefined' &&
        (!!(window as any).SpeechRecognition || !!(window as any).webkitSpeechRecognition);

    // Text-to-Speech (TTS) - AI citeste intrebarile cu voce
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [ttsEnabled, setTtsEnabled] = useState(true);
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

    const speakQuestion = useCallback((text: string) => {
        if (typeof window === 'undefined' || !window.speechSynthesis || !ttsEnabled) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-GB';
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        // Selecteaza o voce engleza daca e disponibila
        const voices = window.speechSynthesis.getVoices();
        const enVoice = voices.find(v => v.lang.startsWith('en-GB')) || voices.find(v => v.lang.startsWith('en'));
        if (enVoice) utterance.voice = enVoice;
        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        utteranceRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    }, [ttsEnabled]);

    const stopSpeaking = useCallback(() => {
        if (typeof window !== 'undefined' && window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        setIsSpeaking(false);
    }, []);

    // Cleanup TTS la unmount
    useEffect(() => {
        return () => {
            if (typeof window !== 'undefined' && window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        };
    }, []);

    // Results state
    const [submitting, setSubmitting] = useState(false);
    const [results, setResults] = useState<BatchResult | null>(null);
    const [submitError, setSubmitError] = useState('');

    // ── Load bands & specialties on mount ──────────────────────────────────
    useEffect(() => {
        const load = async () => {
            setSetupLoading(true);
            setSetupError('');
            try {
                const [bRes, sRes] = await Promise.all([
                    fetch(`${API_URL}/api/questions/bands`),
                    fetch(`${API_URL}/api/questions/specialties`),
                ]);
                if (!bRes.ok) throw new Error(`Bands fetch failed: HTTP ${bRes.status}`);
                if (!sRes.ok) throw new Error(`Specialties fetch failed: HTTP ${sRes.status}`);
                setBands(await bRes.json());
                setSpecialties(await sRes.json());
            } catch (e: any) {
                setSetupError(e?.message || 'Failed to load setup data');
            } finally {
                setSetupLoading(false);
            }
        };
        load();
    }, []);

    // ── Timer ─────────────────────────────────────────────────────────────
    useEffect(() => {
        if (step === 'questions') {
            setElapsed(0);
            timerRef.current = setInterval(() => setElapsed(s => s + 1), 1000);
        } else {
            if (timerRef.current) {
                clearInterval(timerRef.current);
                timerRef.current = null;
            }
        }
        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, [step]);

    // ── Start interview ────────────────────────────────────────────────────
    const startInterview = async () => {
        if (!selectedBand || !selectedSpecialty) return;
        setBankLoading(true);
        setBankError('');
        try {
            const res = await fetch(
                `${API_URL}/api/questions/bank/${selectedSpecialty}/${selectedBand}`
            );
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data: QuestionBank = await res.json();
            if (!data.questions?.length) throw new Error('No questions in bank');
            setBank(data);
            setAnswers({});
            setCurrentIndex(0);
            setResults(null);
            setStep('questions');
        } catch (e: any) {
            setBankError(e?.message || 'Failed to load questions');
        } finally {
            setBankLoading(false);
        }
    };

    // ── Answer helpers ─────────────────────────────────────────────────────
    const currentQuestion = bank?.questions[currentIndex];
    const totalQuestions = bank?.questions.length ?? 0;

    // ── Auto-speak question when it changes ────────────────────────────
    useEffect(() => {
        if (step === 'questions' && currentQuestion && ttsEnabled) {
            // Delay scurt pentru a lasa UI-ul sa se actualizeze
            const timeout = setTimeout(() => {
                speakQuestion(currentQuestion.question_text);
            }, 400);
            return () => clearTimeout(timeout);
        }
    }, [currentIndex, step, currentQuestion, ttsEnabled, speakQuestion]);
    const answeredCount = Object.values(answers).filter(a => a.trim()).length;
    const allAnswered = answeredCount === totalQuestions;

    const setAnswer = (qId: number, value: string) => {
        setAnswers(prev => ({ ...prev, [qId]: value }));
    };

    // ── Navigation ─────────────────────────────────────────────────────────
    const goNext = () => {
        if (currentIndex < totalQuestions - 1) setCurrentIndex(i => i + 1);
    };
    const goPrev = () => {
        if (currentIndex > 0) setCurrentIndex(i => i - 1);
    };

    // ── Speech recognition ─────────────────────────────────────────────────
    const startListening = useCallback(() => {
        if (typeof window === 'undefined') return;
        const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (!SpeechRec || !currentQuestion) return;
        if (recognitionRef.current) {
            try { recognitionRef.current.stop(); } catch {}
        }
        const rec = new SpeechRec();
        recognitionRef.current = rec;
        rec.lang = 'en-GB';
        rec.interimResults = false;
        rec.maxAlternatives = 1;
        rec.onresult = (event: any) => {
            const transcript = event.results?.[0]?.[0]?.transcript || '';
            if (transcript) setAnswer(currentQuestion.id, transcript);
        };
        rec.onerror = () => setIsListening(false);
        rec.onend = () => setIsListening(false);
        rec.start();
        setIsListening(true);
    }, [currentQuestion]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current) {
            try { recognitionRef.current.stop(); } catch {}
            recognitionRef.current = null;
        }
        setIsListening(false);
    }, []);

    // ── Submit ─────────────────────────────────────────────────────────────
    const submitAnswers = async () => {
        if (!bank) return;
        setSubmitting(true);
        setSubmitError('');
        try {
            const payload = {
                answers: bank.questions.map(q => ({
                    question_id: q.id,
                    user_answer: (answers[q.id] ?? '').trim(),
                })),
            };
            const res = await fetch(`${API_URL}/api/demo/submit-batch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data: BatchResult = await res.json();
            setResults(data);
            setStep('results');
        } catch (e: any) {
            setSubmitError(e?.message || 'Failed to submit answers');
        } finally {
            setSubmitting(false);
        }
    };

    // ── Reset ──────────────────────────────────────────────────────────────
    const resetInterview = () => {
        setStep('setup');
        setBank(null);
        setAnswers({});
        setCurrentIndex(0);
        setResults(null);
        setBankError('');
        setSubmitError('');
    };

    // ─── Render ────────────────────────────────────────────────────────────

    return (
        <div className="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans">
            <Head>
                <title>Interview | Nursing Training AI</title>
            </Head>

            {/* Top Navigation */}
            <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200/60 px-6 py-4 flex items-center gap-4 shadow-sm">
                <Link href="/dashboard" className="flex items-center gap-2 text-slate-500 hover:text-indigo-600 transition font-medium text-sm">
                    <LayoutDashboard className="w-4 h-4" />
                    Dashboard
                </Link>
                <ChevronRight className="w-4 h-4 text-slate-300" />
                <span className="text-slate-800 font-semibold text-sm flex items-center gap-2">
                    <Mic className="w-4 h-4 text-teal-600" />
                    Interview Practice
                </span>
                {step === 'questions' && (
                    <div className="ml-auto flex items-center gap-2 text-slate-500 text-sm font-medium">
                        <Clock className="w-4 h-4" />
                        {formatTime(elapsed)}
                    </div>
                )}
            </header>

            <main className="max-w-3xl mx-auto px-4 py-10 space-y-8">

                {/* ── Step 1: Setup ─────────────────────────────────────────── */}
                {step === 'setup' && (
                    <SetupStep
                        bands={bands}
                        specialties={specialties}
                        loading={setupLoading}
                        error={setupError}
                        bankError={bankError}
                        bankLoading={bankLoading}
                        selectedBand={selectedBand}
                        selectedSpecialty={selectedSpecialty}
                        onBandChange={setSelectedBand}
                        onSpecialtyChange={setSelectedSpecialty}
                        onStart={startInterview}
                    />
                )}

                {/* ── Step 2: Questions ──────────────────────────────────────── */}
                {step === 'questions' && bank && currentQuestion && (
                    <QuestionsStep
                        bank={bank}
                        currentIndex={currentIndex}
                        currentQuestion={currentQuestion}
                        answers={answers}
                        allAnswered={allAnswered}
                        answeredCount={answeredCount}
                        isListening={isListening}
                        canListen={canListen}
                        submitting={submitting}
                        submitError={submitError}
                        isSpeaking={isSpeaking}
                        ttsEnabled={ttsEnabled}
                        onAnswer={setAnswer}
                        onNext={goNext}
                        onPrev={goPrev}
                        onStartListening={startListening}
                        onStopListening={stopListening}
                        onSubmit={submitAnswers}
                        onJumpTo={setCurrentIndex}
                        onSpeak={speakQuestion}
                        onStopSpeaking={stopSpeaking}
                        onToggleTts={setTtsEnabled}
                    />
                )}

                {/* ── Step 3: Results ────────────────────────────────────────── */}
                {step === 'results' && results && (
                    <ResultsStep
                        results={results}
                        bank={bank!}
                        onTryAgain={resetInterview}
                    />
                )}
            </main>
        </div>
    );
}

// ─── Step 1: Setup ────────────────────────────────────────────────────────────

function SetupStep({
    bands, specialties, loading, error, bankError, bankLoading,
    selectedBand, selectedSpecialty,
    onBandChange, onSpecialtyChange, onStart,
}: {
    bands: BandOption[];
    specialties: SpecialtyOption[];
    loading: boolean;
    error: string;
    bankError: string;
    bankLoading: boolean;
    selectedBand: string;
    selectedSpecialty: string;
    onBandChange: (v: string) => void;
    onSpecialtyChange: (v: string) => void;
    onStart: () => void;
}) {
    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="relative overflow-hidden bg-gradient-to-r from-teal-600 to-emerald-600 rounded-3xl p-8 text-white shadow-xl shadow-teal-100">
                <div className="absolute top-0 right-0 w-72 h-72 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2.5 bg-white/20 rounded-xl">
                            <Mic className="w-6 h-6" />
                        </div>
                        <span className="text-teal-100 text-sm font-semibold uppercase tracking-wider">Interview Practice</span>
                    </div>
                    <h1 className="text-3xl font-bold mb-2">Start Your Interview</h1>
                    <p className="text-teal-100 text-base max-w-lg">
                        Select your NHS band and clinical specialty to load a personalised question bank. Answer questions one-by-one and get detailed AI feedback at the end.
                    </p>
                </div>
            </div>

            {/* Selection Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8 space-y-6">
                {loading && (
                    <div className="flex items-center gap-3 text-slate-500">
                        <Loader2 className="w-5 h-5 animate-spin text-teal-600" />
                        <span>Loading configuration…</span>
                    </div>
                )}
                {error && (
                    <div className="flex items-center gap-3 text-red-600 bg-red-50 rounded-xl p-4">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                {!loading && !error && (
                    <>
                        {/* Band Selection */}
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-slate-700 block">
                                NHS Band Level
                            </label>
                            <select
                                value={selectedBand}
                                onChange={e => onBandChange(e.target.value)}
                                className="w-full border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition bg-slate-50"
                            >
                                <option value="">Select a band…</option>
                                {bands.map(b => (
                                    <option key={b.id} value={b.id}>
                                        {b.name} — {b.description}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Specialty Selection */}
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-slate-700 block">
                                Clinical Specialty
                            </label>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {specialties.map(s => (
                                    <button
                                        key={s.id}
                                        onClick={() => onSpecialtyChange(s.id)}
                                        className={`text-left px-4 py-3 rounded-xl border-2 transition-all duration-150 ${
                                            selectedSpecialty === s.id
                                                ? 'border-teal-500 bg-teal-50 text-teal-800'
                                                : 'border-slate-200 bg-white text-slate-700 hover:border-teal-300 hover:bg-teal-50/50'
                                        }`}
                                    >
                                        <div className="font-semibold text-sm">{s.name}</div>
                                        <div className="text-xs text-slate-500 mt-0.5">{s.description}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {bankError && (
                            <div className="flex items-center gap-3 text-red-600 bg-red-50 rounded-xl p-4">
                                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                <span>Could not load questions: {bankError}. Try a different band/specialty combination.</span>
                            </div>
                        )}

                        <button
                            onClick={onStart}
                            disabled={!selectedBand || !selectedSpecialty || bankLoading}
                            className="w-full bg-gradient-to-r from-teal-600 to-emerald-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg shadow-teal-100 hover:shadow-xl hover:from-teal-500 hover:to-emerald-500 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-3"
                        >
                            {bankLoading ? (
                                <><Loader2 className="w-5 h-5 animate-spin" /> Loading Questions…</>
                            ) : (
                                <><Mic className="w-5 h-5" /> Start Interview</>
                            )}
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}

// ─── Step 2: Questions ────────────────────────────────────────────────────────

function QuestionsStep({
    bank, currentIndex, currentQuestion, answers, allAnswered,
    answeredCount, isListening, canListen, submitting, submitError,
    isSpeaking, ttsEnabled,
    onAnswer, onNext, onPrev, onStartListening, onStopListening, onSubmit, onJumpTo,
    onSpeak, onStopSpeaking, onToggleTts,
}: {
    bank: QuestionBank;
    currentIndex: number;
    currentQuestion: Question;
    answers: Record<number, string>;
    allAnswered: boolean;
    answeredCount: number;
    isListening: boolean;
    canListen: boolean;
    submitting: boolean;
    submitError: string;
    isSpeaking: boolean;
    ttsEnabled: boolean;
    onAnswer: (id: number, value: string) => void;
    onNext: () => void;
    onPrev: () => void;
    onStartListening: () => void;
    onStopListening: () => void;
    onSpeak: (text: string) => void;
    onStopSpeaking: () => void;
    onToggleTts: (enabled: boolean) => void;
    onSubmit: () => void;
    onJumpTo: (index: number) => void;
}) {
    const total = bank.questions.length;
    const progress = ((currentIndex + 1) / total) * 100;
    const currentAnswer = answers[currentQuestion.id] ?? '';
    const isMultipleChoice = currentQuestion.options && currentQuestion.options.length > 0;

    return (
        <div className="space-y-6">
            {/* Progress header */}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 space-y-4">
                <div className="flex items-center justify-between text-sm font-medium text-slate-600">
                    <span>Question {currentIndex + 1} of {total}</span>
                    <span>{answeredCount}/{total} answered</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5">
                    <div
                        className="bg-gradient-to-r from-teal-500 to-emerald-500 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${progress}%` }}
                    />
                </div>
                {/* Quick-jump dots */}
                <div className="flex gap-1.5 flex-wrap">
                    {bank.questions.map((q, idx) => (
                        <button
                            key={q.id}
                            onClick={() => onJumpTo(idx)}
                            title={`Question ${idx + 1}`}
                            className={`w-6 h-6 rounded-full text-xs font-bold transition-all ${
                                idx === currentIndex
                                    ? 'bg-teal-600 text-white scale-110'
                                    : answers[q.id]?.trim()
                                    ? 'bg-emerald-200 text-emerald-800 hover:bg-emerald-300'
                                    : 'bg-slate-200 text-slate-500 hover:bg-slate-300'
                            }`}
                        >
                            {idx + 1}
                        </button>
                    ))}
                </div>
            </div>

            {/* Question card */}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                {/* Question header */}
                <div className="bg-gradient-to-r from-teal-600 to-emerald-600 px-6 py-5 text-white">
                    <div className="flex items-start justify-between gap-4">
                        <div>
                            <div className="text-teal-100 text-xs font-semibold uppercase tracking-wider mb-1">
                                {currentQuestion.question_type === 'multiple_choice' ? 'Multiple Choice' : 'Scenario / Open-ended'}
                            </div>
                            <h2 className="text-xl font-bold">{currentQuestion.title}</h2>
                        </div>
                        {currentQuestion.difficulty && (
                            <span className={`text-xs font-bold px-3 py-1 rounded-full flex-shrink-0 ${difficultyColor(currentQuestion.difficulty)}`}>
                                {currentQuestion.difficulty}
                            </span>
                        )}
                    </div>
                </div>

                <div className="p-6 space-y-6">
                    {/* Question text */}
                    <p className="text-slate-700 text-base leading-relaxed">
                        {currentQuestion.question_text}
                    </p>

                    {/* TTS Controls */}
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => isSpeaking ? onStopSpeaking() : onSpeak(currentQuestion.question_text)}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                                isSpeaking
                                    ? 'bg-red-50 text-red-600 hover:bg-red-100'
                                    : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                            }`}
                        >
                            {isSpeaking ? (
                                <><VolumeX className="w-4 h-4" /> Stop Reading</>
                            ) : (
                                <><Volume2 className="w-4 h-4" /> Read Aloud</>
                            )}
                        </button>
                        <label className="flex items-center gap-2 text-xs text-slate-500 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={ttsEnabled}
                                onChange={(e) => onToggleTts(e.target.checked)}
                                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                            />
                            Auto-read questions
                        </label>
                    </div>

                    {/* Answer input */}
                    {isMultipleChoice ? (
                        <div className="space-y-3">
                            {currentQuestion.options!.map((opt, i) => (
                                <label
                                    key={i}
                                    className={`flex items-center gap-3 p-3.5 rounded-xl border-2 cursor-pointer transition-all ${
                                        currentAnswer === opt
                                            ? 'border-teal-500 bg-teal-50'
                                            : 'border-slate-200 hover:border-teal-300 hover:bg-slate-50'
                                    }`}
                                >
                                    <input
                                        type="radio"
                                        name={`q-${currentQuestion.id}`}
                                        value={opt}
                                        checked={currentAnswer === opt}
                                        onChange={() => onAnswer(currentQuestion.id, opt)}
                                        className="accent-teal-600 w-4 h-4"
                                    />
                                    <span className="text-slate-700 text-sm">{opt}</span>
                                </label>
                            ))}
                        </div>
                    ) : (
                        <div className="space-y-3">
                            <textarea
                                value={currentAnswer}
                                onChange={e => onAnswer(currentQuestion.id, e.target.value)}
                                placeholder="Type your answer here, or use voice input below…"
                                rows={5}
                                className="w-full border border-slate-200 rounded-xl px-4 py-3 text-slate-700 focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition resize-none text-sm leading-relaxed"
                            />
                            {canListen && (
                                <button
                                    type="button"
                                    onClick={isListening ? onStopListening : onStartListening}
                                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm transition-all ${
                                        isListening
                                            ? 'bg-red-100 text-red-600 border-2 border-red-300 animate-pulse'
                                            : 'bg-teal-50 text-teal-700 border-2 border-teal-200 hover:bg-teal-100'
                                    }`}
                                >
                                    {isListening ? (
                                        <><MicOff className="w-4 h-4" /> Stop Recording</>
                                    ) : (
                                        <><Mic className="w-4 h-4" /> Record Answer</>
                                    )}
                                </button>
                            )}
                        </div>
                    )}

                    {/* Competencies hint */}
                    {currentQuestion.competencies && currentQuestion.competencies.length > 0 && (
                        <div className="text-xs text-slate-400 flex flex-wrap gap-1.5">
                            <span className="font-semibold">Competencies:</span>
                            {currentQuestion.competencies.map((c, i) => (
                                <span key={i} className="bg-slate-100 text-slate-500 px-2 py-0.5 rounded-md">{c}</span>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between gap-4">
                <button
                    onClick={onPrev}
                    disabled={currentIndex === 0}
                    className="flex items-center gap-2 px-5 py-3 rounded-xl border-2 border-slate-200 text-slate-600 font-semibold text-sm hover:border-slate-300 hover:bg-slate-50 transition disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    <ChevronLeft className="w-4 h-4" /> Previous
                </button>

                {currentIndex < bank.questions.length - 1 ? (
                    <button
                        onClick={onNext}
                        className="flex items-center gap-2 px-5 py-3 rounded-xl bg-teal-600 text-white font-semibold text-sm hover:bg-teal-700 transition shadow-sm shadow-teal-100"
                    >
                        Next <ChevronRight className="w-4 h-4" />
                    </button>
                ) : (
                    <button
                        onClick={onSubmit}
                        disabled={!allAnswered || submitting}
                        className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-bold text-sm hover:from-indigo-500 hover:to-violet-500 transition shadow-lg shadow-indigo-100 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                        {submitting ? (
                            <><Loader2 className="w-4 h-4 animate-spin" /> Submitting…</>
                        ) : (
                            <><Send className="w-4 h-4" /> Submit &amp; Get Results</>
                        )}
                    </button>
                )}
            </div>

            {!allAnswered && currentIndex === bank.questions.length - 1 && (
                <p className="text-center text-sm text-amber-600 font-medium">
                    Please answer all {bank.questions.length} questions before submitting. ({bank.questions.length - answeredCount} remaining)
                </p>
            )}

            {submitError && (
                <div className="flex items-center gap-3 text-red-600 bg-red-50 rounded-xl p-4 text-sm">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <span>Submission failed: {submitError}. Please try again.</span>
                </div>
            )}
        </div>
    );
}

// ─── Step 3: Results ──────────────────────────────────────────────────────────

function ResultsStep({
    results, bank, onTryAgain,
}: {
    results: BatchResult;
    bank: QuestionBank;
    onTryAgain: () => void;
}) {
    const scoreColor =
        results.score_percentage >= 80
            ? 'text-emerald-600'
            : results.score_percentage >= 60
            ? 'text-amber-600'
            : 'text-red-600';

    return (
        <div className="space-y-6">
            {/* Score summary */}
            <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-indigo-600 to-violet-600 rounded-3xl p-8 text-white shadow-xl shadow-indigo-100">
                <div className="absolute top-0 right-0 w-72 h-72 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
                <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <Trophy className="w-5 h-5 text-yellow-300" />
                            <span className="text-indigo-200 text-sm font-semibold uppercase tracking-wider">Interview Complete</span>
                        </div>
                        <h2 className="text-3xl font-bold mb-1">
                            {results.correct}/{results.total_questions} Correct
                        </h2>
                        <p className="text-indigo-200">
                            {bank.specialty.toUpperCase()} · {bank.band.replaceAll('_', ' ').toUpperCase()}
                        </p>
                    </div>
                    <div className="text-center">
                        <div className={`text-6xl font-black ${scoreColor} bg-white/10 rounded-2xl px-6 py-4`}>
                            {results.score_percentage}%
                        </div>
                    </div>
                </div>
            </div>

            {/* Per-question feedback */}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-teal-600" />
                    <h3 className="font-bold text-slate-800">Question-by-Question Feedback</h3>
                </div>
                <div className="divide-y divide-slate-100">
                    {results.per_question.map((r, idx) => (
                        <div key={r.question_id} className="p-5 space-y-2">
                            <div className="flex items-center gap-3">
                                {r.is_correct ? (
                                    <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                                ) : (
                                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                                )}
                                <span className="font-semibold text-slate-700 text-sm">
                                    Q{idx + 1}: {bank.questions[idx]?.title ?? `Question ${idx + 1}`}
                                </span>
                                <span className={`ml-auto text-xs font-bold px-2 py-0.5 rounded-full ${
                                    r.is_correct ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600'
                                }`}>
                                    {r.is_correct ? 'Correct' : 'Incorrect'}
                                </span>
                            </div>
                            <p className="text-slate-600 text-sm leading-relaxed pl-8">{r.feedback}</p>
                            {r.recommendations?.length > 0 && (
                                <div className="pl-8 space-y-1.5 mt-2">
                                    {r.recommendations.map((rec, i) => (
                                        <div key={i} className="text-xs text-slate-500 flex items-start gap-2">
                                            <BookOpen className="w-3.5 h-3.5 text-indigo-400 mt-0.5 flex-shrink-0" />
                                            <span><strong className="text-indigo-600">{rec.title}:</strong> {rec.summary}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Study plan */}
            {results.study_plan?.length > 0 && (
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
                        <BookOpen className="w-5 h-5 text-indigo-600" />
                        <h3 className="font-bold text-slate-800">Study Plan</h3>
                    </div>
                    <div className="p-6 space-y-4">
                        {results.study_plan.map((s, i) => (
                            <div key={i}>
                                <h4 className="font-semibold text-slate-700 text-sm mb-2">{s.title}</h4>
                                <ul className="space-y-1">
                                    {s.items.map((item, j) => (
                                        <li key={j} className="text-sm text-slate-600 flex items-start gap-2">
                                            <span className="text-teal-500 mt-0.5">•</span>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                        {results.next_steps && (
                            <div className="mt-4 p-4 bg-indigo-50 rounded-xl text-sm text-indigo-700">
                                <strong>Next steps:</strong> {results.next_steps}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4">
                <button
                    onClick={onTryAgain}
                    className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl border-2 border-teal-200 text-teal-700 font-bold hover:bg-teal-50 transition"
                >
                    <RotateCcw className="w-4 h-4" /> Try Again
                </button>
                <Link
                    href="/dashboard"
                    className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-bold hover:from-indigo-500 hover:to-violet-500 transition shadow-lg shadow-indigo-100"
                >
                    <Activity className="w-4 h-4" /> Back to Dashboard
                </Link>
            </div>
        </div>
    );
}
