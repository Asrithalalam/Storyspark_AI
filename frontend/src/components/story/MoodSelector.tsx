import React from 'react';
import { ALLOWED_MOODS, type Mood } from '../../types';
import { Heart } from 'lucide-react';

interface MoodSelectorProps {
  value: string;
  onChange: (mood: Mood) => void;
  disabled?: boolean;
}

export const MoodSelector: React.FC<MoodSelectorProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 font-serif text-base sm:text-[17px] font-extrabold text-[#2B1B2A] tracking-tight">
          <Heart className="h-4.5 w-4.5 text-[#9C8EB9]" />
          <span>Mood</span>
        </label>
      </div>

      <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Select story mood">
        {ALLOWED_MOODS.map((mood) => {
          const isSelected = value.toLowerCase() === mood.toLowerCase();
          return (
            <button
              key={mood}
              type="button"
              role="radio"
              aria-checked={isSelected}
              disabled={disabled}
              onClick={() => onChange(mood)}
              className={`rounded-xl px-3.5 py-1.5 font-sans text-xs transition-all cursor-pointer disabled:opacity-50 border ${
                isSelected
                  ? 'border-[#9C8EB9] bg-[#F4F0F7] text-[#4C355E] font-semibold ring-1 ring-[#9C8EB9]/30 shadow-2xs'
                  : 'border-[#E6DFD6] bg-[#FCFBF9] text-[#4A3D49] font-medium hover:border-[#D4C3B7] hover:bg-[#FAF7F2]'
              }`}
            >
              {mood}
            </button>
          );
        })}
      </div>
    </div>
  );
};
