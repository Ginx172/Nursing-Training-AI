import { useEffect, useMemo, useRef, useState } from 'react'

interface DemoQuestion {
  id: number
  title: string
  question_text: string
  question_type: string
  options?: string[] | null
  correct_answer: string
  explanation?: string | null
}

interface Recommendation {
  title: string
  summary: string
  url?: string | null
}

interface SubmitResult {
  question_id: number
  is_correct: boolean
  feedback: string
  recommendations: Recommendation[]
}

interface PerQuestionBatchResult {
  question_id: number
  is_correct: boolean
  feedback: string
  recommendations: Recommendation[]
}

interface BatchSummary {
  total_questions: number
  correct: number
  score_percentage: number
  per_question: PerQuestionBatchResult[]
  study_plan: { title: string; items: string[] }[]
  next_steps: string
}

const API_URL = (typeof window !== 'undefined' ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') : 'http://localhost:8000')

export default function DemoPage() {
  const [loading, setLoading] = useState(false)
  const [questions, setQuestions] = useState<DemoQuestion[]>([])
  const [error, setError] = useState<string>('')
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [results, setResults] = useState<Record<number, SubmitResult>>({})
  const [audioEnabled, setAudioEnabled] = useState<boolean>(false)
  const [speakingId, setSpeakingId] = useState<number | null>(null)
  const [interviewMode, setInterviewMode] = useState<boolean>(false)
  const [batchSummary, setBatchSummary] = useState<BatchSummary | null>(null)

  // Speech Recognition (Web Speech API)
  const SpeechRecognitionImpl = useMemo(() => {
    if (typeof window === 'undefined') return null
    const w = window as any
    return w.SpeechRecognition || w.webkitSpeechRecognition || null
  }, [])
  const recognitionRef = useRef<any>(null)
  const [listeningForId, setListeningForId] = useState<number | null>(null)

  useEffect(() => {
    const fetchQuestions = async () => {
      setLoading(true)
      setError('')
      try {
        const res = await fetch(`${API_URL}/api/demo/questions`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data: DemoQuestion[] = await res.json()
        setQuestions(data)
      } catch (e: any) {
        setError(`Eroare la încărcarea întrebărilor: ${e?.message || e}`)
      } finally {
        setLoading(false)
      }
    }
    fetchQuestions()
  }, [])

  const canSpeak = useMemo(() => typeof window !== 'undefined' && 'speechSynthesis' in window, [])
  const canListen = useMemo(() => !!SpeechRecognitionImpl, [SpeechRecognitionImpl])

  const speak = (text: string, id: number) => {
    if (!canSpeak) return
    try {
      window.speechSynthesis.cancel()
      const utter = new SpeechSynthesisUtterance(text)
      utter.lang = 'en-GB'
      setSpeakingId(id)
      utter.onend = () => setSpeakingId(null)
      window.speechSynthesis.speak(utter)
    } catch (_) {}
  }

  const stopSpeak = () => {
    if (!canSpeak) return
    window.speechSynthesis.cancel()
    setSpeakingId(null)
  }

  const handleAnswerChange = (qid: number, value: string) => {
    setAnswers(prev => ({ ...prev, [qid]: value }))
  }

  // Submit single answer (kept for Text Mode quick test); hidden in Interview Mode
  const submitAnswer = async (qid: number) => {
    const user_answer = (answers[qid] ?? '').trim()
    if (!user_answer) {
      alert('Introdu un răspuns înainte de a trimite.')
      return
    }
    try {
      const res = await fetch(`${API_URL}/api/demo/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: qid, user_answer })
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: SubmitResult = await res.json()
      setResults(prev => ({ ...prev, [qid]: data }))
    } catch (e: any) {
      alert(`Eroare la trimiterea răspunsului: ${e?.message || e}`)
    }
  }

  // Batch submit (Interview Mode): send all answers at once
  const submitBatch = async () => {
    const payload = {
      answers: questions.map(q => ({ question_id: q.id, user_answer: (answers[q.id] ?? '').trim() }))
    }
    // Validate that every answer exists
    const missing = payload.answers.filter(a => !a.user_answer)
    if (missing.length > 0) {
      alert('Completează toate răspunsurile înainte de finalizare.')
      return
    }
    try {
      const res = await fetch(`${API_URL}/api/demo/submit-batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: BatchSummary = await res.json()
      setBatchSummary(data)
      // stop any speaking
      stopSpeak()
      // stop recognition if running
      stopListening()
    } catch (e: any) {
      alert(`Eroare la finalizare: ${e?.message || e}`)
    }
  }

  // Speech recognition helpers
  const startListening = (qid: number) => {
    if (!canListen || !SpeechRecognitionImpl) return
    try {
      // Cancel TTS if talking
      stopSpeak()
      // Stop previous recognition
      stopListening()
      const rec: any = new SpeechRecognitionImpl()
      recognitionRef.current = rec
      setListeningForId(qid)
      rec.lang = 'en-GB'
      rec.interimResults = false
      rec.maxAlternatives = 1
      rec.onresult = (event: any) => {
        const transcript = event.results?.[0]?.[0]?.transcript || ''
        if (transcript) {
          handleAnswerChange(qid, transcript)
        }
      }
      rec.onerror = () => {
        setListeningForId(null)
      }
      rec.onend = () => {
        setListeningForId(null)
      }
      rec.start()
    } catch (_) {
      setListeningForId(null)
    }
  }

  const stopListening = () => {
    const rec = recognitionRef.current
    if (rec && typeof rec.stop === 'function') {
      try { rec.stop() } catch {}
    }
    recognitionRef.current = null
    setListeningForId(null)
  }

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', padding: '0 16px', fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      <h1 style={{ fontSize: 28, marginBottom: 8 }}>Nursing Training AI — Demo</h1>
      <p style={{ color: '#555', marginBottom: 24 }}>Întrebări text + opțional Audio (TTS) și răspuns oral (Speech Recognition). Feedback-ul în modul Interviu apare doar la final.</p>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            checked={audioEnabled}
            onChange={(e) => setAudioEnabled(e.target.checked)}
            disabled={!canSpeak}
          />
          <span>Activează Audio (TTS local)</span>
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            checked={interviewMode}
            onChange={(e) => {
              setInterviewMode(e.target.checked)
              setBatchSummary(null)
              setResults({})
            }}
          />
          <span>Mod Interviu (feedback doar la final)</span>
        </label>
        {!canSpeak && (
          <span style={{ color: '#a00' }}>Browserul nu suportă Web Speech Synthesis</span>
        )}
        {interviewMode && !canListen && (
          <span style={{ color: '#a00' }}>Browserul nu suportă Speech Recognition</span>
        )}
      </div>

      {loading && <div>Se încarcă întrebările...</div>}
      {error && (
        <div style={{ background: '#fee', border: '1px solid #f99', padding: 12, borderRadius: 8, marginBottom: 16 }}>
          {error}
        </div>
      )}

      {questions.map((q) => {
        const isSpeaking = speakingId === q.id
        const isListening = listeningForId === q.id
        return (
          <div key={q.id} style={{ border: '1px solid #ddd', borderRadius: 10, padding: 16, marginBottom: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{q.title}</div>
                <div style={{ color: '#333', marginTop: 6 }}>{q.question_text}</div>
              </div>
              {audioEnabled && canSpeak && (
                <div>
                  {!isSpeaking ? (
                    <button onClick={() => speak(`${q.title}. ${q.question_text}`, q.id)} style={{ padding: '8px 12px' }}>
                      🔊 Redă întrebarea
                    </button>
                  ) : (
                    <button onClick={stopSpeak} style={{ padding: '8px 12px' }}>
                      ⏹ Oprește
                    </button>
                  )}
                </div>
              )}
            </div>

            <div style={{ marginTop: 12, display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
              {q.options && q.options.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: '1 1 300px' }}>
                  {q.options.map((opt, idx) => (
                    <label key={idx} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <input
                        type="radio"
                        name={`q-${q.id}`}
                        value={opt}
                        checked={(answers[q.id] || '') === opt}
                        onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <input
                  type="text"
                  placeholder={interviewMode ? 'Răspuns (poți dicta)...' : 'Răspunsul tău...'}
                  value={answers[q.id] || ''}
                  onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                  style={{ flex: '1 1 300px', padding: 10, border: '1px solid #ccc', borderRadius: 8 }}
                />
              )}

              {interviewMode && canListen && (
                !isListening ? (
                  <button onClick={() => startListening(q.id)} style={{ padding: '8px 12px' }}>
                    🎙️ Răspunde vocal
                  </button>
                ) : (
                  <button onClick={stopListening} style={{ padding: '8px 12px' }}>
                    ⏹ Oprește dictarea
                  </button>
                )
              )}
            </div>

            {!interviewMode && (
              <div style={{ marginTop: 12, display: 'flex', gap: 10 }}>
                <button onClick={() => submitAnswer(q.id)} style={{ padding: '8px 12px' }}>Trimite răspuns</button>
                {/* Feedback per întrebare rămâne disponibil doar în Text Mode */}
              </div>
            )}

            {!interviewMode && results[q.id] && (
              <div style={{ marginTop: 14, padding: 12, borderRadius: 8, background: results[q.id].is_correct ? '#ecfdf5' : '#fef2f2', border: `1px solid ${results[q.id].is_correct ? '#10b981' : '#ef4444'}` }}>
                <div style={{ fontWeight: 700, marginBottom: 6 }}>{results[q.id].is_correct ? 'Corect ✅' : 'Incorect ❌'}</div>
                <div style={{ whiteSpace: 'pre-wrap' }}>{results[q.id].feedback}</div>
                {results[q.id].recommendations?.length > 0 && (
                  <div style={{ marginTop: 10 }}>
                    <div style={{ fontWeight: 700, marginBottom: 6 }}>Recomandări de studiu:</div>
                    <ul style={{ paddingLeft: 18 }}>
                      {results[q.id].recommendations.map((r, i) => (
                        <li key={i} style={{ marginBottom: 6 }}>
                          <div style={{ fontWeight: 600 }}>{r.title}</div>
                          <div style={{ color: '#333' }}>{r.summary}</div>
                          {r.url && (
                            <div>
                              <a href={r.url} target="_blank" rel="noreferrer">Deschide resursă</a>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}

      {interviewMode && questions.length > 0 && (
        <div style={{ position: 'sticky', bottom: 0, background: '#fff', padding: 12, borderTop: '1px solid #eee', display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <button onClick={submitBatch} style={{ padding: '10px 14px', fontWeight: 600 }}>
            ✅ Finalizare și feedback
          </button>
        </div>
      )}

      {batchSummary && (
        <div style={{ marginTop: 20, padding: 16, borderRadius: 10, border: '1px solid #ddd', background: '#fafafa' }}>
          <div style={{ fontSize: 18, fontWeight: 800, marginBottom: 8 }}>Rezultate finale</div>
          <div style={{ marginBottom: 6 }}>Întrebări: {batchSummary.total_questions}</div>
          <div style={{ marginBottom: 6 }}>Corecte: {batchSummary.correct}</div>
          <div style={{ marginBottom: 12 }}>Scor: {batchSummary.score_percentage}%</div>

          <div style={{ fontWeight: 700, marginBottom: 6 }}>Detalii pe întrebare</div>
          <ul style={{ paddingLeft: 18, marginBottom: 12 }}>
            {batchSummary.per_question.map((r) => (
              <li key={r.question_id} style={{ marginBottom: 8 }}>
                <div><strong>Q{r.question_id}:</strong> {r.is_correct ? 'Corect ✅' : 'Incorect ❌'}</div>
                <div>{r.feedback}</div>
                {r.recommendations?.length > 0 && (
                  <ul style={{ paddingLeft: 18, marginTop: 4 }}>
                    {r.recommendations.map((rec, i) => (
                      <li key={i}>
                        <strong>{rec.title}:</strong> {rec.summary}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>

          <div style={{ fontWeight: 700, marginBottom: 6 }}>Plan de studiu</div>
          <ul style={{ paddingLeft: 18, marginBottom: 12 }}>
            {batchSummary.study_plan.map((s, i) => (
              <li key={i} style={{ marginBottom: 6 }}>
                <div style={{ fontWeight: 600 }}>{s.title}</div>
                <ul style={{ paddingLeft: 18 }}>
                  {s.items.map((it, j) => (<li key={j}>{it}</li>))}
                </ul>
              </li>
            ))}
          </ul>

          <div><strong>Pași următori:</strong> {batchSummary.next_steps}</div>
        </div>
      )}
    </div>
  )
}
