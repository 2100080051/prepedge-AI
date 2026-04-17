/**
 * Code Editor Component
 * Supports multiple programming languages with syntax highlighting
 */

import React, { useState, useRef, useEffect } from 'react';
import { Play, Copy, Check, AlertCircle, Loader2, RotateCcw } from 'lucide-react';
import { codeExecutor, SUPPORTED_LANGUAGES, LANGUAGE_TEMPLATES } from '@/lib/codeExecutor';

interface CodeEditorProps {
  initialCode?: string;
  language?: string;
  onTest?: (code: string, output: string) => void;
  showPlayground?: boolean;
  isForProgrammingQuestion?: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  initialCode = '',
  language = 'python3',
  onTest,
  showPlayground = true,
  isForProgrammingQuestion = false,
}) => {
  const [code, setCode] = useState(initialCode || LANGUAGE_TEMPLATES[language] || '');
  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [executing, setExecuting] = useState(false);
  const [stdin, setStdin] = useState('');
  const [copied, setCopied] = useState(false);
  const [executionStats, setExecutionStats] = useState<{
    time: number;
    memory: string;
  } | null>(null);
  const editorRef = useRef<HTMLTextAreaElement>(null);

  // Handle language change
  const handleLanguageChange = (newLang: string) => {
    setSelectedLanguage(newLang);
    if (!code || code === LANGUAGE_TEMPLATES[language]) {
      setCode(LANGUAGE_TEMPLATES[newLang] || '');
    }
    setOutput('');
    setError('');
  };

  // Execute code
  const handleExecute = async () => {
    if (!code.trim()) {
      setError('Please write some code first');
      return;
    }

    setExecuting(true);
    setError('');
    setOutput('');

    try {
      const result = await codeExecutor.execute({
        language: selectedLanguage,
        code,
        stdin,
      });

      if (result.success) {
        setOutput(result.output || '(No output)');
        setExecutionStats({
          time: result.executionTime,
          memory: result.memory,
        });
        onTest?.(code, result.output);
      } else {
        setError(result.error || 'Execution failed');
      }
    } catch (err: any) {
      setError(err.message || 'Unknown error occurred');
    } finally {
      setExecuting(false);
    }
  };

  // Copy code to clipboard
  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Reset code
  const handleReset = () => {
    setCode(LANGUAGE_TEMPLATES[selectedLanguage] || '');
    setOutput('');
    setError('');
    setStdin('');
  };

  // Handle tab key in textarea
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.target as HTMLTextAreaElement;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      setCode(code.substring(0, start) + '  ' + code.substring(end));
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 2;
      }, 0);
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200">
        <div className="flex flex-wrap items-center gap-2">
          <label className="text-sm font-semibold text-slate-700">Language:</label>
          <select
            value={selectedLanguage}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleReset}
            disabled={executing}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 rounded-lg transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-emerald-500" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy
              </>
            )}
          </button>
          <button
            onClick={handleExecute}
            disabled={executing}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-all"
          >
            {executing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Code
              </>
            )}
          </button>
        </div>
      </div>

      {/* Code Editor */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <textarea
          ref={editorRef}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          onKeyDown={handleKeyDown}
          spellCheck={false}
          className="w-full p-4 bg-slate-900 text-slate-50 font-mono text-sm focus:ring-2 focus:ring-indigo-500 outline-none resize-y min-h-80 leading-relaxed"
          placeholder="Write your code here..."
        />
      </div>

      {/* Input Section (for stdin) */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
          <label className="text-sm font-semibold text-slate-700">Standard Input (Optional)</label>
        </div>
        <textarea
          value={stdin}
          onChange={(e) => setStdin(e.target.value)}
          spellCheck={false}
          className="w-full p-4 bg-slate-50 text-slate-700 font-mono text-sm focus:ring-2 focus:ring-indigo-500 outline-none resize-y min-h-20 leading-relaxed"
          placeholder="Enter input data here (one line per input)..."
        />
      </div>

      {/* Output Section */}
      {(output || error) && (
        <div className={`rounded-xl border overflow-hidden ${
          error
            ? 'bg-red-50 border-red-200'
            : 'bg-emerald-50 border-emerald-200'
        }`}>
          <div className={`px-4 py-3 border-b flex items-center gap-2 ${
            error
              ? 'bg-red-100 border-red-200'
              : 'bg-emerald-100 border-emerald-200'
          }`}>
            {error ? (
              <>
                <AlertCircle className={`w-5 h-5 ${error ? 'text-red-600' : 'text-emerald-600'}`} />
                <span className={`font-semibold ${error ? 'text-red-900' : 'text-emerald-900'}`}>
                  {error ? 'Error' : 'Output'}
                </span>
              </>
            ) : (
              <>
                <Check className="w-5 h-5 text-emerald-600" />
                <span className="font-semibold text-emerald-900">Output</span>
                {executionStats && (
                  <span className="ml-auto text-xs text-emerald-700">
                    Time: {executionStats.time}ms | Memory: {executionStats.memory}
                  </span>
                )}
              </>
            )}
          </div>
          <pre className={`p-4 font-mono text-sm whitespace-pre-wrap break-words ${
            error
              ? 'text-red-700 bg-red-50'
              : 'text-emerald-900 bg-emerald-50'
          }`}>
            {error || output}
          </pre>
        </div>
      )}

      {/* Execution Stats */}
      {executionStats && !error && (
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
            <div className="text-indigo-600 font-semibold">⏱️ Execution Time</div>
            <div className="text-indigo-900 text-lg font-bold">{executionStats.time}ms</div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <div className="text-purple-600 font-semibold">💾 Memory Used</div>
            <div className="text-purple-900 text-lg font-bold">{executionStats.memory}</div>
          </div>
        </div>
      )}

      {/* Help Text */}
      {showPlayground && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
          <div className="font-semibold text-blue-900 mb-2">💡 Playground Tips</div>
          <ul className="text-blue-800 space-y-1 ml-4 list-disc">
            <li>Press Tab to indent code</li>
            <li>Click "Run Code" to execute and see output</li>
            <li>Use Standard Input to provide test data</li>
            <li>All output is printed to the Output section</li>
          </ul>
        </div>
      )}

      {isForProgrammingQuestion && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm">
          <div className="font-semibold text-amber-900 mb-2">✓ For Programming Submissions</div>
          <ul className="text-amber-800 space-y-1 ml-4 list-disc">
            <li>Test your solution here before submitting</li>
            <li>Make sure output matches expected results</li>
            <li>After testing, copy your code and submit</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default CodeEditor;
