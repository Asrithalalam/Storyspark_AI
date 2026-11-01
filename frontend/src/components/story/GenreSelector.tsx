import React from 'react';
import { ALLOWED_GENRES, type Genre } from '../../types';
import {
  Sparkles,
  Compass,
  Key,
  Globe,
  Heart,
  Laugh,
  Flame,
  BookOpen,
} from 'lucide-react';

interface GenreSelectorProps {
  value: string;
  onChange: (genre: Genre) => void;
  disabled?: boolean;
}

const GENRE_MOTIFS: Record<string, { icon: React.FC<{ className?: string }>; description: string }> = {
  Fantasy: { icon: Sparkles, description: 'Step into the extraordinary.' },
  Mystery: { icon: Key, description: 'Follow the clues.' },
  Adventure: { icon: Compass, description: 'Discover the unknown.' },
  'Science Fiction': { icon: Globe, description: "Explore tomorrow's worlds." },
  Romance: { icon: Heart, description: 'Whispers of the heart.' },
  Comedy: { icon: Laugh, description: 'Find joy in the unexpected.' },
  Inspirational: { icon: Flame, description: 'Stories that uplift the spirit.' },
  Fiction: { icon: BookOpen, description: 'Moments of human truth.' },
};

export const GenreSelector: React.FC<GenreSelectorProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 font-serif text-base sm:text-[17px] font-extrabold text-[#2B1B2A] tracking-tight">
          <BookOpen className="h-4.5 w-4.5 text-[#C85E45]" />
          <span>Genre</span>
        </label>
      </div>

      <div
        className="grid grid-cols-2 sm:grid-cols-4 gap-2"
        role="radiogroup"
        aria-label="Select story genre"
      >
        {ALLOWED_GENRES.map((genre) => {
          const isSelected = value.toLowerCase() === genre.toLowerCase();
          const info = GENRE_MOTIFS[genre] || { icon: Sparkles, description: 'Creative story.' };
          const Icon = info.icon;

          return (
            <button
              key={genre}
              type="button"
              role="radio"
              aria-checked={isSelected}
              disabled={disabled}
              onClick={() => onChange(genre)}
              className={`flex items-center gap-2.5 p-2.5 rounded-2xl border text-left transition-all cursor-pointer disabled:opacity-50 ${
                isSelected
                  ? 'border-[#C85E45] bg-[#FAF3EE] ring-1 ring-[#C85E45]/25 shadow-2xs'
                  : 'border-[#EAE2D8] bg-[#FCFBF9] hover:border-[#D4C4B6] hover:bg-[#FAF7F2]'
              }`}
            >
              <div
                className={`h-7 w-7 rounded-xl flex items-center justify-center shrink-0 transition-colors ${
                  isSelected ? 'bg-[#C85E45] text-white shadow-xs' : 'bg-[#F2ECE4] text-[#7D6B8D]'
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
              </div>
              <span
                className={`font-sans text-xs sm:text-[13px] truncate leading-tight ${
                  isSelected ? 'font-semibold text-[#C85E45]' : 'font-medium text-[#463745]'
                }`}
              >
                {genre}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
