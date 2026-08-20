import { Sparkles } from 'lucide-react';

interface FollowUpChipsProps {
  items: string[];
  onPick: (prompt: string) => void;
  compact?: boolean;
}

export default function FollowUpChips({ items, onPick, compact }: FollowUpChipsProps) {
  if (!items.length) return null;

  return (
    <div className={`${compact ? 'mt-2' : 'mt-4'} animate-fade-in`}>
      {!compact && (
        <div className="flex items-center gap-1.5 text-[11px] font-medium text-muted mb-2 uppercase tracking-wide">
          <Sparkles className="w-3 h-3 text-brand-500" />
          Suggested follow-ups
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        {items.map((item, i) => (
          <button
            key={`${item}-${i}`}
            type="button"
            onClick={() => onPick(item)}
            className="text-left text-xs sm:text-sm px-3 py-2 rounded-xl border border-app surface-2 hover:border-brand-500 hover:bg-brand-50/50 dark:hover:bg-brand-900/20 hover:text-brand-700 dark:hover:text-brand-300 transition shadow-sm max-w-full truncate"
            title={item}
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}
