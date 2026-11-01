import React from 'react';
import { LENGTH_OPTIONS, type StoryLength } from '../../types';
import { BookMarked } from 'lucide-react';

interface LengthSelectorProps {
  value: string;
  onChange: (length: StoryLength) => void;
  disabled?: boolean;
}

export const LengthSelector: React.FC<LengthSelectorProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 font-serif text-base sm:text-[17px] font-extrabold text-[#2B1B2A] tracking-tight">
          <BookMarked className="h-4.5 w-4.5 text-[#D96B50]" />
          <span>Story Length</span>
        </label>
      </div>

      <div
        className="grid grid-cols-3 gap-2"
        role="radiogroup"
        aria-label="Select story length"
      >
        {LENGTH_OPTIONS.map((opt) => {
          const isSelected = value.toLowerCase() === opt.value.toLowerCase();
          return (
            <button
              key={opt.value}
              type="button"
              role="radio"
              aria-checked={isSelected}
              disabled={disabled}
              onClick={() => onChange(opt.value)}
              className={`flex flex-col text-left p-2.5 sm:p-3 rounded-2xl border transition-all cursor-pointer disabled:opacity-50 ${
                isSelected
                  ? 'border-[#D96B50] bg-[#FAF2EE] ring-1 ring-[#D96B50]/30 shadow-2xs'
                  : 'border-[#E6DFD6] bg-[#FCFBF9] hover:border-[#D4C3B7] hover:bg-[#FAF7F2]'
              }`}
            >
              <div className="flex items-center justify-between">
                <span
                  className={`font-sans text-xs sm:text-[13px] ${
                    isSelected ? 'font-semibold text-[#9E3F27]' : 'font-medium text-[#352033]'
                  }`}
                >
                  {opt.label}
                </span>
                <span className="text-[10px] text-[#7A6C79] font-mono">{opt.targetRange}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
