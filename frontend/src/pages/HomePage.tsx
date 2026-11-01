import React, { useRef } from 'react';
import { Sparkles, BookOpen, Feather } from 'lucide-react';
import { useStorySession } from '../hooks/useStorySession';
import { StoryCreationForm } from '../components/story/StoryCreationForm';
import { StoryReader } from '../components/story/StoryReader';
import type { GenerateStoryRequest } from '../types';

export const HomePage: React.FC = () => {
  const studioRef = useRef<HTMLDivElement | null>(null);

  const {
    isGenerating,
    error,
    activeStory,
    formDraft,
    updateFormDraft,
    generateStory,
    regenerateStory,
    editPromptAndPreferences,
    clearActiveStory,
    clearError,
  } = useStorySession();

  const handleGenerateStory = async (req: GenerateStoryRequest, file: File | null) => {
    await generateStory(req, file);
  };

  const handleRegenerate = async () => {
    await regenerateStory();
  };

  const handleEditPrompt = () => {
    editPromptAndPreferences();
    setTimeout(() => {
      studioRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  };

  const handleCreateNewStory = () => {
    clearActiveStory();
    clearError();
    setTimeout(() => {
      studioRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  };

  return (
    <div className="w-full flex-1 flex flex-col items-center justify-start text-center bg-[#ECE5DC] min-h-[calc(100vh-65px)] transition-colors">
      {/* Editorial Hero with Rich Deep Plum Contrast (Creation Mode) */}
      {!activeStory ? (
        <section className="relative w-full overflow-hidden bg-gradient-to-b from-[#241524] via-[#2D1A2C] to-[#251524] text-white px-4 pt-12 pb-14 sm:px-6 sm:pt-16 sm:pb-18 shadow-md">
          {/* Subtle Storytelling Ambient Glow - Clean & Uncluttered */}
          <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
            <div className="absolute -top-24 left-1/2 -translate-x-1/2 h-64 w-[36rem] rounded-full bg-[#C85E45]/15 blur-3xl" />
            <div className="absolute top-1/2 right-12 h-52 w-52 rounded-full bg-[#8E7C9D]/15 blur-3xl" />
            <div className="absolute bottom-0 left-12 h-44 w-44 rounded-full bg-[#C85E45]/10 blur-2xl" />
          </div>

          <div className="relative z-10 max-w-3xl mx-auto space-y-4 animate-in fade-in duration-300">
            {/* Brand Identity & Tagline */}
            <div className="flex flex-col items-center gap-1.5">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-xs font-semibold text-[#F7EFF8] backdrop-blur-md shadow-xs">
                <Feather className="h-3.5 w-3.5 text-[#E88C74]" />
                <span className="font-serif tracking-wider font-bold">StorySpark AI</span>
              </div>
              <p className="font-serif text-xs sm:text-sm italic text-[#CDBDD8] font-normal tracking-wide">
                Where ideas become stories.
              </p>
            </div>

            {/* Main Hero Heading with Distinctive Font, Size & Weight */}
            <h1 className="font-hero text-3xl sm:text-5xl md:text-[3.25rem] font-bold tracking-tight text-white leading-[1.18] max-w-2xl mx-auto">
              Every little idea has a story waiting to unfold.
            </h1>

            {/* Visually Secondary Supporting Text */}
            <p className="font-sans text-xs sm:text-sm font-normal text-[#D2C3D8]/80 leading-relaxed max-w-lg mx-auto">
              Turn your words and visual inspiration into stories filled with imagination.
            </p>
          </div>
        </section>
      ) : (
        /* Brand Ribbon in Story Reader View */
        <div className="w-full max-w-4xl mx-auto flex items-center justify-between px-4 pt-7 sm:px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-[#C85E45] to-[#8E7C9D] text-white shadow-sm shadow-[#C85E45]/20">
              <BookOpen className="h-4 w-4" />
            </div>
            <div className="text-left">
              <p className="font-serif text-sm font-bold tracking-tight text-[#2B1B2A]">
                StorySpark AI
              </p>
              <p className="font-serif text-xs italic text-[#7D6B8D]">
                Where ideas become stories.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleCreateNewStory}
            className="inline-flex items-center gap-1.5 rounded-xl border border-[#D5C7B8] bg-[#FFFFFF] px-3.5 py-1.5 text-xs font-medium text-[#4D3B4B] hover:bg-[#F5EFEB] hover:text-[#2B1B2A] transition-all cursor-pointer shadow-2xs active:scale-95"
            title="Start crafting another story"
          >
            <Sparkles className="h-3.5 w-3.5 text-[#C85E45]" />
            <span>New Story</span>
          </button>
        </div>
      )}

      {/* Main Interactive Studio: Creation Form or Story Reader */}
      <div
        ref={studioRef}
        className="w-full flex justify-center px-4 py-8 sm:px-6 md:py-10 scroll-mt-20"
      >
        {activeStory ? (
          <StoryReader
            story={activeStory}
            isRegenerating={isGenerating}
            regenerationError={error}
            onRegenerate={handleRegenerate}
            onEditPrompt={handleEditPrompt}
          />
        ) : (
          <StoryCreationForm
            initialPrompt={formDraft.prompt}
            initialGenre={formDraft.genre}
            initialMood={formDraft.mood}
            initialLength={formDraft.length}
            initialFile={formDraft.file}
            isGenerating={isGenerating}
            errorMessage={error}
            onClearError={clearError}
            onSubmit={handleGenerateStory}
            onChangeDraft={updateFormDraft}
          />
        )}
      </div>
    </div>
  );
};
