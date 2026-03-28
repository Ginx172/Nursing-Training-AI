import React, { useState, useEffect } from 'react';
import api from '../../lib/api';
import { BookOpen, GraduationCap, ChevronRight, FileText, CheckCircle, Brain, AlertCircle, Loader2 } from 'lucide-react';

interface Question {
    id: number;
    question: string;
    options: string[];
    correctAnswer: string;
}

interface QuizData {
    topic: string;
    questions: Question[];
}

const StudyZone = () => {
    const [topics, setTopics] = useState<string[]>([]);
    const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'materials' | 'quiz'>('materials');
    const [quizData, setQuizData] = useState<QuizData | null>(null);
    const [loading, setLoading] = useState(false);

    // Quiz state
    const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
    const [userAnswers, setUserAnswers] = useState<{ [key: number]: string }>({});
    const [showResults, setShowResults] = useState(false);
    const [generatingQuiz, setGeneratingQuiz] = useState(false);

    useEffect(() => {
        fetchTopics();
    }, []);

    const fetchTopics = async () => {
        try {
            setLoading(true);
            const response = await api.get('/study/topics');
            setTopics(response.data);
        } catch (err) {
            console.error("Error fetching topics:", err);
            // Fallback for demo if API fails
            setTopics(["Anatomy", "Medication Administration", "Patient Safety", "Clinical Assessment"]);
        } finally {
            setLoading(false);
        }
    };

    const handleTopicSelect = (topic: string) => {
        setSelectedTopic(topic);
        setActiveTab('materials');
        setQuizData(null);
        setShowResults(false);
        setUserAnswers({});
        setCurrentQuestionIdx(0);
    };

    const generateQuiz = async () => {
        if (!selectedTopic) return;
        try {
            setGeneratingQuiz(true);
            const response = await api.post('/study/quiz', {
                topic: selectedTopic,
                difficulty: 'medium',
                question_count: 5
            });
            setQuizData(response.data);
            setActiveTab('quiz');
        } catch (err) {
            console.error("Error generating quiz:", err);
            // Fallback mock quiz
            setQuizData({
                topic: selectedTopic,
                questions: [
                    {
                        id: 1,
                        question: "What is the primary sign of hypovolemic shock?",
                        options: ["Hypertension", "Tachycardia", "Bradycardia", "Hyperthermia"],
                        correctAnswer: "Tachycardia"
                    },
                    {
                        id: 2,
                        question: "Which verification check is mandatory before blood transfusion?",
                        options: ["Patient ID & Blood Type", "Only Patient Name", "Only Blood Type", "Room Number"],
                        correctAnswer: "Patient ID & Blood Type"
                    },
                    {
                        id: 3,
                        question: "When administering IV potassium, you should NEVER:",
                        options: ["Dilute it", "Give it as a bolus push", "Monitor ECG", "Check renal function"],
                        correctAnswer: "Give it as a bolus push"
                    }
                ]
            });
            setActiveTab('quiz');
        } finally {
            setGeneratingQuiz(false);
        }
    };

    const calculateScore = () => {
        if (!quizData) return 0;
        let correct = 0;
        quizData.questions.forEach(q => {
            if (userAnswers[q.id] === q.correctAnswer) correct++;
        });
        return Math.round((correct / quizData.questions.length) * 100);
    };

    return (
        <div className="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden flex flex-col h-[700px]">
            {/* Header */}
            <div className="bg-gradient-to-r from-violet-600 to-indigo-600 px-8 py-6 text-white flex justify-between items-center shadow-lg z-10">
                <div className="flex items-center space-x-4">
                    <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                        <BookOpen className="h-8 w-8 text-white" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">AI Study Zone</h2>
                        <p className="text-indigo-100 text-sm font-medium">Personalized Knowledge Base & Testing</p>
                    </div>
                </div>
                {selectedTopic && (
                    <div className="flex items-center space-x-3 bg-white/10 px-4 py-2 rounded-lg border border-white/20">
                        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                        <span className="font-semibold px-2">{selectedTopic}</span>
                    </div>
                )}
            </div>

            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <div className="w-72 bg-slate-50/80 border-r border-slate-200 flex flex-col backdrop-blur-sm">
                    <div className="p-4 border-b border-slate-200 bg-slate-100/50">
                        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Knowledge Base</h3>
                        <p className="text-xs text-slate-500">Select a topic to begin</p>
                    </div>
                    <div className="flex-1 overflow-y-auto p-3 space-y-2">
                        {loading ? (
                            <div className="space-y-3 p-2">
                                {[1, 2, 3, 4].map(i => <div key={i} className="h-10 bg-slate-200 animate-pulse rounded-lg"></div>)}
                            </div>
                        ) : (
                            topics.map((topic) => (
                                <button
                                    key={topic}
                                    onClick={() => handleTopicSelect(topic)}
                                    className={`w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 flex items-center justify-between group
                                    ${selectedTopic === topic
                                            ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                                            : 'text-slate-600 hover:bg-white hover:shadow-sm hover:text-indigo-600 border border-transparent hover:border-slate-200'}`}
                                >
                                    <span className="truncate">{topic}</span>
                                    <ChevronRight className={`h-4 w-4 transition-transform ${selectedTopic === topic ? 'text-indigo-200' : 'text-slate-300 group-hover:text-indigo-400'}`} />
                                </button>
                            ))
                        )}
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 bg-slate-50/30 p-8 overflow-y-auto">
                    {!selectedTopic ? (
                        <div className="h-full flex flex-col items-center justify-center text-center">
                            <div className="bg-white p-6 rounded-full shadow-lg mb-6 animate-bounce">
                                <Brain className="h-16 w-16 text-indigo-500" />
                            </div>
                            <h3 className="text-3xl font-bold text-slate-800 mb-3">Welcome to Study Zone</h3>
                            <p className="text-slate-500 max-w-md text-lg leading-relaxed">
                                Select a topic from the sidebar to access AI-curated study materials and generate personalized quizzes.
                            </p>
                        </div>
                    ) : (
                        <div className="max-w-4xl mx-auto h-full flex flex-col">
                            {/* Tabs */}
                            <div className="flex space-x-2 bg-white p-1 rounded-xl shadow-sm border border-slate-200 mb-8 w-fit">
                                <button
                                    onClick={() => setActiveTab('materials')}
                                    className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 flex items-center space-x-2
                                    ${activeTab === 'materials'
                                            ? 'bg-indigo-50 text-indigo-700 shadow-sm ring-1 ring-indigo-200'
                                            : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'}`}
                                >
                                    <FileText className="h-4 w-4" />
                                    <span>Study Materials</span>
                                </button>
                                <button
                                    onClick={() => setActiveTab('quiz')}
                                    className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 flex items-center space-x-2
                                    ${activeTab === 'quiz'
                                            ? 'bg-indigo-50 text-indigo-700 shadow-sm ring-1 ring-indigo-200'
                                            : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'}`}
                                >
                                    <GraduationCap className="h-4 w-4" />
                                    <span>Knowledge Check</span>
                                </button>
                            </div>

                            {/* Materials Content */}
                            {activeTab === 'materials' && (
                                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 rounded-2xl p-6 flex items-start gap-4 shadow-sm">
                                        <div className="p-3 bg-blue-100/50 rounded-xl">
                                            <Brain className="h-6 w-6 text-blue-600" />
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-bold text-blue-900 mb-1">AI Learning Path: {selectedTopic}</h3>
                                            <p className="text-blue-700/80 text-sm leading-relaxed">
                                                Based on our document analysis, these are the critical concepts you need to master for <strong>{selectedTopic}</strong>.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {[1, 2, 3, 4].map((i) => (
                                            <div key={i} className="bg-white p-5 rounded-2xl border border-slate-100 shadow-md hover:shadow-xl hover:border-indigo-100 transition-all duration-300 cursor-pointer group">
                                                <div className="flex items-start justify-between mb-4">
                                                    <div className="p-3 bg-slate-50 rounded-xl group-hover:bg-indigo-50 transition-colors">
                                                        <FileText className="h-6 w-6 text-slate-400 group-hover:text-indigo-600" />
                                                    </div>
                                                    <span className="px-2.5 py-1 bg-slate-100 text-slate-500 text-xs font-bold rounded-md uppercase tracking-wide">PDF</span>
                                                </div>
                                                <h4 className="text-lg font-bold text-slate-800 mb-2 group-hover:text-indigo-600 transition-colors">Clinical Guideline {i}</h4>
                                                <p className="text-sm text-slate-500 line-clamp-2 leading-relaxed">
                                                    Standard operating procedures and safety protocols regarding {selectedTopic.toLowerCase()}.
                                                </p>
                                                <div className="mt-4 pt-4 border-t border-slate-50 flex items-center text-xs font-medium text-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    View Document <ChevronRight className="h-3 w-3 ml-1" />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="text-center pt-4">
                                        <button
                                            onClick={generateQuiz}
                                            className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl shadow-lg hover:shadow-indigo-200 hover:scale-105 transition-all duration-300 font-semibold inline-flex items-center"
                                        >
                                            <GraduationCap className="mr-2 h-5 w-5" />
                                            Take Practice Quiz
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Quiz Content */}
                            {activeTab === 'quiz' && (
                                <div className="h-full animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    {!quizData ? (
                                        <div className="h-[400px] flex flex-col items-center justify-center bg-white rounded-3xl border border-slate-100 shadow-sm">
                                            {generatingQuiz ? (
                                                <>
                                                    <div className="relative mb-6">
                                                        <div className="w-16 h-16 border-4 border-indigo-100 border-t-indigo-500 rounded-full animate-spin"></div>
                                                        <Brain className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-6 w-6 text-indigo-500 animate-pulse" />
                                                    </div>
                                                    <h3 className="text-lg font-bold text-slate-800">Generating Quiz...</h3>
                                                    <p className="text-slate-400 mt-2">Analyzing knowledge base chunks</p>
                                                </>
                                            ) : (
                                                <div className="text-center max-w-sm">
                                                    <div className="w-20 h-20 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-6">
                                                        <GraduationCap className="h-10 w-10 text-indigo-500" />
                                                    </div>
                                                    <h3 className="text-xl font-bold text-slate-800 mb-2">Ready to test?</h3>
                                                    <p className="text-slate-500 mb-8 leading-relaxed">We'll generate 5 questions based on the materials for <strong>{selectedTopic}</strong>.</p>
                                                    <button
                                                        onClick={generateQuiz}
                                                        className="w-full px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition shadow-lg hover:shadow-indigo-200"
                                                    >
                                                        Start Assessment
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    ) : showResults ? (
                                        <div className="bg-white rounded-3xl shadow-sm border border-slate-100 p-8 text-center">
                                            <div className="inline-flex items-center justify-center p-6 bg-green-50 rounded-full mb-6 ring-8 ring-green-50/50">
                                                <CheckCircle className="h-12 w-12 text-green-500" />
                                            </div>
                                            <h3 className="text-3xl font-extrabold text-slate-800 mb-2">Assessment Complete!</h3>
                                            <p className="text-slate-500 mb-8">You scored <span className="font-extrabold text-indigo-600 text-2xl ml-1">{calculateScore()}%</span></p>

                                            <div className="max-w-2xl mx-auto space-y-4 text-left mb-8">
                                                {quizData.questions.map((q, idx) => (
                                                    <div key={q.id} className={`p-6 rounded-xl border-l-4 ${userAnswers[q.id] === q.correctAnswer ? 'bg-green-50/50 border-green-500' : 'bg-red-50/50 border-red-500'}`}>
                                                        <p className="font-bold text-slate-800 mb-3 text-lg">{idx + 1}. {q.question}</p>
                                                        <div className="flex items-center justify-between text-sm bg-white p-3 rounded-lg border border-slate-100">
                                                            <span className={`font-semibold ${userAnswers[q.id] === q.correctAnswer ? 'text-green-700' : 'text-red-700'}`}>
                                                                Your answer: {userAnswers[q.id]}
                                                            </span>
                                                            {userAnswers[q.id] !== q.correctAnswer && (
                                                                <span className="text-green-700 font-bold bg-green-50 px-3 py-1 rounded-md">Correct: {q.correctAnswer}</span>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>

                                            <button
                                                onClick={() => { setQuizData(null); setShowResults(false); }}
                                                className="px-8 py-3 bg-white border border-slate-200 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition shadow-sm"
                                            >
                                                Return to Materials
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="max-w-2xl mx-auto h-full flex flex-col justify-center">
                                            <div className="mb-8 p-4 bg-white rounded-xl shadow-sm border border-slate-100">
                                                <div className="flex justify-between items-center text-sm font-semibold text-slate-400 mb-2">
                                                    <span>Question {currentQuestionIdx + 1}/{quizData.questions.length}</span>
                                                    <span>{Math.round((currentQuestionIdx / quizData.questions.length) * 100)}%</span>
                                                </div>
                                                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                                                    <div className="h-full bg-indigo-500 transition-all duration-500 ease-out" style={{ width: `${(currentQuestionIdx / quizData.questions.length) * 100}%` }}></div>
                                                </div>
                                            </div>

                                            <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 mb-8 relative overflow-hidden">
                                                <div className="absolute top-0 left-0 w-2 h-full bg-indigo-500"></div>
                                                <h3 className="text-2xl font-bold text-slate-800 mb-8 leading-snug">{quizData.questions[currentQuestionIdx].question}</h3>
                                                <div className="space-y-4">
                                                    {quizData.questions[currentQuestionIdx].options.map((option) => (
                                                        <button
                                                            key={option}
                                                            onClick={() => setUserAnswers({ ...userAnswers, [quizData.questions[currentQuestionIdx].id]: option })}
                                                            className={`w-full text-left p-5 rounded-2xl border-2 transition-all duration-200 flex items-center group
                                                            ${userAnswers[quizData.questions[currentQuestionIdx].id] === option
                                                                    ? 'border-indigo-500 bg-indigo-50/50 text-indigo-900'
                                                                    : 'border-slate-100 hover:border-indigo-200 hover:bg-slate-50 text-slate-600'}`}
                                                        >
                                                            <div className={`w-6 h-6 rounded-full border-2 mr-4 flex items-center justify-center transition-colors
                                                                ${userAnswers[quizData.questions[currentQuestionIdx].id] === option ? 'border-indigo-500 bg-indigo-500' : 'border-slate-300 group-hover:border-indigo-300'}`}>
                                                                {userAnswers[quizData.questions[currentQuestionIdx].id] === option && <div className="w-2 h-2 bg-white rounded-full"></div>}
                                                            </div>
                                                            <span className="font-medium text-lg">{option}</span>
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>

                                            <div className="flex justify-between items-center px-4">
                                                <button disabled={currentQuestionIdx === 0} onClick={() => setCurrentQuestionIdx(c => c - 1)} className="px-6 py-2 text-slate-400 font-semibold disabled:opacity-30 hover:text-slate-600">Previous</button>
                                                {currentQuestionIdx < quizData.questions.length - 1 ? (
                                                    <button onClick={() => setCurrentQuestionIdx(c => c + 1)} className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition shadow-lg">Next Question</button>
                                                ) : (
                                                    <button onClick={() => setShowResults(true)} className="px-8 py-3 bg-green-500 text-white rounded-xl font-bold hover:bg-green-600 transition shadow-lg">Complete Quiz</button>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StudyZone;
