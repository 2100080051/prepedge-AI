interface SkeletonProps {
  className?: string;
}

function SkeletonBase({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`animate-shimmer bg-gradient-to-r from-slate-100 via-slate-200 to-slate-100 rounded-lg ${className}`}
      style={{ backgroundSize: '400% 100%' }}
    />
  );
}

export function SkeletonText({ className = 'h-4 w-full' }: SkeletonProps) {
  return <SkeletonBase className={className} />;
}

export function SkeletonCard({ className = '' }: SkeletonProps) {
  return (
    <div className={`glass-card rounded-2xl p-6 animate-fade-in ${className}`}>
      <div className="flex items-center gap-4 mb-4">
        <SkeletonBase className="w-12 h-12 rounded-xl flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <SkeletonBase className="h-4 w-2/3" />
          <SkeletonBase className="h-3 w-1/3" />
        </div>
      </div>
      <div className="space-y-2">
        <SkeletonBase className="h-3 w-full" />
        <SkeletonBase className="h-3 w-full" />
        <SkeletonBase className="h-3 w-3/4" />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="glass-card rounded-2xl overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="flex gap-4 px-5 py-4 border-b border-slate-100 bg-slate-50">
        {Array.from({ length: cols }).map((_, i) => (
          <SkeletonBase key={i} className="h-3 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, ri) => (
        <div key={ri} className="flex items-center gap-4 px-5 py-4 border-b border-slate-50 last:border-0">
          <SkeletonBase className="w-8 h-8 rounded-full flex-shrink-0" />
          {Array.from({ length: cols - 1 }).map((_, ci) => (
            <SkeletonBase key={ci} className={`h-3.5 flex-1 ${ci === 0 ? 'w-1/3' : ''}`} />
          ))}
          <SkeletonBase className="w-16 h-7 rounded-lg flex-shrink-0" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonHero() {
  return (
    <div className="text-center max-w-3xl mx-auto space-y-5 animate-fade-in">
      <SkeletonBase className="h-5 w-40 mx-auto rounded-full" />
      <SkeletonBase className="h-12 w-3/4 mx-auto rounded-xl" />
      <SkeletonBase className="h-12 w-1/2 mx-auto rounded-xl" />
      <SkeletonBase className="h-5 w-2/3 mx-auto" />
      <SkeletonBase className="h-5 w-1/2 mx-auto" />
    </div>
  );
}

export function SkeletonStatRow({ count = 3 }: { count?: number }) {
  return (
    <div className={`grid gap-4 animate-fade-in`} style={{ gridTemplateColumns: `repeat(${count}, 1fr)` }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="glass-card rounded-2xl p-5 text-center space-y-2">
          <SkeletonBase className="w-10 h-10 rounded-xl mx-auto" />
          <SkeletonBase className="h-7 w-16 mx-auto" />
          <SkeletonBase className="h-3 w-20 mx-auto" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonQuestion({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-3 animate-fade-in">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="glass-card rounded-2xl p-5 flex items-center gap-4">
          <div className="flex-1 space-y-2">
            <SkeletonBase className="h-4 w-full" />
            <SkeletonBase className="h-3 w-2/3" />
            <div className="flex gap-2 pt-1">
              <SkeletonBase className="h-5 w-14 rounded-lg" />
              <SkeletonBase className="h-5 w-20 rounded-lg" />
              <SkeletonBase className="h-5 w-16 rounded-lg" />
            </div>
          </div>
          <SkeletonBase className="h-9 w-20 rounded-xl flex-shrink-0" />
        </div>
      ))}
    </div>
  );
}

// Default export — generic skeleton
export default SkeletonBase;
