import { useState, useCallback } from 'react';
import { api, ApiError } from '../services/api';
import type { GenerateStoryRequest, Story } from '../types';

export function useStoryGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStory, setCurrentStory] = useState<Story | null>(null);
  const [lastRequest, setLastRequest] = useState<GenerateStoryRequest | null>(null);

  const generate = useCallback(async (payload: GenerateStoryRequest): Promise<Story | null> => {
    setIsGenerating(true);
    setError(null);
    setLastRequest(payload);

    try {
      const story = await api.generateStory(payload);
      setCurrentStory(story);
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
  }, []);

  const regenerate = useCallback(async (): Promise<Story | null> => {
    if (!lastRequest || isGenerating) return null;

    setIsGenerating(true);
    setError(null);

    try {
      const story = await api.generateStory(lastRequest);
      setCurrentStory(story);
      return story;
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "We couldn't create your story. Please try again.";
      setError(message);
      // Preserves existing currentStory so previous story remains visible
      return null;
    } finally {
      setIsGenerating(false);
    }
  }, [lastRequest, isGenerating]);

  const clearStory = useCallback(() => {
    setCurrentStory(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const resetAll = useCallback(() => {
    setCurrentStory(null);
    setError(null);
    setIsGenerating(false);
    setLastRequest(null);
  }, []);

  return {
    isGenerating,
    error,
    currentStory,
    lastRequest,
    generate,
    regenerate,
    clearStory,
    clearError,
    resetAll,
  };
}
