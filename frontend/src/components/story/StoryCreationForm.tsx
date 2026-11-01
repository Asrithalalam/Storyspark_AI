import React, { useState } from 'react';
import { AlertTriangle, Loader2, PenLine, Image as ImageIcon, Layers, Sparkles } from 'lucide-react';
import { PromptInput } from './PromptInput';
import { ImageUpload } from './ImageUpload';
import { GenreSelector } from './GenreSelector';
import { MoodSelector } from './MoodSelector';
import { LengthSelector } from './LengthSelector';
import type { GenerateStoryRequest, Genre, Mood, StoryLength, SuggestedPrompt } from '../../types';

interface StoryCreationFormProps {
  initialPrompt?: string;
  initialGenre?: string;
  initialMood?: string;
  initialLength?: string;
  initialFile?: File | null;
  isGenerating: boolean;
  errorMessage: string | null;
  onClearError: () => void;
  onSubmit: (request: GenerateStoryRequest, file: File | null) => Promise<void>;
  onChangeDraft?: (draft: {
    prompt: string;
    genre: Genre;
    mood: Mood;
    length: StoryLength;
    file: File | null;
  }) => void;
}

type InputMode = 'written' | 'image' | 'both';

// Convert File to base64 Data URL only at generation time
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result);
      } else {
        reject(new Error('Failed to read image as base64 string.'));
      }
    };
    reader.onerror = () => reject(new Error('File reading error.'));
    reader.readAsDataURL(file);
  });
}

