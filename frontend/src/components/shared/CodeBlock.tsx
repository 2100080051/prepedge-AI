import { useEffect, useRef, useState } from 'react'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

interface CodeBlockProps {
  code: string
  language?: string
}

export default function CodeBlock({ code, language = 'javascript' }: CodeBlockProps) {
  const codeRef = useRef<HTMLElement>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (codeRef.current) {
      // Need to wipe out previous highlighting if code changes
      delete codeRef.current.dataset.highlighted
      hljs.highlightElement(codeRef.current)
    }
  }, [code, language])

  function copyToClipboard() {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative bg-slate-900 rounded-xl overflow-hidden shadow-sm">
      <div className="absolute top-3 right-3 z-10">
        <button
          onClick={copyToClipboard}
          className="px-3 py-1.5 text-xs font-medium bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors border border-slate-600/50"
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>
      <pre className="p-4 pt-10 overflow-x-auto select-text font-mono text-sm leading-relaxed text-slate-300">
        <code
          ref={codeRef}
          className={`language-${language} outline-none`}
        >
          {code}
        </code>
      </pre>
    </div>
  )
}
