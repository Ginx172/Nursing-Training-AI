import React, { useState, useRef, useEffect } from 'react';
import { Mic, Play, Square, Loader2, CheckCircle, Volume2, User, Bot, RotateCcw, FastForward, Send, Keyboard, Pause } from 'lucide-react';

const InterviewMode = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [feedback, setFeedback] = useState<any>(null);
    const [transcript, setTranscript] = useState<any[]>([
        { role: 'ai', text: "Hello! I'm your AI Clinical Interviewer. I'll be asking you a series of scenario-based questions to assess your clinical reasoning and communication skills. Are you ready to begin?" }
    ]);

    // Text Input State
    const [isTyping, setIsTyping] = useState(false);
    const [textInput, setTextInput] = useState("");

    // Audio Controls State
    const [isPlaying, setIsPlaying] = useState(false);
    const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
    const speechRef = useRef<SpeechSynthesisUtterance | null>(null);

    useEffect(() => {
        // Cleanup speech on unmount
        return () => {
            window.speechSynthesis.cancel();
        };
    }, []);

    const speakText = (text: string) => {
        window.speechSynthesis.cancel(); // Stop any current speech

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = playbackSpeed;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        utterance.onstart = () => setIsPlaying(true);
        utterance.onend = () => setIsPlaying(false);
        utterance.onerror = () => setIsPlaying(false);

        speechRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    };

    const stopSpeaking = () => {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
    };

    const handleSpeedChange = () => {
        const newSpeed = playbackSpeed >= 1.5 ? 0.75 : playbackSpeed + 0.25;
        setPlaybackSpeed(newSpeed);
    };

    const replayLastQuestion = () => {
        const lastAiMsg = [...transcript].reverse().find(m => m.role === 'ai');
        if (lastAiMsg) {
            speakText(lastAiMsg.text);
        }
    };

    const startRecording = () => {
        setIsRecording(true);
        // Simulate recording duration
        setTimeout(() => {
            setIsRecording(false);
            analyzeResponse("I believe checking patient ID is crucial because it ensures the right patient gets the right medication, preventing critical errors."); // Simulating transcribed audio
        }, 3000);
    };

    const handleTextSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!textInput.trim()) return;

        analyzeResponse(textInput);
        setTextInput("");
        setIsTyping(false);
    };

    const analyzeResponse = (userResponse: string) => {
        setProcessing(true);

        // Add user message immediately
        setTranscript(prev => [...prev, { role: 'user', text: userResponse }]);

        // Simulate AI analysis and response
        setTimeout(() => {
            setProcessing(false);
            const nextQuestion = "That's a solid answer. Now, imagine the patient becomes unresponsive during the procedure. What is your immediate next step?";

            setTranscript(prev => [
                ...prev,
                { role: 'ai', text: nextQuestion }
            ]);

            setFeedback({
                score: 85,
                clarity: "High",
                clinical_accuracy: "Good",
                tips: "Good use of safety protocols. To improve, explicitly mention checking the wristband against the MAR."
            });

            // Auto-play the next question
            speakText(nextQuestion);
        }, 2000);
    };

    return (
        <div className="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden flex flex-col h-[700px]">
            {/* Header */}
            <div className="bg-gradient-to-r from-teal-600 to-emerald-600 px-8 py-6 text-white flex justify-between items-center shadow-lg z-10">
                <div className="flex items-center space-x-4">
                    <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                        <Mic className="h-8 w-8 text-white" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">AI Clinical Interview</h2>
                        <p className="text-teal-100 text-sm font-medium">Voice & Text Simulation with Feedback</p>
                    </div>
                </div>

                {/* Audio Controls */}
                <div className="flex items-center space-x-2 bg-black/20 rounded-lg p-1">
                    <button
                        onClick={replayLastQuestion}
                        className="p-2 hover:bg-white/20 rounded-lg transition text-white/90"
                        title="Replay Question"
                    >
                        <RotateCcw className="h-5 w-5" />
                    </button>
                    {(isPlaying) ? (
                        <button
                            onClick={stopSpeaking}
                            className="p-2 hover:bg-white/20 rounded-lg transition text-white/90"
                            title="Stop Audio"
                        >
                            <Pause className="h-5 w-5" />
                        </button>
                    ) : (
                        <button
                            onClick={() => {
                                const lastAiMsg = [...transcript].reverse().find(m => m.role === 'ai');
                                if (lastAiMsg) speakText(lastAiMsg.text);
                            }}
                            className="p-2 hover:bg-white/20 rounded-lg transition text-white/90"
                            title="Play Audio"
                        >
                            <Volume2 className="h-5 w-5" />
                        </button>
                    )}

                    <button
                        onClick={handleSpeedChange}
                        className="px-3 py-1.5 hover:bg-white/20 rounded-lg transition text-xs font-bold w-16 text-center"
                        title="Playback Speed"
                    >
                        {playbackSpeed}x
                    </button>
                </div>
            </div>

            {/* Transcript Area */}
            <div className="flex-1 bg-slate-50 p-6 overflow-y-auto space-y-6">
                {transcript.map((msg, idx) => (
                    <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm border-2 border-white ${msg.role === 'user' ? 'bg-indigo-100' : 'bg-teal-100'}`}>
                            {msg.role === 'user' ? <User className="text-indigo-600 h-5 w-5" /> : <Bot className="text-teal-600 h-5 w-5" />}
                        </div>
                        <div className={`p-4 rounded-2xl max-w-lg shadow-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-white border border-slate-200 text-slate-700 rounded-bl-none'}`}>
                            <p className="font-bold text-xs mb-1 opacity-75 uppercase tracking-wide">{msg.role === 'user' ? 'You' : 'AI Interviewer'}</p>
                            <p className="leading-relaxed text-sm md:text-base">{msg.text}</p>
                        </div>
                    </div>
                ))}

                {processing && (
                    <div className="flex gap-4">
                        <div className="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center animate-bounce">
                            <Bot className="text-teal-600" />
                        </div>
                        <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 flex items-center gap-3">
                            <Loader2 className="animate-spin text-teal-600" />
                            <span className="text-slate-500 italic text-sm">Analyzing your response...</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Feedback Area */}
            {feedback && (
                <div className="bg-white border-b border-t border-slate-100 px-6 py-4 bg-slate-50/50">
                    <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-500">Confidence:</span>
                            <span className="font-black text-teal-600">{feedback.score}/100</span>
                        </div>
                        <div className="h-4 w-px bg-slate-300"></div>
                        <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-500">Tips:</span>
                            <span className="text-slate-600 italic truncate max-w-md">{feedback.tips}</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Input Area */}
            <div className="bg-white p-6 border-t border-slate-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-20">
                {!isRecording && !processing ? (
                    isTyping ? (
                        <form onSubmit={handleTextSubmit} className="flex gap-3 animate-in slide-in-from-bottom-2">
                            <input
                                type="text"
                                autoFocus
                                value={textInput}
                                onChange={(e) => setTextInput(e.target.value)}
                                placeholder="Type your response here..."
                                className="flex-1 border border-slate-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition shadow-inner"
                            />
                            <button
                                type="submit"
                                disabled={!textInput.trim()}
                                className="bg-indigo-600 text-white px-6 rounded-xl font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                            >
                                <Send className="h-5 w-5" />
                            </button>
                            <button
                                type="button"
                                onClick={() => setIsTyping(false)}
                                className="p-3 text-slate-400 hover:text-slate-600 transition"
                            >
                                <RotateCcw className="h-5 w-5" />
                            </button>
                        </form>
                    ) : (
                        <div className="flex justify-center gap-4">
                            <button
                                onClick={startRecording}
                                className="group relative bg-teal-600 text-white pl-6 pr-8 py-4 rounded-full font-bold text-lg shadow-lg shadow-teal-200 hover:shadow-xl hover:scale-105 transition-all flex items-center gap-3 active:scale-95"
                            >
                                <span className="absolute inset-0 rounded-full border-2 border-white/20 group-hover:border-white/40 transition-colors"></span>
                                <Mic className="h-6 w-6" />
                                <span>Record Answer</span>
                            </button>

                            <div className="flex items-center justify-center p-2">
                                <span className="text-slate-300 font-medium text-sm">OR</span>
                            </div>

                            <button
                                onClick={() => setIsTyping(true)}
                                className="bg-white border-2 border-slate-200 text-slate-600 px-6 py-4 rounded-full font-bold text-lg hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all flex items-center gap-3"
                            >
                                <Keyboard className="h-6 w-6" />
                                <span>Type Answer</span>
                            </button>
                        </div>
                    )
                ) : (
                    <div className="flex justify-center py-2">
                        {isRecording ? (
                            <div className="flex items-center gap-3 text-teal-600 font-bold animate-pulse">
                                <span className="w-3 h-3 bg-red-500 rounded-full animate-ping"></span>
                                Listening...
                            </div>
                        ) : (
                            <span className="text-slate-400 font-medium">Processing...</span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default InterviewMode;