export const StoryCreationForm: React.FC<StoryCreationFormProps> = ({
  initialPrompt = '',
  initialGenre = 'Fantasy',
  initialMood = 'Mysterious',
  initialLength = 'Short',
  initialFile = null,
  isGenerating,
  errorMessage,
  onClearError,
  onSubmit,
  onChangeDraft,
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [selectedFile, setSelectedFile] = useState<File | null>(initialFile);
  const [genre, setGenre] = useState<Genre>(initialGenre as Genre);
  const [mood, setMood] = useState<Mood>(initialMood as Mood);
  const [length, setLength] = useState<StoryLength>(initialLength as StoryLength);
  const [clientError, setClientError] = useState<string | null>(null);

  // Creative input mode selection: Written Idea, Visual Inspiration, or Both
  const [inputMode, setInputMode] = useState<InputMode>(() => {
    if (initialPrompt && initialFile) return 'both';
    if (initialFile) return 'image';
    return 'written';
  });

  const hasPrompt = Boolean(prompt.trim());
  const hasImage = Boolean(selectedFile);

  const canSubmit =
    !isGenerating &&
    ((inputMode === 'written' && hasPrompt) ||
      (inputMode === 'image' && hasImage) ||
      (inputMode === 'both' && (hasPrompt || hasImage)));

  const handleSelectSuggestion = (suggestion: SuggestedPrompt) => {
    setPrompt(suggestion.prompt);
    setGenre(suggestion.genre);
    setMood(suggestion.mood);
    setClientError(null);
    onClearError();
    onChangeDraft?.({
      prompt: suggestion.prompt,
      genre: suggestion.genre,
      mood: suggestion.mood,
      length,
      file: selectedFile,
    });
  };

  const handlePromptChange = (val: string) => {
    setPrompt(val);
    if (clientError) setClientError(null);
    onChangeDraft?.({ prompt: val, genre, mood, length, file: selectedFile });
  };

  const handleFileChange = (f: File | null) => {
    setSelectedFile(f);
    if (clientError) setClientError(null);
    onChangeDraft?.({ prompt, genre, mood, length, file: f });
  };

  const handleGenreChange = (g: Genre) => {
    setGenre(g);
    onChangeDraft?.({ prompt, genre: g, mood, length, file: selectedFile });
  };

  const handleMoodChange = (m: Mood) => {
    setMood(m);
    onChangeDraft?.({ prompt, genre, mood: m, length, file: selectedFile });
  };

  const handleLengthChange = (l: StoryLength) => {
    setLength(l);
    onChangeDraft?.({ prompt, genre, mood, length: l, file: selectedFile });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) {
      if (inputMode === 'written' && !hasPrompt) {
        setClientError('Your story starts with an idea. Add a few words to begin.');
      } else if (inputMode === 'image' && !hasImage) {
        setClientError('Please upload an image to begin.');
      } else if (inputMode === 'both' && !hasPrompt && !hasImage) {
        setClientError('Please provide a written idea, an image, or both to begin.');
      }
      return;
    }

    setClientError(null);
    onClearError();

    try {
      let imageBase64: string | undefined = undefined;
      const fileToSend = inputMode === 'written' ? null : selectedFile;
      const promptToSend = inputMode === 'image' ? undefined : (prompt.trim() || undefined);

      if (fileToSend) {
        imageBase64 = await fileToBase64(fileToSend);
      }

      await onSubmit(
        {
          prompt: promptToSend,
          image_base64: imageBase64,
          genre,
          mood,
          length,
        },
        fileToSend
      );
    } catch (err) {
      setClientError(
        err instanceof Error ? err.message : 'Unable to prepare your image. Please try again.'
      );
    }
  };

  const displayError = clientError || errorMessage;

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-3xl rounded-3xl border border-[#E8DFD5] bg-white p-6 sm:p-9 shadow-[0_8px_30px_rgb(43,27,42,0.04)] space-y-7 text-left"
    >
      {/* Short, elegant section heading */}
      <div className="pb-2 border-b border-[#EFE8DF] flex items-center justify-between">
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-[#2B1B2A]">
          Create Your Story
        </h2>
      </div>

      {/* Friendly error alert banner */}
      {displayError && (
        <div className="flex items-start gap-2.5 rounded-2xl border border-rose-200 bg-[#FFF5F3] p-4 text-xs text-rose-800 animate-in fade-in">
          <AlertTriangle className="h-4 w-4 shrink-0 text-rose-500 mt-0.5" />
          <div className="flex-1 font-medium leading-relaxed">
            <span>{displayError}</span>
          </div>
          <button
            type="button"
            onClick={() => {
              setClientError(null);
              onClearError();
            }}
            className="text-rose-600 hover:text-rose-800 text-xs px-1 font-semibold cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* 3 Creative Input Modes Segmented Selector */}
      <div className="space-y-1 text-center">
        <label className="font-serif text-xs font-semibold text-[#7D6B8D] uppercase tracking-wider block mb-2">
          How would you like to start?
        </label>
        <div className="flex rounded-2xl border border-[#EAE2D8] bg-[#F7F2EC] p-1 max-w-md mx-auto">
          <button
            type="button"
            onClick={() => setInputMode('written')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-sans font-medium transition-all cursor-pointer ${
              inputMode === 'written'
                ? 'bg-white text-[#C85E45] font-semibold shadow-xs'
                : 'text-[#6A5868] hover:text-[#2B1B2A]'
            }`}
          >
            <PenLine className="h-3.5 w-3.5" />
            <span>Written Idea</span>
          </button>

          <button
            type="button"
            onClick={() => setInputMode('image')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-sans font-medium transition-all cursor-pointer ${
              inputMode === 'image'
                ? 'bg-white text-[#C85E45] font-semibold shadow-xs'
                : 'text-[#6A5868] hover:text-[#2B1B2A]'
            }`}
          >
            <ImageIcon className="h-3.5 w-3.5" />
            <span>Visual Inspiration</span>
          </button>

          <button
            type="button"
            onClick={() => setInputMode('both')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-sans font-medium transition-all cursor-pointer ${
              inputMode === 'both'
                ? 'bg-white text-[#C85E45] font-semibold shadow-xs'
                : 'text-[#6A5868] hover:text-[#2B1B2A]'
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Visual Inspiration + Idea</span>
          </button>
        </div>
      </div>

      {/* Input Fields according to active mode */}
      {(inputMode === 'written' || inputMode === 'both') && (
        <PromptInput
          value={prompt}
          onChange={handlePromptChange}
          onSelectSuggestion={handleSelectSuggestion}
          disabled={isGenerating}
        />
      )}

      {(inputMode === 'image' || inputMode === 'both') && (
        <ImageUpload
          file={selectedFile}
          onSelectFile={handleFileChange}
          disabled={isGenerating}
        />
      )}

      {/* Genre Selector with artistic motifs */}
      <GenreSelector
        value={genre}
        onChange={handleGenreChange}
        disabled={isGenerating}
      />

      {/* Mood Selector */}
      <MoodSelector
        value={mood}
        onChange={handleMoodChange}
        disabled={isGenerating}
      />

      {/* Length Selector */}
      <LengthSelector
        value={length}
        onChange={handleLengthChange}
        disabled={isGenerating}
      />

      {/* Submit Button */}
      <div className="pt-2">
        <button
          type="submit"
          disabled={!canSubmit}
          className="relative flex w-full items-center justify-center gap-2.5 rounded-2xl bg-gradient-to-r from-[#C85E45] to-[#A24867] hover:from-[#B8523A] hover:to-[#913B57] active:scale-[0.99] py-4 px-6 text-sm font-semibold text-white shadow-md shadow-[#C85E45]/20 transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none"
        >
          {isGenerating ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-white" />
              <span>Gathering your ideas into a story...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              <span>Generate Story</span>
            </>
          )}
        </button>

        {isGenerating && (
          <p className="mt-2.5 text-center text-xs text-[#7A6C79] font-serif italic animate-pulse">
            Weaving your characters, scenes, and atmosphere. This usually takes a moment...
          </p>
        )}
      </div>
    </form>
  );
};
