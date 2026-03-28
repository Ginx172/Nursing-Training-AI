import React, { useState } from 'react';
import api from '../../lib/api';
import { Video, Play, Loader2, AlertTriangle, CheckCircle, Smartphone } from 'lucide-react';

const VideoAnalysis = () => {
    const [videoUrl, setVideoUrl] = useState('');
    const [context, setContext] = useState('Cannulation procedure');
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState('');

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!videoUrl) return;

        setAnalyzing(true);
        setError('');
        setResult(null);

        try {
            const response = await api.post('/api/ai/video/analyze', {
                video_url: videoUrl,
                context: context
            });
            setResult(response.data);
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || 'Failed to analyze video. Ensure Backend is running and API Key is set.');
        } finally {
            setAnalyzing(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 mb-6 border-b border-slate-100 pb-4">
                <div className="p-2 bg-indigo-100 rounded-lg">
                    <Video className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                    <h2 className="text-lg font-semibold text-slate-800">AI Video Analysis</h2>
                    <p className="text-sm text-slate-500">Multimodal Clinical Procedure Assessment (Gemini 1.5/GPT-4o)</p>
                </div>
            </div>

            <form onSubmit={handleAnalyze} className="space-y-4 mb-8">
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Video URL / Path</label>
                    <input
                        type="text"
                        value={videoUrl}
                        onChange={(e) => setVideoUrl(e.target.value)}
                        placeholder="https://example.com/procedure.mp4"
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all text-sm"
                    />
                    <p className="text-xs text-slate-400 mt-1">Accepts MP4, MOV, or YouTube links (simulation)</p>
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Clinical Context</label>
                    <select
                        value={context}
                        onChange={(e) => setContext(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                    >
                        <option value="Cannulation procedure">Cannulation</option>
                        <option value="Hand hygiene">Hand Hygiene</option>
                        <option value="Catheter insertion">Catheter Insertion</option>
                        <option value="NG Tube insertion">NG Tube Insertion</option>
                        <option value="Wound dressing">Wound Dressing</option>
                    </select>
                </div>

                <button
                    type="submit"
                    disabled={analyzing || !videoUrl}
                    className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {analyzing ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Analyzing Procedure...
                        </>
                    ) : (
                        <>
                            <Play className="w-4 h-4" />
                            Start Analysis
                        </>
                    )}
                </button>
            </form>

            {error && (
                <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-100 flex items-start gap-3 mt-4">
                    <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div className="text-sm">{error}</div>
                </div>
            )}

            {result && result.analysis && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="bg-slate-50 border border-slate-200 rounded-xl overflow-hidden">
                        <div className="p-4 bg-white border-b border-slate-200 flex justify-between items-center">
                            <h3 className="font-semibold text-slate-800">Analysis Results</h3>
                            <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${result.analysis.overall_rating === 'Pass'
                                    ? 'bg-green-100 text-green-700'
                                    : 'bg-amber-100 text-amber-700'
                                }`}>
                                {result.analysis.overall_rating.toUpperCase()}
                            </span>
                        </div>

                        <div className="p-4 space-y-4">
                            <div className="bg-white p-3 rounded-lg border border-slate-100 shadow-sm">
                                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">AI Feedback</p>
                                <p className="text-slate-700 text-sm leading-relaxed">
                                    {result.analysis.feedback}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Procedure Steps</p>
                                <div className="space-y-2">
                                    {result.analysis.steps_identified.map((step: any, idx: number) => (
                                        <div key={idx} className="flex items-center justify-between text-sm p-2 bg-white rounded border border-slate-100">
                                            <div className="flex items-center gap-3">
                                                <span className="w-6 h-6 flex items-center justify-center bg-slate-100 text-slate-500 rounded-full text-xs font-mono">
                                                    {idx + 1}
                                                </span>
                                                <span className="text-slate-700">{step.description}</span>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <span className="text-xs font-mono text-slate-400">{step.timestamp}</span>
                                                {step.correct ? (
                                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                                ) : (
                                                    <AlertTriangle className="w-4 h-4 text-amber-500" />
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-100">
                                <span>Model: {result.model_used}</span>
                                <span>Conf: {(result.analysis.confidence_score * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VideoAnalysis;
