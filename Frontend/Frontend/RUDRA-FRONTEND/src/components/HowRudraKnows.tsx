import { useState } from 'react';
import { CheckCircle2, ChevronRight, Database, ExternalLink, Layers, ShieldCheck } from 'lucide-react';
import type { Evidence } from '@/types';

interface HowRudraKnowsProps {
  evidence?: Evidence[];
}

function formatAgentName(name: string): string {
  if (!name) return 'RUDRA Agent';
  return name
    .replace(/_/g, ' ')
    .replace(/\bagent\b/i, '')
    .trim()
    .split(' ')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ') + ' Agent';
}

function formatRetrievalMethod(method: string): string {
  switch (method) {
    case 'filtered_json': return 'Filtered JSON lookup';
    case 'exact_lookup': return 'Exact database lookup';
    case 'structured_json': return 'Structured dataset query';
    case 'semantic_search': return 'Semantic vector search';
    case 'hybrid_search': return 'Hybrid semantic search';
    case 'external_search': return 'External web discovery';
    case 'database_query': return 'Database query';
    default: return method.replace(/_/g, ' ');
  }
}

function formatFilters(filters?: Record<string, unknown>): string {
  if (!filters || Object.keys(filters).length === 0) return 'None';
  return Object.entries(filters)
    .filter(([_, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => `${k.charAt(0).toUpperCase() + k.slice(1)}: ${String(v)}`)
    .join(' · ');
}

export default function HowRudraKnows({ evidence }: HowRudraKnowsProps) {
  const [expanded, setExpanded] = useState(false);

  if (!evidence || evidence.length === 0) {
    return null;
  }

  const hasExternal = evidence.some(e => e.source_type === 'external_web' || e.metadata?.is_external);

  return (
    <div className="mt-3 pt-2 border-t border-app/60 text-xs transition-all">
      {/* Header bar */}
      <div className="flex items-center justify-between text-muted hover:text-foreground">
        <div className="flex items-center gap-1.5 font-medium text-[11px]">
          <CheckCircle2 className={`w-3.5 h-3.5 ${hasExternal ? 'text-blue-500' : 'text-emerald-500'}`} />
          <span>{hasExternal ? 'Sourced from verified & external data' : 'Verified from RUDRA data'}</span>
        </div>
        <button
          onClick={() => setExpanded(prev => !prev)}
          className="flex items-center gap-1 px-2 py-0.5 rounded-md hover:bg-app text-[11px] font-medium text-brand-600 dark:text-brand-400 transition"
        >
          <ChevronRight className={`w-3 h-3 transition-transform duration-200 ${expanded ? 'rotate-90' : ''}`} />
          <span>How RUDRA knows</span>
        </button>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="mt-2.5 space-y-2.5 p-3 rounded-xl surface-2 border border-app animate-slide-up text-muted">
          <div className="text-[10px] font-bold uppercase tracking-wider text-muted/80 mb-1 flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-brand-600" />
            HOW RUDRA KNOWS
          </div>

          {evidence.map((ev, idx) => {
            const pages = Array.isArray(ev.metadata?.pages) ? (ev.metadata.pages as number[]).join(', ') : null;
            const isExternal = ev.source_type === 'external_web' || ev.metadata?.is_external;

            return (
              <div key={ev.id || idx} className="text-xs space-y-1 p-2 rounded-lg bg-background/50 border border-app/40">
                <div className="flex items-center justify-between font-medium text-foreground">
                  <div className="flex items-center gap-1.5">
                    {ev.source_type === 'vector_database' ? (
                      <Layers className="w-3.5 h-3.5 text-purple-500" />
                    ) : isExternal ? (
                      <ExternalLink className="w-3.5 h-3.5 text-blue-500" />
                    ) : (
                      <Database className="w-3.5 h-3.5 text-brand-600" />
                    )}
                    <span className="font-semibold text-xs">{ev.source_name}</span>
                  </div>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${isExternal ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400' : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'}`}>
                    {isExternal ? 'External Opportunity' : '✓ Verified'}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-1 text-[11px] pt-1">
                  <div>
                    <span className="text-muted/70">Agent:</span>{' '}
                    <span className="font-medium text-foreground/90">{formatAgentName(ev.agent)}</span>
                  </div>

                  <div>
                    <span className="text-muted/70">Source:</span>{' '}
                    <span className="font-medium text-foreground/90">{ev.source_name}</span>
                  </div>

                  {ev.source_file && (
                    <div>
                      <span className="text-muted/70">Dataset:</span>{' '}
                      <code className="text-[10px] bg-app px-1 py-0.5 rounded text-foreground/90">{ev.source_file}</code>
                    </div>
                  )}

                  <div>
                    <span className="text-muted/70">Retrieval:</span>{' '}
                    <span className="font-medium text-foreground/90">{formatRetrievalMethod(ev.retrieval_method)}</span>
                  </div>

                  <div>
                    <span className="text-muted/70">Records matched:</span>{' '}
                    <span className="font-medium text-foreground/90">{ev.records_matched}</span>
                  </div>

                  {pages && (
                    <div>
                      <span className="text-muted/70">Relevant sections:</span>{' '}
                      <span className="font-medium text-foreground/90">Pages {pages}</span>
                    </div>
                  )}
                </div>

                {ev.filters && Object.keys(ev.filters).length > 0 && (
                  <div className="text-[11px] pt-0.5">
                    <span className="text-muted/70">Filters:</span>{' '}
                    <span className="font-medium text-foreground/90">{formatFilters(ev.filters)}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
