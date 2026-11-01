import { useContext } from 'react';
import { StorySessionContext } from '../context/storySessionContextDef';

export function useStorySession() {
  const context = useContext(StorySessionContext);
  if (!context) {
    throw new Error('useStorySession must be used within a StorySessionProvider');
  }
  return context;
}
