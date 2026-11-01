import { createContext } from 'react';
import type { GenerateStoryRequest, Genre, Mood, StoryLength, Story } from '../types';

export interface FormDraftState {
  prompt: string;
  genre: Genre;
  mood: Mood;
  length: StoryLength;
  file: File | null;
}

export interface StorySessionContextType {
  // Generation & Active Story State
  isGenerating: boolean;
  error: string | null;
  activeStory: Story | null;
  lastRequest: GenerateStoryRequest | null;
  lastUploadedFile: File | null;

  // Form Draft State (Preserved across route navigation)
  formDraft: FormDraftState;
  updateFormDraft: (updates: Partial<FormDraftState>) => void;
  resetFormDraft: () => void;

  // Actions
  generateStory: (req: GenerateStoryRequest, file: File | null) => Promise<Story | null>;
  regenerateStory: () => Promise<Story | null>;
  editPromptAndPreferences: () => void;
  clearActiveStory: () => void;
  clearError: () => void;
  setActiveStoryDirectly: (story: Story | null) => void;
}

export const StorySessionContext = createContext<StorySessionContextType | null>(null);
