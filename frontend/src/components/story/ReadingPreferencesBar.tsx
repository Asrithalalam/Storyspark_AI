import React from 'react';
import { RotateCcw, Type } from 'lucide-react';
import type { FontFamilyOption, ReadingPreferences } from '../../hooks/useReadingPreferences';

interface ReadingPreferencesBarProps {
  preferences: ReadingPreferences;
  onSetFontFamily: (font: FontFamilyOption) => void;
  onSetFontSize: (size: number) => void;
  onSetLineHeight: (height: number) => void;
  onReset: () => void;
}

export const ReadingPreferencesBar: React.FC<ReadingPreferencesBarProps> = ({
  preferences,
  onSetFontFamily,
  onSetFontSize,
  onSetLineHeight,
  onReset,
}) => {
  return (
    <div className="rounded-2xl border border-[#E8E0D5] bg-[#FAF8F5] p-4.5 shadow-sm space-y-4 text-left transition-all">
      <div className="flex items-center justify-between pb-2.5 border-b border-[#EFE8DF]">
        <div className="flex items-center gap-2 text-xs font-semibold text-[#352033] font-serif">
          <Type className="h-4 w-4 text-[#D96B50]" />
          <span>Reading Comfort Preferences</span>
        </div>
        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-1 text-xs text-[#7A6C79] hover:text-[#C9593E] transition-colors cursor-pointer"
          title="Reset to default typography settings"
        >
          <RotateCcw className="h-3 w-3" />
          <span>Reset Defaults</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* 1. Font Family */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-[#7A6C79]">
            Font Family
          </label>
          <div className="flex rounded-xl border border-[#E6DFD6] bg-[#F2ECE4] p-0.5">
            <button
              type="button"
              onClick={() => onSetFontFamily('serif')}
              className={`flex-1 rounded-lg py-1 text-xs font-serif transition-colors cursor-pointer ${
                preferences.fontFamily === 'serif'
                  ? 'bg-white text-[#9E3F27] font-semibold shadow-xs'
                  : 'text-[#6A5A68] hover:text-[#352033]'
              }`}
            >
              Serif
            </button>
            <button
              type="button"
              onClick={() => onSetFontFamily('sans')}
              className={`flex-1 rounded-lg py-1 text-xs font-sans transition-colors cursor-pointer ${
                preferences.fontFamily === 'sans'
                  ? 'bg-white text-[#9E3F27] font-semibold shadow-xs'
                  : 'text-[#6A5A68] hover:text-[#352033]'
              }`}
            >
              Sans
            </button>
            <button
              type="button"
              onClick={() => onSetFontFamily('mono')}
              className={`flex-1 rounded-lg py-1 text-xs font-mono transition-colors cursor-pointer ${
                preferences.fontFamily === 'mono'
                  ? 'bg-white text-[#9E3F27] font-semibold shadow-xs'
                  : 'text-[#6A5A68] hover:text-[#352033]'
              }`}
            >
              Mono
            </button>
          </div>
        </div>

        {/* 2. Font Size */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <label htmlFor="font-size-slider" className="font-medium text-[#7A6C79]">
              Font Size
            </label>
            <span className="font-mono text-[#352033] font-medium">{preferences.fontSize}px</span>
          </div>
          <div className="flex items-center gap-2 pt-1">
            <span className="text-[11px] text-[#A697A5] font-mono">14</span>
            <input
              id="font-size-slider"
              type="range"
              min={14}
              max={32}
              step={1}
              value={preferences.fontSize}
              onChange={(e) => onSetFontSize(Number(e.target.value))}
              className="w-full accent-[#D96B50] cursor-pointer"
            />
            <span className="text-[11px] text-[#A697A5] font-mono">32</span>
          </div>
        </div>

        {/* 3. Line Spacing */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <label htmlFor="line-height-slider" className="font-medium text-[#7A6C79]">
              Line Spacing
            </label>
            <span className="font-mono text-[#352033] font-medium">{preferences.lineHeight}x</span>
          </div>
          <div className="flex items-center gap-2 pt-1">
            <span className="text-[11px] text-[#A697A5] font-mono">1.2</span>
            <input
              id="line-height-slider"
              type="range"
              min={1.2}
              max={2.4}
              step={0.1}
              value={preferences.lineHeight}
              onChange={(e) => onSetLineHeight(Number(e.target.value))}
              className="w-full accent-[#D96B50] cursor-pointer"
            />
            <span className="text-[11px] text-[#A697A5] font-mono">2.4</span>
          </div>
        </div>
      </div>
    </div>
  );
};
