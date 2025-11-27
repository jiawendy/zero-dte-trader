import { useState, useEffect, useRef } from 'react'

function App() {
    const [analysis, setAnalysis] = useState(null)
    const [voiceEnabled, setVoiceEnabled] = useState(false)
    const [lastReadTimestamp, setLastReadTimestamp] = useState(null)
    const [loading, setLoading] = useState(false)

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

    const fetchAnalysis = async () => {
        try {
            const res = await fetch(`${API_URL}/api/latest`)
            const data = await res.json()
            setAnalysis(data)
        } catch (err) {
            console.error("Failed to fetch analysis", err)
        }
    }

    const triggerAnalysis = async () => {
        setLoading(true)
        try {
            await fetch(`${API_URL}/api/analyze`, { method: 'POST' })
            await fetchAnalysis()
        } catch (err) {
            console.error("Failed to trigger analysis", err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchAnalysis()
        const interval = setInterval(fetchAnalysis, 60000) // Poll every minute
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        if (voiceEnabled && analysis && analysis.text && analysis.timestamp !== lastReadTimestamp) {
            const utterance = new SpeechSynthesisUtterance(analysis.text)
            window.speechSynthesis.speak(utterance)
            setLastReadTimestamp(analysis.timestamp)
        }
    }, [analysis, voiceEnabled, lastReadTimestamp])

    return (
        <div className="min-h-screen p-8 bg-slate-900 text-slate-100 font-sans">
            <header className="mb-8 flex justify-between items-center">
                <h1 className="text-3xl font-bold text-blue-400">0DTE Trader Assistant</h1>
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setVoiceEnabled(!voiceEnabled)}
                        className={`px-4 py-2 rounded-full font-semibold transition-colors ${voiceEnabled ? 'bg-green-600 hover:bg-green-500' : 'bg-slate-600 hover:bg-slate-500'
                            }`}
                    >
                        {voiceEnabled ? 'Voice ON' : 'Voice OFF'}
                    </button>
                    <button
                        onClick={triggerAnalysis}
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold disabled:opacity-50"
                    >
                        {loading ? 'Analyzing...' : 'Refresh Now'}
                    </button>
                </div>
            </header>

            <main className="max-w-4xl mx-auto">
                {analysis ? (
                    <div className="space-y-6">
                        <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-semibold text-slate-300">Latest Analysis</h2>
                                <span className="text-sm text-slate-500">
                                    {analysis.timestamp ? new Date(analysis.timestamp).toLocaleString() : 'Never'}
                                </span>
                            </div>
                            <div className="prose prose-invert max-w-none text-lg leading-relaxed whitespace-pre-line">
                                {analysis.text}
                            </div>
                        </div>

                        {analysis.data && (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                                    <h3 className="text-sm font-medium text-slate-400 mb-1">Spot Price</h3>
                                    <p className="text-2xl font-bold">{analysis.data.spot_price || 'N/A'}</p>
                                </div>
                                <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                                    <h3 className="text-sm font-medium text-slate-400 mb-1">Call Volume</h3>
                                    <p className="text-2xl font-bold text-green-400">{analysis.data.call_volume?.toLocaleString() || '0'}</p>
                                </div>
                                <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                                    <h3 className="text-sm font-medium text-slate-400 mb-1">Put Volume</h3>
                                    <p className="text-2xl font-bold text-red-400">{analysis.data.put_volume?.toLocaleString() || '0'}</p>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="text-center text-slate-500 mt-20">
                        Loading analysis data...
                    </div>
                )}
            </main>
        </div>
    )
}

export default App
