'use client'

import { useState, useRef, useEffect } from 'react'
import AnimatedBackground from './components/AnimatedBackground'

interface ResearchResults {
  question: string
  summary: string
  findings: string[]
  sources: string[]
  timestamp: string
}

export default function Home() {
  const [value, setValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ResearchResults | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
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

  return (
    <main className="min-h-screen flex flex-col items-center px-4 relative pt-60 pb-8">
      <AnimatedBackground />
      <h1 className="text-5xl md:text-6xl font-righteous text-white mb-6 relative z-10 text-center tracking-wide">Let&apos;s Research!</h1>
      <div className="w-full max-w-2xl relative z-10">
        <div className="flex gap-2 mb-6">
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your research question..."
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
              <p>Agent is researching your question...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/20 backdrop-blur-md border border-red-500/50 rounded-xl p-6 shadow-lg mb-6">
            <p className="text-red-200">Error: {error}</p>
          </div>
        )}

        {results && (
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 shadow-lg space-y-4">
            <h2 className="text-2xl font-bold text-white mb-2">Research Results</h2>
            <div className="text-white/90">
              <p className="text-lg mb-4">{results.summary}</p>
              
              <div className="mb-4">
                <h3 className="text-xl font-semibold mb-2 text-white">Key Findings:</h3>
                <ul className="list-disc list-inside space-y-2 ml-2">
                  {results.findings.map((finding, index) => (
                    <li key={index}>{finding}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-2 text-white">Sources:</h3>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  {results.sources.map((source, index) => (
                    <li key={index} className="text-white/70">{source}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

