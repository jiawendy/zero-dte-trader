import { useState, useEffect, useRef } from 'react'

function App() {
    const [analysis, setAnalysis] = useState(null)
    const [voiceEnabled, setVoiceEnabled] = useState(false)
    const [autoSaveDocs, setAutoSaveDocs] = useState(false)
    const [autoSaveDisk, setAutoSaveDisk] = useState(false)
    const [isPaused, setIsPaused] = useState(false)
    const [lastReadTimestamp, setLastReadTimestamp] = useState(null)
    const [lastSavedTimestamp, setLastSavedTimestamp] = useState(null)
    const [loading, setLoading] = useState(false)

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

    const fetchStatus = async () => {
        try {
            const res = await fetch(`${API_URL}/api/status`)
            const data = await res.json()
            if (data.paused !== undefined) {
                setIsPaused(data.paused)
            }
        } catch (err) {
            console.error("Failed to fetch status", err)
        }
    }

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
        fetchStatus()
        fetchAnalysis()
        const interval = setInterval(() => {
            fetchAnalysis()
            fetchStatus()
        }, 60000) // Poll every minute
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        if (!analysis || !analysis.timestamp) return

        // Voice Logic
        if (voiceEnabled && analysis.text && analysis.timestamp !== lastReadTimestamp) {
            const utterance = new SpeechSynthesisUtterance(analysis.text)
            window.speechSynthesis.speak(utterance)
            setLastReadTimestamp(analysis.timestamp)
        }

        // Auto-Save Logic
        if (analysis.timestamp !== lastSavedTimestamp) {
            if (autoSaveDocs) {
                shareToDocs(true) // Pass true to suppress alerts
            }
            if (autoSaveDisk) {
                saveToDisk(true) // Pass true to suppress alerts
            }
            // Only update timestamp if we actually saved something or if we just want to mark this analysis as "seen" for saving purposes?
            // Actually, if we toggle ON later, we might want to save the current one? 
            // The user said "every 10 mins". 
            // Let's update lastSavedTimestamp only if we attempted a save OR if we just want to track "processed".
            // If I update it here unconditionally, then toggling ON later won't save the *current* stale one, which is probably good.
            // We only want to auto-save *fresh* incoming data.
            setLastSavedTimestamp(analysis.timestamp)
        }
    }, [analysis, voiceEnabled, autoSaveDocs, autoSaveDisk, lastReadTimestamp, lastSavedTimestamp])

    const shareToDocs = async (silent = false) => {
        try {
            const res = await fetch(`${API_URL}/api/share`, { method: 'POST' })
            const data = await res.json()
            if (data.url) {
                if (!silent) window.open(data.url, '_blank')
                console.log("Shared to docs:", data.url)
            } else if (data.error) {
                console.error("Error sharing:", data.error)
                if (!silent) alert(`Error sharing: ${data.error}`)
            }
        } catch (err) {
            console.error("Failed to share", err)
            if (!silent) alert("Failed to share to Google Docs")
        }
    }

    const saveToDisk = async (silent = false) => {
        try {
            const res = await fetch(`${API_URL}/api/save_local`, { method: 'POST' })
            const data = await res.json()
            if (data.path) {
                console.log("Saved to disk:", data.path)
                if (!silent) alert(`Saved to: ${data.path}`)
            } else if (data.error) {
                console.error("Error saving:", data.error)
                if (!silent) alert(`Error saving: ${data.error}`)
            }
        } catch (err) {
            console.error("Failed to save", err)
            if (!silent) alert("Failed to save to disk")
        }
    }

    const togglePause = async () => {
        const endpoint = isPaused ? 'resume' : 'pause'
        try {
            await fetch(`${API_URL}/api/${endpoint}`, { method: 'POST' })
            setIsPaused(!isPaused)
            alert(`Analysis ${isPaused ? 'Resumed' : 'Paused'}`)
        } catch (err) {
            console.error("Failed to toggle pause", err)
            alert("Failed to toggle pause state")
        }
    }

    return (
        <div className="min-h-screen p-8 bg-slate-900 text-slate-100 font-sans">
            <header className="mb-8 flex justify-between items-center">
                <h1 className="text-3xl font-bold text-blue-400">0DTE Trader Assistant</h1>
                <div className="flex items-center gap-4">
                    <button
                        onClick={togglePause}
                        className={`px-4 py-2 rounded-full font-semibold transition-colors ${isPaused ? 'bg-green-600 hover:bg-green-500' : 'bg-yellow-600 hover:bg-yellow-500'
                            }`}
                    >
                        {isPaused ? 'Resume Analysis ▶️' : 'Pause Analysis ⏸️'}
                    </button>
                    <button
                        onClick={() => setAutoSaveDisk(!autoSaveDisk)}
                        className={`px-4 py-2 rounded-full font-semibold transition-colors ${autoSaveDisk ? 'bg-purple-600 hover:bg-purple-500' : 'bg-slate-600 hover:bg-slate-500'
                            }`}
                    >
                        {autoSaveDisk ? 'Auto-Save Disk: ON' : 'Auto-Save Disk: OFF'}
                    </button>
                    <button
                        onClick={() => setAutoSaveDocs(!autoSaveDocs)}
                        className={`px-4 py-2 rounded-full font-semibold transition-colors ${autoSaveDocs ? 'bg-yellow-600 hover:bg-yellow-500' : 'bg-slate-600 hover:bg-slate-500'
                            }`}
                    >
                        {autoSaveDocs ? 'Auto-Save Docs: ON' : 'Auto-Save Docs: OFF'}
                    </button>
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
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-full font-semibold disabled:opacity-50 transition-colors"
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
                                    {analysis.timestamp ? new Date(analysis.timestamp).toLocaleString('en-US', { timeZone: 'America/New_York', timeZoneName: 'short' }) : 'Never'}
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
                                <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                                    <h3 className="text-sm font-medium text-slate-400 mb-1">VIX Index</h3>
                                    <div className="flex items-baseline gap-2">
                                        <p className="text-2xl font-bold text-purple-400">{analysis.data.vix_current || 'N/A'}</p>
                                        <span className="text-sm text-slate-500">{analysis.data.vix_trend}</span>
                                    </div>
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
