import React, { useState } from 'react';
import { Sparkles, X, PenLine, ChevronDown, ChevronUp } from 'lucide-react';
import { SUGGESTED_PROMPTS, type SuggestedPrompt } from '../../types';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onSelectSuggestion?: (suggestion: SuggestedPrompt) => void;
  disabled?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  value,
  onChange,
  onSelectSuggestion,
  disabled = false,
}) => {
  const maxLength = 5000;
  const [showSuggestions, setShowSuggestions] = useState(false);

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between">
        <label
          htmlFor="story-prompt-input"
          className="flex items-center gap-2 font-serif text-base sm:text-[17px] font-extrabold text-[#2B1B2A] tracking-tight"
        >
          <PenLine className="h-4.5 w-4.5 text-[#D96B50]" />
          <span>Written Idea</span>
        </label>
        <span className="font-sans text-xs font-normal text-[#8A7988]">
          {value.length} / 5000
        </span>
      </div>

      <div className="relative rounded-2xl border border-[#E4DDD4] bg-[#FCFBF9] transition-all focus-within:border-[#D96B50] focus-within:ring-2 focus-within:ring-[#D96B50]/15 shadow-2xs">
        <textarea
          id="story-prompt-input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          maxLength={maxLength}
          rows={4}
          placeholder="Your story starts with an idea. Add a few words to begin..."
          className="w-full resize-y bg-transparent px-4 py-3.5 text-sm text-[#352033] placeholder-[#9E909D] focus:outline-none disabled:opacity-50 min-h-[105px] max-h-[260px] leading-relaxed"
        />

        {value && !disabled && (
          <button
            type="button"
            onClick={() => onChange('')}
            className="absolute top-3 right-3 rounded-xl p-1 text-[#9E909D] hover:bg-[#F0E9DF] hover:text-[#352033] transition-colors cursor-pointer"
            title="Clear prompt"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Expandable inspiration suggestions */}
      <div className="space-y-2 pt-0.5">
        <button
          type="button"
          onClick={() => setShowSuggestions((prev) => !prev)}
          className="inline-flex items-center gap-1.5 text-xs text-[#7A6C79] hover:text-[#C85E45] transition-colors cursor-pointer"
        >
          <Sparkles className="h-3.5 w-3.5 text-[#D96B50]" />
          <span>{showSuggestions ? 'Hide inspiration ideas' : 'Need inspiration? Try an idea'}</span>
          {showSuggestions ? (
            <ChevronUp className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
        </button>

        {showSuggestions && (
          <div className="flex flex-wrap gap-2 pt-1 animate-in fade-in duration-200">
            {SUGGESTED_PROMPTS.map((item) => (
              <button
                key={item.id}
                type="button"
                disabled={disabled}
                onClick={() => {
                  onSelectSuggestion?.(item);
                  setShowSuggestions(false);
                }}
                className="inline-flex items-center gap-1.5 rounded-xl border border-[#EAE2D8] bg-[#FAF5EE] px-3 py-1.5 text-xs text-[#5C4558] hover:bg-[#F3EBE0] hover:border-[#D8C7B8] hover:text-[#352033] transition-all disabled:opacity-50 cursor-pointer shadow-2xs"
              >
                <span className="font-medium">"{item.prompt}"</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
