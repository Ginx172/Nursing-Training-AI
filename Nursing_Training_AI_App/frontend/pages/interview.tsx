import React, { useState, useEffect, useRef, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
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
    question_title: string;
    question_text: string;
    user_answer: string;
    is_correct: boolean;
    score: number;
    max_score: number;
    feedback: string;
    strengths: string[];
    weaknesses: string[];
    ideal_answer: string;
    recommendations?: { title: string; summary: string; url?: string | null }[];
}

interface BatchResult {
    total_questions: number;
    correct: number;
    score_percentage: number;
    total_score: number;
    total_possible: number;
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
    const [speechRate, setSpeechRate] = useState(1.0);
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

    const speakQuestion = useCallback((text: string) => {
        if (typeof window === 'undefined' || !window.speechSynthesis || !ttsEnabled) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-GB';
        utterance.rate = speechRate;
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
    }, [ttsEnabled, speechRate]);

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
                    api.get('/api/questions/bands'),
                    api.get('/api/questions/specialties'),
                ]);
                setBands(bRes.data);
                setSpecialties(sRes.data);
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
            const res = await api.get(`/api/questions/bank/${selectedSpecialty}/${selectedBand}`);
            const data: QuestionBank = res.data;
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
                band: bank.band,
                specialty: bank.specialty,
                answers: bank.questions.map(q => ({
                    question_id: q.id,
                    question_text: q.question_text,
                    question_title: q.title,
                    user_answer: (answers[q.id] ?? '').trim(),
                    correct_answer: q.correct_answer ?? '',
                    expected_points: q.expected_points ?? [],
                })),
            };
            const res = await api.post('/api/questions/submit-interview', payload);
            const data: BatchResult = res.data;
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
        <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 text-slate-900 font-sans">
            <Head>
                <title>Interview | Nursing Training AI</title>
            </Head>

            {/* Top Navigation */}
            <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-xl border-b border-indigo-100 px-6 py-4 flex items-center gap-4 shadow-md shadow-indigo-50">
                <Link href="/dashboard" className="flex items-center gap-2 text-slate-500 hover:text-indigo-600 transition font-medium text-sm">
                    <LayoutDashboard className="w-4 h-4" />
                    Dashboard
                </Link>
                <ChevronRight className="w-4 h-4 text-slate-300" />
                <span className="text-indigo-700 font-bold text-sm flex items-center gap-2">
                    <Mic className="w-4 h-4 text-indigo-500" />
                    Interview Practice
                </span>
                {step === 'questions' && (
                    <div className="ml-auto flex items-center gap-2 bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-full text-sm font-bold">
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
                        speechRate={speechRate}
                        onSpeechRateChange={setSpeechRate}
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
        </ProtectedRoute>
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
            {/* Hero */}
            <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 rounded-3xl p-10 text-white shadow-2xl">
                <div className="absolute top-0 right-0 w-72 h-72 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full blur-2xl translate-y-1/3 -translate-x-1/4 pointer-events-none" />
                <div className="absolute top-1/2 left-1/3 w-32 h-32 bg-pink-400/10 rounded-full blur-2xl pointer-events-none" />
                <div className="relative z-10">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-white/20 rounded-2xl backdrop-blur-sm border border-white/10 shadow-lg">
                            <BookOpen className="w-7 h-7" />
                        </div>
                        <h1 className="text-3xl font-black tracking-tight">Clinical Interview Practice</h1>
                    </div>
                    <p className="text-blue-100 max-w-xl text-base leading-relaxed">
                        Select your NHS band and specialty to begin an AI-powered clinical interview.
                        Questions are tailored to your level and read aloud by the AI interviewer.
                    </p>
                </div>
            </div>

            {/* Selection Card */}
            <div className="bg-white rounded-2xl shadow-lg shadow-indigo-50 border border-indigo-100 p-8 space-y-8">
                {loading && (
                    <div className="flex items-center gap-3 text-slate-500">
                        <Loader2 className="w-5 h-5 animate-spin text-indigo-600" />
                        <span>Loading configuration...</span>
                    </div>
                )}
                {error && (
                    <div className="flex items-center gap-3 text-red-700 bg-red-50 rounded-xl p-4 border border-red-200">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                {!loading && !error && (
                    <>
                        {/* Band Selection - Card Grid */}
                        <div className="space-y-4">
                            <label className="text-base font-bold text-slate-800 block">
                                Select Your NHS Band
                            </label>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                {bands.map(b => (
                                    <button
                                        key={b.id}
                                        onClick={() => onBandChange(b.id)}
                                        className={`text-left px-5 py-4 rounded-xl border-2 transition-all duration-200 hover:scale-[1.03] ${
                                            selectedBand === b.id
                                                ? 'border-indigo-500 bg-indigo-50 ring-2 ring-indigo-500 shadow-lg shadow-indigo-100'
                                                : 'border-slate-200 bg-white text-slate-700 hover:border-indigo-300 hover:shadow-lg'
                                        }`}
                                    >
                                        <div className="font-bold text-sm">{b.name}</div>
                                        <div className="text-xs text-slate-500 mt-1">{b.description}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Specialty Selection - Card Grid */}
                        <div className="space-y-4">
                            <label className="text-base font-bold text-slate-800 block">
                                Select Your Specialty
                            </label>
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                {specialties.map(s => (
                                    <button
                                        key={s.id}
                                        onClick={() => onSpecialtyChange(s.id)}
                                        className={`text-left px-5 py-4 rounded-xl border-2 transition-all duration-200 hover:scale-[1.03] ${
                                            selectedSpecialty === s.id
                                                ? 'border-indigo-500 bg-indigo-50 ring-2 ring-indigo-500 shadow-lg shadow-indigo-100'
                                                : 'border-slate-200 bg-white text-slate-700 hover:border-indigo-300 hover:shadow-lg'
                                        }`}
                                    >
                                        <div className="font-bold text-sm">{s.name}</div>
                                        <div className="text-xs text-slate-500 mt-1">{s.description}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {bankError && (
                            <div className="flex items-center gap-3 text-red-700 bg-red-50 rounded-xl p-4 border border-red-200">
                                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                <span>Could not load questions: {bankError}. Try a different band/specialty combination.</span>
                            </div>
                        )}

                        <div className="flex flex-col items-center">
                            <button
                                onClick={onStart}
                                disabled={!selectedBand || !selectedSpecialty || bankLoading}
                                className="w-full max-w-md bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 text-white py-4 rounded-xl font-bold text-lg shadow-xl hover:shadow-2xl hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-3"
                            >
                                {bankLoading ? (
                                    <><Loader2 className="w-5 h-5 animate-spin" /> Loading Questions...</>
                                ) : (
                                    <>Begin Interview <ChevronRight className="w-5 h-5" /></>
                                )}
                            </button>
                            <p className="text-xs text-slate-400 mt-3">15 randomized questions tailored to your level</p>
                        </div>
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
    isSpeaking, ttsEnabled, speechRate,
    onAnswer, onNext, onPrev, onStartListening, onStopListening, onSubmit, onJumpTo,
    onSpeak, onStopSpeaking, onToggleTts, onSpeechRateChange,
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
    speechRate: number;
    onAnswer: (id: number, value: string) => void;
    onNext: () => void;
    onPrev: () => void;
    onStartListening: () => void;
    onStopListening: () => void;
    onSpeak: (text: string) => void;
    onStopSpeaking: () => void;
    onToggleTts: (enabled: boolean) => void;
    onSpeechRateChange: (rate: number) => void;
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
            <div className="bg-white rounded-2xl border border-indigo-100 shadow-lg shadow-indigo-50 p-6 space-y-4">
                <div className="flex items-center justify-between text-sm font-semibold text-slate-700">
                    <span>Question {currentIndex + 1} of {total}</span>
                    <span className="text-indigo-600">{answeredCount}/{total} answered</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3">
                    <div
                        className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500 shadow-sm"
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
                            className={`w-7 h-7 rounded-full text-xs font-bold transition-all ${
                                idx === currentIndex
                                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200 scale-110'
                                    : answers[q.id]?.trim()
                                    ? 'bg-emerald-400 text-white hover:bg-emerald-500'
                                    : 'bg-slate-200 text-slate-500 hover:bg-slate-300'
                            }`}
                        >
                            {idx + 1}
                        </button>
                    ))}
                </div>
            </div>

            {/* Question card */}
            <div className="bg-white rounded-2xl border border-indigo-100 shadow-lg shadow-indigo-50 overflow-hidden">
                {/* Question header */}
                <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 px-6 py-6 text-white">
                    <div className="flex items-start justify-between gap-4">
                        <div>
                            <div className="text-indigo-200 text-xs font-semibold uppercase tracking-wider mb-1.5">
                                {currentQuestion.question_type === 'multiple_choice' ? 'Multiple Choice' : 'Scenario / Open-ended'}
                            </div>
                            <h2 className="text-xl font-bold">{currentQuestion.title}</h2>
                        </div>
                        {currentQuestion.difficulty && (
                            <span className={`text-sm font-bold px-4 py-1.5 rounded-full flex-shrink-0 border border-white/20 ${difficultyColor(currentQuestion.difficulty)}`}>
                                {currentQuestion.difficulty}
                            </span>
                        )}
                    </div>
                </div>

                <div className="p-6 space-y-6">
                    {/* Question text */}
                    <p className="text-slate-700 text-lg leading-relaxed border-l-4 border-indigo-300 pl-4">
                        {currentQuestion.question_text}
                    </p>

                    {/* TTS Controls */}
                    <div className="flex flex-wrap items-center gap-3 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
                        <button
                            onClick={() => isSpeaking ? onStopSpeaking() : onSpeak(currentQuestion.question_text)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-sm ${
                                isSpeaking
                                    ? 'bg-red-500 text-white hover:bg-red-600'
                                    : 'bg-indigo-600 text-white hover:bg-indigo-700'
                            }`}
                        >
                            {isSpeaking ? (
                                <><VolumeX className="w-4 h-4" /> Stop</>
                            ) : (
                                <><Volume2 className="w-4 h-4" /> Read Aloud</>
                            )}
                        </button>
                        <button
                            onClick={() => onSpeak(currentQuestion.question_text)}
                            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold bg-purple-100 text-purple-700 hover:bg-purple-200 transition-all"
                        >
                            <RotateCcw className="w-3.5 h-3.5" /> Repeat
                        </button>
                        <label className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer ml-auto">
                            <input
                                type="checkbox"
                                checked={ttsEnabled}
                                onChange={(e) => onToggleTts(e.target.checked)}
                                className="rounded border-indigo-300 text-indigo-600 focus:ring-indigo-500"
                            />
                            Auto-read
                        </label>
                        <div className="flex items-center gap-2 text-xs text-slate-600">
                            <span>Speed:</span>
                            <input
                                type="range"
                                min="0.5"
                                max="2"
                                step="0.1"
                                value={speechRate}
                                onChange={(e) => onSpeechRateChange(parseFloat(e.target.value))}
                                className="w-20 h-1.5 accent-indigo-600"
                            />
                            <span className="font-semibold text-indigo-700 w-8">{speechRate}x</span>
                        </div>
                    </div>

                    {/* Answer input */}
                    {isMultipleChoice ? (
                        <div className="space-y-3">
                            {currentQuestion.options!.map((opt, i) => (
                                <label
                                    key={i}
                                    className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                                        currentAnswer === opt
                                            ? 'border-indigo-500 bg-indigo-50 shadow-md shadow-indigo-50'
                                            : 'border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50'
                                    }`}
                                >
                                    <input
                                        type="radio"
                                        name={`q-${currentQuestion.id}`}
                                        value={opt}
                                        checked={currentAnswer === opt}
                                        onChange={() => onAnswer(currentQuestion.id, opt)}
                                        className="accent-indigo-600 w-4 h-4"
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
                                placeholder="Type your answer here, or use voice input below..."
                                rows={5}
                                className="w-full border-2 border-indigo-200 rounded-xl px-4 py-3 text-slate-700 focus:ring-2 focus:ring-indigo-200 focus:border-indigo-500 outline-none transition resize-none text-sm leading-relaxed min-h-[120px]"
                            />
                            {canListen && (
                                <button
                                    type="button"
                                    onClick={isListening ? onStopListening : onStartListening}
                                    className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm transition-all shadow-sm ${
                                        isListening
                                            ? 'bg-red-500 text-white border-2 border-red-400 animate-pulse shadow-red-100'
                                            : 'bg-gradient-to-r from-teal-500 to-emerald-500 text-white hover:from-teal-600 hover:to-emerald-600 shadow-teal-100'
                                    }`}
                                >
                                    {isListening ? (
                                        <><MicOff className="w-4 h-4" /> Stop Recording</>
                                    ) : (
                                        <><Mic className="w-4 h-4" /> Record Answer</>
                                    )}
                                </button>
                            )}
                            {currentAnswer.trim() && (
                                <button
                                    type="button"
                                    onClick={currentIndex < bank.questions.length - 1 ? onNext : undefined}
                                    disabled={!currentAnswer.trim()}
                                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold text-sm hover:from-emerald-600 hover:to-teal-600 transition shadow-md shadow-emerald-100"
                                >
                                    <Send className="w-4 h-4" />
                                    {currentIndex < bank.questions.length - 1 ? 'Confirm & Next' : 'Answer Saved'}
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
                    className="flex items-center gap-2 px-5 py-3 rounded-xl border-2 border-indigo-200 text-indigo-700 font-semibold text-sm hover:bg-indigo-50 transition disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    <ChevronLeft className="w-4 h-4" /> Previous
                </button>

                {currentIndex < bank.questions.length - 1 ? (
                    <button
                        onClick={onNext}
                        className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-sm hover:from-indigo-700 hover:to-purple-700 transition shadow-lg shadow-indigo-100"
                    >
                        Next <ChevronRight className="w-4 h-4" />
                    </button>
                ) : (
                    <button
                        onClick={onSubmit}
                        disabled={submitting}
                        className="flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 text-white font-black text-base hover:from-emerald-500 hover:via-teal-500 hover:to-cyan-500 transition shadow-xl shadow-emerald-100 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                        {submitting ? (
                            <><Loader2 className="w-5 h-5 animate-spin" /> Submitting...</>
                        ) : (
                            <><Send className="w-5 h-5" /> Submit &amp; Get Results</>
                        )}
                    </button>
                )}
            </div>

            {answeredCount < total && currentIndex === bank.questions.length - 1 && (
                <p className="text-center text-sm text-amber-600 font-medium">
                    {answeredCount} of {total} questions answered. You can still submit.
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
            <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-3xl p-10 text-white shadow-2xl shadow-indigo-200">
                <div className="absolute top-0 right-0 w-72 h-72 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full blur-2xl translate-y-1/3 -translate-x-1/4 pointer-events-none" />
                <div className="absolute top-1/3 left-1/2 w-36 h-36 bg-white/5 rounded-full blur-xl pointer-events-none" />
                <div className="absolute bottom-4 right-16 w-20 h-20 bg-white/10 rounded-full blur-lg pointer-events-none" />
                <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <Trophy className="w-6 h-6 text-yellow-300" />
                            <span className="text-purple-200 text-sm font-bold uppercase tracking-wider">Interview Complete</span>
                        </div>
                        <h2 className="text-3xl font-black mb-2">
                            {results.correct}/{results.total_questions} Correct
                        </h2>
                        <p className="text-purple-200 text-base">
                            {bank.specialty.toUpperCase()} · {bank.band.replaceAll('_', ' ').toUpperCase()}
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="w-32 h-32 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center shadow-lg shadow-white/10 border border-white/20">
                            <span className={`text-7xl font-black ${scoreColor}`}>
                                {results.score_percentage}<span className="text-3xl">%</span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Per-question detailed feedback */}
            <div className="space-y-4">
                <div className="flex items-center gap-2 px-1">
                    <CheckCircle className="w-5 h-5 text-indigo-600" />
                    <h3 className="font-bold text-slate-800 text-lg">Detailed Feedback per Question</h3>
                </div>
                {results.per_question.map((r, idx) => (
                    <div key={r.question_id} className={`bg-white rounded-2xl shadow-md overflow-hidden ${
                        r.is_correct ? 'border-l-4 border-emerald-500' : 'border-l-4 border-red-400'
                    }`}>
                        {/* Question header with score */}
                        <div className={`px-6 py-4 flex items-center justify-between ${
                            r.is_correct ? 'bg-gradient-to-r from-emerald-50 to-green-50' : 'bg-gradient-to-r from-red-50 to-orange-50'
                        }`}>
                            <div className="flex items-center gap-3">
                                {r.is_correct ? (
                                    <CheckCircle className="w-6 h-6 text-emerald-500" />
                                ) : (
                                    <AlertCircle className="w-6 h-6 text-red-400" />
                                )}
                                <div>
                                    <span className="font-bold text-slate-800">Q{idx + 1}: {r.question_title || `Question ${idx + 1}`}</span>
                                    <p className="text-xs text-slate-500 mt-0.5">{r.question_text}</p>
                                </div>
                            </div>
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-sm font-black ${
                                r.score >= 8 ? 'bg-gradient-to-br from-emerald-400 to-green-500 text-white' :
                                r.score >= 5 ? 'bg-gradient-to-br from-amber-400 to-orange-500 text-white' :
                                'bg-gradient-to-br from-red-400 to-rose-500 text-white'
                            }`}>
                                {r.score}/{r.max_score}
                            </div>
                        </div>

                        <div className="p-6 space-y-4">
                            {/* AI Feedback */}
                            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                                <p className="text-sm text-blue-800 font-medium">{r.feedback}</p>
                            </div>

                            {/* Your answer */}
                            <div>
                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Your Answer</h4>
                                <p className="text-sm text-slate-700 bg-slate-50 rounded-lg p-3 border-l-4 border-slate-300">{r.user_answer}</p>
                            </div>

                            {/* Strengths */}
                            {r.strengths && r.strengths.length > 0 && (
                                <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
                                    <h4 className="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-2">What you did well</h4>
                                    <ul className="space-y-1.5">
                                        {r.strengths.map((s, i) => (
                                            <li key={i} className="text-sm text-emerald-700 flex items-start gap-2">
                                                <CheckCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" /> {s}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Weaknesses */}
                            {r.weaknesses && r.weaknesses.length > 0 && (
                                <div className="bg-red-50 rounded-xl p-4 border border-red-100">
                                    <h4 className="text-xs font-bold text-red-600 uppercase tracking-wider mb-2">Areas to improve</h4>
                                    <ul className="space-y-1.5">
                                        {r.weaknesses.map((w, i) => (
                                            <li key={i} className="text-sm text-red-600 flex items-start gap-2">
                                                <AlertCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" /> {w}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Ideal answer */}
                            {r.ideal_answer && (
                                <div className="border-t border-slate-100 pt-4">
                                    <h4 className="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                                        <BookOpen className="w-3.5 h-3.5" /> Model / Ideal Answer
                                    </h4>
                                    <p className="text-sm text-indigo-800 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 leading-relaxed border border-indigo-100">{r.ideal_answer}</p>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Study plan */}
            {results.study_plan?.length > 0 && (
                <div className="bg-white rounded-2xl border border-indigo-100 shadow-lg shadow-indigo-50 overflow-hidden">
                    <div className="px-6 py-4 border-b border-indigo-100 flex items-center gap-2 bg-gradient-to-r from-indigo-50 to-purple-50">
                        <BookOpen className="w-5 h-5 text-indigo-600" />
                        <h3 className="font-bold text-indigo-800">Study Plan</h3>
                    </div>
                    <div className="p-6 space-y-4">
                        {results.study_plan.map((s, i) => (
                            <div key={i}>
                                <h4 className="font-semibold text-slate-700 text-sm mb-2">{s.title}</h4>
                                <ul className="space-y-1.5">
                                    {s.items.map((item, j) => (
                                        <li key={j} className="text-sm text-slate-600 flex items-start gap-2">
                                            <span className="text-indigo-500 mt-0.5 font-bold">*</span>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                        {results.next_steps && (
                            <div className="mt-4 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl text-sm text-indigo-700 border border-indigo-100">
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
                    className="flex-1 flex items-center justify-center gap-2 py-4 rounded-xl border-2 border-indigo-300 text-indigo-700 font-bold text-base hover:bg-indigo-50 hover:border-indigo-400 transition-all"
                >
                    <RotateCcw className="w-5 h-5" /> Try Again
                </button>
                <Link
                    href="/dashboard"
                    className="flex-1 flex items-center justify-center gap-2 py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-base hover:from-indigo-500 hover:to-purple-500 transition-all shadow-lg shadow-indigo-200"
                >
                    <Activity className="w-5 h-5" /> Back to Dashboard
                </Link>
            </div>
        </div>
    );
}
