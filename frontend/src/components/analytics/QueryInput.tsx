import React, { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { Button } from '../common/Button';

interface QueryInputProps {
  onSearch?: (question: string) => void;
  value?: string;
  onChange?: (val: string) => void;
  onSubmit?: () => void;
  isLoading?: boolean;
  placeholder?: string;
}

export const QueryInput: React.FC<QueryInputProps> = ({
  onSearch,
  value,
  onChange,
  onSubmit,
  isLoading = false,
  placeholder = 'Ask FreshMart any business, sales, inventory, HR, or financial question...',
}) => {
  const [internalVal, setInternalVal] = useState('');

  const currentVal = value !== undefined ? value : internalVal;

  const handleChange = (newVal: string) => {
    if (onChange) {
      onChange(newVal);
    } else {
      setInternalVal(newVal);
    }
  };

  const suggestions = [
    'Why did profit decrease in August?',
    'Show monthly sales for the last 12 months.',
    'Which products are low in stock?',
    'Show leads by status.',
    'Show employee salaries.', // Useful for testing 403 RBAC guard
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentVal.trim() || isLoading) return;

    if (onSubmit) {
      onSubmit();
    } else if (onSearch) {
      onSearch(currentVal.trim());
      setInternalVal('');
    }
  };

  const handleSuggestionClick = (q: string) => {
    if (isLoading) return;
    if (onChange) {
      onChange(q);
    }
    if (onSearch) {
      onSearch(q);
    }
  };

  return (
    <div className="w-full space-y-3">
      {/* Main Text Input (NO MICROPHONE BUTTON!) */}
      <form onSubmit={handleSubmit} className="relative flex items-center shadow-2xl">
        <input
          type="text"
          value={currentVal}
          disabled={isLoading}
          onChange={(e) => handleChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-[#0F1626] border border-slate-700/80 focus:border-emerald-500 rounded-2xl pl-5 pr-28 py-4 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 transition-all shadow-inner disabled:opacity-60"
        />
        <div className="absolute right-2.5">
          <Button
            type="submit"
            size="md"
            variant="primary"
            disabled={!currentVal.trim() || isLoading}
            isLoading={isLoading}
            icon={<Send className="w-4 h-4" />}
          >
            <span>Ask AI</span>
          </Button>
        </div>
      </form>

      {/* Suggested Query Chips if no external suggestions rendered */}
      {!onChange && (
        <div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-2 font-medium">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Suggested analytical prompts:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((sug) => (
              <button
                key={sug}
                type="button"
                disabled={isLoading}
                onClick={() => handleSuggestionClick(sug)}
                className="text-xs px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-emerald-300 hover:border-emerald-500/40 hover:bg-emerald-950/20 transition-all text-left disabled:opacity-50"
              >
                {sug}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
