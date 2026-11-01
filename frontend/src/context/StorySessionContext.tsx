import React, { useState, useCallback, useMemo } from 'react';
import { api, ApiError } from '../services/api';
import type { GenerateStoryRequest, Genre, Mood, StoryLength, Story } from '../types';
import { StorySessionContext, type FormDraftState } from './storySessionContextDef';

const defaultDraft: FormDraftState = {
  prompt: '',
  genre: 'Fantasy',
  mood: 'Mysterious',
  length: 'Short',
  file: null,
};

export const StorySessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStory, setActiveStory] = useState<Story | null>(null);
  const [lastRequest, setLastRequest] = useState<GenerateStoryRequest | null>(null);
  const [lastUploadedFile, setLastUploadedFile] = useState<File | null>(null);

  // Form draft preserved across tab/page navigation
  const [formDraft, setFormDraft] = useState<FormDraftState>(defaultDraft);

  const updateFormDraft = useCallback((updates: Partial<FormDraftState>) => {
    setFormDraft((prev) => ({ ...prev, ...updates }));
  }, []);

  const resetFormDraft = useCallback(() => {
    setFormDraft(defaultDraft);
  }, []);

  const generateStory = useCallback(
    async (payload: GenerateStoryRequest, file: File | null): Promise<Story | null> => {
      setIsGenerating(true);
      setError(null);
      setLastRequest(payload);
      setLastUploadedFile(file);

      try {
        const story = await api.generateStory(payload);
        setActiveStory(story);
        return story;
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "We couldn't create your story. Please try again.";
        setError(message);
        return null;
      } finally {
        setIsGenerating(false);
      }
    },
    []
  );

  const regenerateStory = useCallback(async (): Promise<Story | null> => {
    if (!lastRequest || isGenerating) return null;

    setIsGenerating(true);
    setError(null);

    try {
      const story = await api.generateStory(lastRequest);
      setActiveStory(story);
      return story;
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "We couldn't create your story. Please try again.";
      setError(message);
      // Preserves existing activeStory in view
      return null;
    } finally {
      setIsGenerating(false);
    }
  }, [lastRequest, isGenerating]);

  // "Edit Prompt / Preferences": restores previous inputs to the form and exits reader view
  const editPromptAndPreferences = useCallback(() => {
    if (lastRequest) {
      setFormDraft({
        prompt: lastRequest.prompt || '',
        genre: (lastRequest.genre as Genre) || 'Fantasy',
        mood: (lastRequest.mood as Mood) || 'Mysterious',
        length: (lastRequest.length as StoryLength) || 'Short',
        file: lastUploadedFile,
      });
    }
    setActiveStory(null);
  }, [lastRequest, lastUploadedFile]);

  const clearActiveStory = useCallback(() => {
    setActiveStory(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const setActiveStoryDirectly = useCallback((story: Story | null) => {
    setActiveStory(story);
  }, []);

  const value = useMemo(
    () => ({
      isGenerating,
      error,
      activeStory,
      lastRequest,
      lastUploadedFile,
      formDraft,
      updateFormDraft,
      resetFormDraft,
      generateStory,
      regenerateStory,
      editPromptAndPreferences,
      clearActiveStory,
      clearError,
      setActiveStoryDirectly,
    }),
    [
      isGenerating,
      error,
      activeStory,
      lastRequest,
      lastUploadedFile,
      formDraft,
      updateFormDraft,
      resetFormDraft,
      generateStory,
      regenerateStory,
      editPromptAndPreferences,
      clearActiveStory,
      clearError,
      setActiveStoryDirectly,
    ]
  );

  return <StorySessionContext.Provider value={value}>{children}</StorySessionContext.Provider>;
};
