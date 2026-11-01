import { useState, useEffect, useCallback } from 'react';

export type FontFamilyOption = 'sans' | 'serif' | 'mono';

export interface ReadingPreferences {
  fontFamily: FontFamilyOption;
  fontSize: number; // 14px to 32px
  lineHeight: number; // 1.2 to 2.4
}

export const DEFAULT_READING_PREFERENCES: ReadingPreferences = {
  fontFamily: 'sans',
  fontSize: 16,
  lineHeight: 1.8,
};

const STORAGE_KEY = 'storyspark_reading_preferences_v1';

export function useReadingPreferences() {
  const [preferences, setPreferences] = useState<ReadingPreferences>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return {
          fontFamily: ['sans', 'serif', 'mono'].includes(parsed.fontFamily)
            ? parsed.fontFamily
            : DEFAULT_READING_PREFERENCES.fontFamily,
          fontSize:
            typeof parsed.fontSize === 'number' && parsed.fontSize >= 14 && parsed.fontSize <= 32
              ? parsed.fontSize
              : DEFAULT_READING_PREFERENCES.fontSize,
          lineHeight:
            typeof parsed.lineHeight === 'number' && parsed.lineHeight >= 1.2 && parsed.lineHeight <= 2.4
              ? parsed.lineHeight
              : DEFAULT_READING_PREFERENCES.lineHeight,
        };
      }
    } catch {
      // Fallback on storage read error
    }
    return DEFAULT_READING_PREFERENCES;
  });

  // Sync to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
    } catch {
      // Ignore quota/storage errors
    }
  }, [preferences]);

  const setFontFamily = useCallback((fontFamily: FontFamilyOption) => {
    setPreferences((prev) => ({ ...prev, fontFamily }));
  }, []);

  const setFontSize = useCallback((fontSize: number) => {
    const clamped = Math.min(32, Math.max(14, fontSize));
    setPreferences((prev) => ({ ...prev, fontSize: clamped }));
  }, []);

  const setLineHeight = useCallback((lineHeight: number) => {
    const clamped = Math.min(2.4, Math.max(1.2, parseFloat(lineHeight.toFixed(1))));
    setPreferences((prev) => ({ ...prev, lineHeight: clamped }));
  }, []);

  const resetToDefaults = useCallback(() => {
    setPreferences(DEFAULT_READING_PREFERENCES);
  }, []);

  return {
    preferences,
    setFontFamily,
    setFontSize,
    setLineHeight,
    resetToDefaults,
  };
}
