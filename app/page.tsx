'use client'

import { useState, useRef, useEffect } from 'react'
import AnimatedBackground from './components/AnimatedBackground'

interface ResearchResults {
  question: string
  summary: string
  findings: string[]
  sources: string[]
  timestamp: string
  category?: string
}

interface HistoryItem {
  question: string
  summary: string
  timestamp: string
  category: string
  findings: string[]
  sources: string[]
}

type History = Record<string, HistoryItem[]>

export default function Home() {
  const [value, setValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ResearchResults | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<History>({})
  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const fetchHistory = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${apiUrl}/api/history`)
      if (res.ok) {
        const data = await res.json()
        setHistory(data)
      }
    } catch (e) {
      console.error("Failed to fetch history", e)
    }
  }

  useEffect(() => {
    inputRef.current?.focus()
    fetchHistory()
  }, [])

  const handleResearch = async () => {
    if (!value.trim()) return

    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      console.log(`Making request to: ${apiUrl}/api/research`)
      
      const response = await fetch(`${apiUrl}/api/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: value }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Response error:', response.status, errorText)
        throw new Error(`Server error: ${response.status} - ${errorText || 'Unknown error'}`)
      }

      const data = await response.json()
      setResults(data)
      fetchHistory() // Refresh history after successful research
    } catch (err) {
      console.error('Fetch error:', err)
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Failed to connect to API server. Make sure FastAPI is running on http://localhost:8000')
      } else {
        setError(err instanceof Error ? err.message : 'An error occurred')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading) {
      handleResearch()
    }
  }

  const loadHistoryItem = (item: HistoryItem) => {
      setValue(item.question)
      setResults({
        question: item.question,
        summary: item.summary,
        findings: item.findings,
        sources: item.sources,
        timestamp: item.timestamp,
        category: item.category
      })
      // Close the category view (optional, or keep it open)
      // setActiveCategory(null) 
      inputRef.current?.focus()
  }

  const toggleCategory = (category: string) => {
      setActiveCategory(activeCategory === category ? null : category)
  }

  return (
    <div className="min-h-screen text-white relative flex">
      <AnimatedBackground />
      
      {/* Sidebar for Notebooks */}
      <aside className="w-80 bg-black/40 backdrop-blur-xl border-r border-white/10 p-6 fixed h-full overflow-y-auto hidden md:block z-20 transition-all duration-300">
        <h2 className="text-2xl font-bold mb-8 text-purple-300 font-righteous tracking-wide">Research Notebooks</h2>
        
        <div className="space-y-4">
            {Object.entries(history).map(([category, items]) => (
                <div key={category} className="rounded-xl overflow-hidden border border-white/5 bg-white/5 hover:bg-white/10 transition-all duration-300 shadow-lg">
                    <button 
                        onClick={() => toggleCategory(category)}
                        className={`w-full p-4 flex items-center justify-between text-left transition-colors ${activeCategory === category ? 'bg-purple-600/20 text-purple-200' : ''}`}
                    >
                        <span className="font-semibold text-lg tracking-wide">{category}</span>
                        <div className="flex items-center gap-3">
                            <span className="bg-black/30 px-2 py-1 rounded text-xs font-mono text-gray-400">
                                {items.length}
                            </span>
                            <svg 
                                className={`w-4 h-4 transition-transform duration-300 ${activeCategory === category ? 'rotate-180' : ''}`} 
                                fill="none" viewBox="0 0 24 24" stroke="currentColor"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </div>
                    </button>
                    
                    {/* Expanded Notebook Content */}
                    <div className={`
                        transition-all duration-300 ease-in-out overflow-hidden
                        ${activeCategory === category ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'}
                    `}>
                        <div className="p-2 space-y-1 bg-black/20">
                            {items && items.length > 0 ? (
                                items.map((item, idx) => (
                                    <button 
                                        key={idx}
                                        onClick={() => loadHistoryItem(item)}
                                        className="w-full text-left p-3 rounded-lg hover:bg-white/10 transition-all group border-l-2 border-transparent hover:border-purple-400"
                                    >
                                        <p className="font-medium text-sm truncate text-gray-300 group-hover:text-white transition-colors">
                                            {item.question}
                                        </p>
                                        <p className="text-[10px] text-gray-500 mt-1 truncate font-mono opacity-60">
                                            {new Date(item.timestamp).toLocaleDateString()}
                                        </p>
                                    </button>
                                ))
                            ) : (
                                <p className="text-center text-gray-500 text-xs py-4 italic">Empty notebook</p>
                            )}
                        </div>
                    </div>
                </div>
            ))}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center px-4 pt-40 pb-8 md:ml-80 relative z-10 w-full transition-all duration-300">
        <h1 className="text-5xl md:text-6xl font-righteous text-white mb-6 text-center tracking-wide">Let&apos;s Research!</h1>
        <div className="w-full max-w-2xl">
          <div className="flex gap-2 mb-6">
            <input
              ref={inputRef}
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything..."
              disabled={isLoading}
              className="flex-1 px-6 py-4 text-lg bg-white/10 backdrop-blur-md border border-white/20 rounded-xl shadow-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all placeholder:text-gray-500 text-white disabled:opacity-50"
            />
            <button
              onClick={handleResearch}
              disabled={isLoading || !value.trim()}
              className="px-6 py-4 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-xl font-semibold transition-all shadow-lg"
            >
              {isLoading ? 'Researching...' : 'Research'}
            </button>
          </div>

          {isLoading && (
            <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-3 text-white">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                <p>AI is thinking...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-500/20 backdrop-blur-md border border-red-500/50 rounded-xl p-6 shadow-lg mb-6">
              <p className="text-red-200">Error: {error}</p>
            </div>
          )}

          {results && (
            <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 shadow-lg space-y-4 animate-fade-in">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-2xl font-bold text-white">Research Results</h2>
                {results.category && (
                    <span className="px-3 py-1 rounded-full bg-purple-500/30 border border-purple-500/50 text-xs font-medium text-purple-200 uppercase tracking-widest">
                        {results.category}
                    </span>
                )}
              </div>
              <div className="text-white/90">
                <p className="text-lg mb-4 leading-relaxed font-light">{results.summary}</p>
                
                <div className="mb-6">
                  <h3 className="text-xl font-semibold mb-3 text-white border-b border-white/10 pb-2">Key Findings</h3>
                  <ul className="space-y-3">
                    {results.findings.map((finding, index) => (
                      <li key={index} className="flex gap-3 items-start bg-white/5 p-3 rounded-lg hover:bg-white/10 transition-colors">
                         <span className="text-purple-400 mt-1">•</span>
                         <span>{finding}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3 text-white border-b border-white/10 pb-2">Sources</h3>
                  <ul className="space-y-2">
                    {results.sources.map((source, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm text-white/70 hover:text-white transition-colors truncate">
                        <span className="text-purple-400 text-xs">LINK</span>
                        <a href={source.startsWith('http') ? source : '#'} target="_blank" rel="noopener noreferrer" className="hover:underline truncate w-full">
                            {source}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
