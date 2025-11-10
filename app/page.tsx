'use client'

import { useState, useRef, useEffect } from 'react'
import AnimatedBackground from './components/AnimatedBackground'

export default function Home() {
  const [value, setValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  return (
    <main className="min-h-screen flex flex-col items-center px-4 relative pt-60">
      <AnimatedBackground />
      <h1 className="text-5xl md:text-6xl font-righteous text-white mb-6 relative z-10 text-center tracking-wide">Let&apos;s Research!</h1>
      <div className="w-full max-w-2xl relative z-10">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Type something..."
          className="w-full px-6 py-4 text-lg bg-white/10 backdrop-blur-md border border-white/20 rounded-xl shadow-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all placeholder:text-gray-500 text-white"
        />
      </div>
    </main>
  )
}

