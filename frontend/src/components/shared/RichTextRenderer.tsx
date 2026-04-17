import ReactMarkdown from 'react-markdown'
import CodeBlock from '@/components/shared/CodeBlock' // Assuming this is highlight.js wrapping component

interface RichTextRendererProps {
  source: string
  className?: string
}

export default function RichTextRenderer({ source, className = '' }: RichTextRendererProps) {
  return (
    <div className={`prose prose-slate prose-indigo max-w-none prose-p:leading-relaxed prose-li:my-1 ${className}`}>
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '')
            const language = match ? match[1] : 'javascript'
            
            if (!inline) {
              return (
                <div className="not-prose my-6">
                  <CodeBlock 
                    code={String(children).replace(/\n$/, '')} 
                    language={language}
                  />
                </div>
              )
            }
            return (
              <code className="px-1.5 py-0.5 bg-slate-100 text-indigo-600 rounded-md font-mono text-sm before:content-none after:content-none" {...props}>
                {children}
              </code>
            )
          }
        }}
      >
        {source}
      </ReactMarkdown>
    </div>
  )
}
