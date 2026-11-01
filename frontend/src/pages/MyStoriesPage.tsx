import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Trash2,
  Clock,
  Calendar,
  Image as ImageIcon,
  Sparkles,
  RefreshCw,
  AlertCircle,
  ArrowLeft,
  Loader2,
  ExternalLink,
  CheckSquare,
  Square,
  X,
  AlertTriangle,
} from 'lucide-react';
import { api, ApiError } from '../services/api';
import type { Story } from '../types';
import { StoryReader } from '../components/story/StoryReader';
import { useStorySession } from '../hooks/useStorySession';

// Genre-inspired decorative spine styles for storybook-feel cards
const GENRE_ACCENTS: Record<string, { border: string; badge: string; text: string }> = {
  Fantasy: { border: 'border-t-[#C85E45]', badge: 'bg-[#FAF3EE] text-[#C85E45] border-[#F0D5C9]', text: 'text-[#C85E45]' },
  Mystery: { border: 'border-t-[#2D3154]', badge: 'bg-[#EEF1FA] text-[#2D3154] border-[#D6DBEF]', text: 'text-[#2D3154]' },
  Adventure: { border: 'border-t-[#2A6546]', badge: 'bg-[#EFF6F2] text-[#2A6546] border-[#D3E8DC]', text: 'text-[#2A6546]' },
  'Science Fiction': { border: 'border-t-[#5C457A]', badge: 'bg-[#F4EFFB] text-[#5C457A] border-[#E2D4F3]', text: 'text-[#5C457A]' },
  Romance: { border: 'border-t-[#A24867]', badge: 'bg-[#FCEDF2] text-[#A24867] border-[#F5D3E0]', text: 'text-[#A24867]' },
  Comedy: { border: 'border-t-[#B86B35]', badge: 'bg-[#FAF2EC] text-[#B86B35] border-[#F2DCCF]', text: 'text-[#B86B35]' },
  Inspirational: { border: 'border-t-[#A37B24]', badge: 'bg-[#FAF5EA] text-[#A37B24] border-[#EFE1C0]', text: 'text-[#A37B24]' },
  Fiction: { border: 'border-t-[#5A3855]', badge: 'bg-[#F7EEF6] text-[#5A3855] border-[#E8D4E6]', text: 'text-[#5A3855]' },
};

export const MyStoriesPage: React.FC = () => {
  const navigate = useNavigate();
  const { setActiveStoryDirectly } = useStorySession();

  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  // Active story opened for full reading
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);

  // Individual deletion state
  const [storyToDelete, setStoryToDelete] = useState<Story | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // Selection & Bulk Management State
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [showBulkDeleteModal, setShowBulkDeleteModal] = useState(false);
  const [showClearAllModal, setShowClearAllModal] = useState(false);
  const [clearAllConfirmText, setClearAllConfirmText] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    let isSubscribed = true;

    api.getStories()
      .then((data) => {
        if (isSubscribed) {
          setStories(data);
          setError(null);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isSubscribed) {
          const message =
            err instanceof ApiError
              ? err.message
              : 'Unable to open your stories right now. Please check your connection and try again.';
          setError(message);
          setLoading(false);
        }
      });

    return () => {
      isSubscribed = false;
    };
  }, [reloadKey]);

  const fetchStories = useCallback(() => {
    setLoading(true);
    setError(null);
    setReloadKey((prev) => prev + 1);
  }, []);

  const handleOpenStory = (story: Story) => {
    if (isSelectionMode) {
      toggleStorySelection(story.id);
      return;
    }
    setSelectedStory(story);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBackToList = () => {
    setSelectedStory(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleOpenInStudio = (story: Story) => {
    setActiveStoryDirectly(story);
    navigate('/');
  };

  // Individual Deletion
  const confirmDelete = (story: Story, e: React.MouseEvent) => {
    e.stopPropagation();
    setStoryToDelete(story);
    setDeleteError(null);
  };

  const cancelDelete = () => {
    setStoryToDelete(null);
    setDeleteError(null);
  };

  const executeDelete = async () => {
    if (!storyToDelete) return;
    setIsDeleting(true);
    setDeleteError(null);

    try {
      await api.deleteStory(storyToDelete.id);
      setStories((prev) => prev.filter((s) => s.id !== storyToDelete.id));

      if (selectedStory?.id === storyToDelete.id) {
        setSelectedStory(null);
      }

      setStoryToDelete(null);
      setFeedback({ type: 'success', message: 'Story deleted successfully.' });
      setTimeout(() => setFeedback(null), 3000);
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : 'Unable to remove this story. Please try again.';
      setDeleteError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // Selection & Bulk Management
  const toggleSelectionMode = () => {
    setIsSelectionMode((prev) => !prev);
    setSelectedIds(new Set());
    setFeedback(null);
  };

  const toggleStorySelection = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const selectAll = () => {
    setSelectedIds(new Set(stories.map((s) => s.id)));
  };

  const deselectAll = () => {
    setSelectedIds(new Set());
  };

  const executeBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    setIsDeleting(true);
    setDeleteError(null);

    try {
      const idsToDelete = Array.from(selectedIds);
      const res = await api.bulkDeleteStories(idsToDelete);
      setStories((prev) => prev.filter((s) => !selectedIds.has(s.id)));
      if (selectedStory && selectedIds.has(selectedStory.id)) {
        setSelectedStory(null);
      }
      setShowBulkDeleteModal(false);
      setSelectedIds(new Set());
      setIsSelectionMode(false);
      setFeedback({
        type: 'success',
        message: `Successfully deleted ${res.deleted_count} ${res.deleted_count === 1 ? 'story' : 'stories'}.`,
      });
      setTimeout(() => setFeedback(null), 3500);
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : 'Failed to delete selected stories. Please try again.';
      setDeleteError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  const executeClearAll = async () => {
    setIsDeleting(true);
    setDeleteError(null);

    try {
      const res = await api.clearAllStories();
      setStories([]);
      setSelectedStory(null);
      setShowClearAllModal(false);
      setClearAllConfirmText('');
      setIsSelectionMode(false);
      setSelectedIds(new Set());
      setFeedback({
        type: 'success',
        message: `Successfully cleared all ${res.deleted_count} stories from your library.`,
      });
      setTimeout(() => setFeedback(null), 3500);
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : 'Failed to clear stories. Please try again.';
      setDeleteError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="w-full flex-1 flex flex-col items-center justify-start px-4 py-8 sm:px-6 md:py-10">
      {/* If a story is selected for full reading, show StoryReader with back controls */}
      {selectedStory ? (
        <div className="w-full max-w-3xl space-y-6">
          {/* Top navigation ribbon */}
          <div className="flex flex-wrap items-center justify-between gap-3 px-1">
            <button
              type="button"
              onClick={handleBackToList}
              className="inline-flex items-center gap-2 rounded-2xl border border-[#E8DFD5] bg-[#FCFBF9] px-4 py-2 text-xs font-medium text-[#554553] hover:bg-[#F5EFEB] hover:text-[#2B1B2A] transition-colors cursor-pointer shadow-2xs"
            >
              <ArrowLeft className="h-4 w-4 text-[#C85E45]" />
              <span>Back to My Stories</span>
            </button>

            <button
              type="button"
              onClick={() => handleOpenInStudio(selectedStory)}
              className="inline-flex items-center gap-1.5 rounded-2xl bg-gradient-to-r from-[#C85E45] to-[#A24867] px-4 py-2 text-xs font-semibold text-white shadow-xs hover:from-[#B8523A] hover:to-[#913B57] transition-all cursor-pointer"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              <span>Open in Story Studio</span>
            </button>
          </div>

          <StoryReader
            story={selectedStory}
            onRegenerate={async () => {
              navigate('/');
            }}
            onEditPrompt={() => {
              navigate('/');
            }}
          />
        </div>
      ) : (
        /* Bookshelf Story Collection List */
        <div className="w-full max-w-5xl space-y-8 animate-in fade-in duration-300">
          {/* Header & Story Management Controls */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left border-b border-[#EFE8DF] pb-6">
            <div className="space-y-1">
              <h1 className="font-serif text-2xl sm:text-3xl font-bold tracking-tight text-[#2B1B2A]">
                My Stories
              </h1>
              <p className="text-xs sm:text-sm text-[#7D6B8D]">
                Your personal library of adventures, memories, and imagined worlds.
              </p>
            </div>

            {/* Management & Action Controls */}
            <div className="flex flex-wrap items-center gap-2">
              {!isSelectionMode ? (
                <>
                  <button
                    type="button"
                    onClick={fetchStories}
                    disabled={loading}
                    title="Refresh stories"
                    className="inline-flex items-center gap-1.5 rounded-2xl border border-[#E8DFD5] bg-[#FCFBF9] px-3.5 py-2 text-xs font-medium text-[#554553] hover:bg-[#F5EFEB] hover:text-[#2B1B2A] transition-colors cursor-pointer shadow-2xs disabled:opacity-50"
                  >
                    <RefreshCw className={`h-3.5 w-3.5 text-[#7D6B8D] ${loading ? 'animate-spin' : ''}`} />
                    <span>Refresh</span>
                  </button>

                  <Link
                    to="/"
                    className="inline-flex items-center gap-1.5 rounded-2xl bg-[#C85E45] px-3.5 py-2 text-xs font-semibold text-white hover:bg-[#B8523A] transition-colors cursor-pointer shadow-2xs"
                  >
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Create Story</span>
                  </Link>

                  {stories.length > 0 && (
                    <button
                      type="button"
                      onClick={toggleSelectionMode}
                      className="inline-flex items-center gap-1.5 rounded-2xl border border-[#E8DFD5] bg-[#FCFBF9] px-3.5 py-2 text-xs font-medium text-[#554553] hover:bg-[#F5EFEB] hover:text-[#2B1B2A] transition-colors cursor-pointer shadow-2xs"
                    >
                      <CheckSquare className="h-3.5 w-3.5 text-[#C85E45]" />
                      <span>Manage Stories</span>
                    </button>
                  )}
                </>
              ) : (
                <div className="flex flex-wrap items-center gap-2 bg-[#F7F2EC] p-1.5 rounded-2xl border border-[#EAE2D8]">
                  <span className="text-xs font-semibold font-serif text-[#2B1B2A] px-2">
                    {selectedIds.size} selected
                  </span>

                  <button
                    type="button"
                    onClick={selectAll}
                    disabled={selectedIds.size === stories.length}
                    className="rounded-xl bg-white px-2.5 py-1 text-xs font-medium text-[#554553] hover:text-[#2B1B2A] shadow-2xs cursor-pointer disabled:opacity-50"
                  >
                    Select All
                  </button>

                  <button
                    type="button"
                    onClick={deselectAll}
                    disabled={selectedIds.size === 0}
                    className="rounded-xl bg-white px-2.5 py-1 text-xs font-medium text-[#554553] hover:text-[#2B1B2A] shadow-2xs cursor-pointer disabled:opacity-50"
                  >
                    Deselect All
                  </button>

                  {selectedIds.size > 0 && (
                    <button
                      type="button"
                      onClick={() => {
                        setDeleteError(null);
                        setShowBulkDeleteModal(true);
                      }}
                      className="inline-flex items-center gap-1 rounded-xl bg-rose-600 px-3 py-1 text-xs font-semibold text-white hover:bg-rose-700 transition-colors cursor-pointer shadow-2xs"
                    >
                      <Trash2 className="h-3 w-3" />
                      <span>Delete Selected ({selectedIds.size})</span>
                    </button>
                  )}

                  <button
                    type="button"
                    onClick={() => {
                      setDeleteError(null);
                      setClearAllConfirmText('');
                      setShowClearAllModal(true);
                    }}
                    className="rounded-xl border border-rose-200 bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700 hover:bg-rose-100 transition-colors cursor-pointer"
                    title="Permanently remove all stories from library"
                  >
                    Clear All Stories
                  </button>

                  <button
                    type="button"
                    onClick={toggleSelectionMode}
                    className="inline-flex items-center gap-1 rounded-xl px-2 py-1 text-xs font-medium text-[#7D6B8D] hover:text-[#2B1B2A] cursor-pointer"
                  >
                    <X className="h-3.5 w-3.5" />
                    <span>Done</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Toast / Feedback Notice */}
          {feedback && (
            <div
              className={`rounded-2xl border p-3.5 text-xs animate-in fade-in duration-200 text-left flex items-center justify-between ${
                feedback.type === 'success'
                  ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
                  : 'border-rose-200 bg-[#FFF5F3] text-rose-800'
              }`}
            >
              <span>{feedback.message}</span>
              <button
                type="button"
                onClick={() => setFeedback(null)}
                className="font-bold text-xs px-1 cursor-pointer"
              >
                ✕
              </button>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="py-20 flex flex-col items-center justify-center space-y-3">
              <Loader2 className="h-8 w-8 animate-spin text-[#C85E45]" />
              <p className="font-serif text-sm text-[#7D6B8D]">
                Gathering your stories...
              </p>
            </div>
          )}

          {/* Error State */}
          {!loading && error && (
            <div className="rounded-3xl border border-rose-200 bg-[#FFF5F3] p-8 text-center space-y-4 max-w-md mx-auto">
              <div className="h-10 w-10 rounded-2xl bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
                <AlertCircle className="h-5 w-5" />
              </div>
              <p className="text-xs text-rose-800 leading-relaxed">{error}</p>
              <button
                type="button"
                onClick={fetchStories}
                className="inline-flex items-center gap-1.5 rounded-2xl bg-rose-600 px-4 py-2 text-xs font-medium text-white hover:bg-rose-700 transition-colors cursor-pointer shadow-xs"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                <span>Try again</span>
              </button>
            </div>
          )}

          {/* Empty State */}
          {!loading && !error && stories.length === 0 && (
            <div className="rounded-3xl border border-[#E8DFD5] bg-white p-12 text-center space-y-5 max-w-lg mx-auto shadow-sm">
              <div className="h-14 w-14 rounded-3xl bg-[#FAF0EB] text-[#C85E45] flex items-center justify-center mx-auto shadow-xs">
                <BookOpen className="h-7 w-7" />
              </div>
              <div className="space-y-1.5">
                <h3 className="font-serif text-lg font-bold text-[#2B1B2A]">
                  Your story collection is waiting for its first adventure.
                </h3>
                <p className="text-xs text-[#7A6C79] max-w-sm mx-auto leading-relaxed">
                  Start with a written idea, upload an image, or blend both together to create your first story.
                </p>
              </div>
              <div>
                <Link
                  to="/"
                  className="inline-flex items-center gap-2 rounded-2xl bg-[#C85E45] px-6 py-2.5 text-xs font-semibold text-white hover:bg-[#B8523A] transition-colors cursor-pointer shadow-xs"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>Create a story</span>
                </Link>
              </div>
            </div>
          )}

          {/* Story Cards Grid */}
          {!loading && !error && stories.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 text-left">
              {stories.map((story) => {
                const accent = GENRE_ACCENTS[story.genre] || GENRE_ACCENTS.Fantasy;
                const wordCount = story.content.trim().split(/\s+/).filter(Boolean).length;
                const readingTime = Math.max(1, Math.ceil(wordCount / 200));
                const isSelected = selectedIds.has(story.id);

                return (
                  <article
                    key={story.id}
                    onClick={() => handleOpenStory(story)}
                    className={`group relative rounded-3xl border bg-white p-5 shadow-2xs hover:shadow-md transition-all cursor-pointer flex flex-col justify-between border-t-4 ${
                      accent.border
                    } ${
                      isSelected
                        ? 'ring-2 ring-[#C85E45] bg-[#FAF4EE] border-[#C85E45]'
                        : 'border-[#E8DFD5] hover:border-[#D4C4B6]'
                    }`}
                  >
                    <div>
                      {/* Top ribbon: Selection Checkbox or Genre Badge + Delete */}
                      <div className="flex items-center justify-between gap-2 mb-3">
                        <div className="flex items-center gap-1.5">
                          {isSelectionMode && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleStorySelection(story.id);
                              }}
                              className="mr-1 text-[#C85E45] p-0.5 cursor-pointer"
                              aria-label={isSelected ? 'Deselect story' : 'Select story'}
                            >
                              {isSelected ? (
                                <CheckSquare className="h-4 w-4 text-[#C85E45]" />
                              ) : (
                                <Square className="h-4 w-4 text-[#A697A5]" />
                              )}
                            </button>
                          )}

                          <span
                            className={`inline-flex items-center rounded-xl border px-2.5 py-0.5 text-[11px] font-serif font-semibold ${accent.badge}`}
                          >
                            {story.genre}
                          </span>

                          {story.image_filename && (
                            <span className="inline-flex items-center gap-1 rounded-xl bg-[#EFF6F2] border border-[#D3E8DC] px-2 py-0.5 text-[11px] text-[#2A6546]">
                              <ImageIcon className="h-2.5 w-2.5" />
                              <span>Visual</span>
                            </span>
                          )}
                        </div>

                        {/* Individual Delete Button (hidden in selection mode) */}
                        {!isSelectionMode && (
                          <button
                            type="button"
                            onClick={(e) => confirmDelete(story, e)}
                            title="Remove from collection"
                            className="text-[#A697A5] hover:text-rose-600 p-1.5 rounded-xl hover:bg-rose-50 transition-colors cursor-pointer"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        )}
                      </div>

                      {/* Title */}
                      <h3 className="font-serif text-base sm:text-lg font-bold text-[#2B1B2A] group-hover:text-[#C85E45] transition-colors line-clamp-1 leading-snug">
                        {story.title}
                      </h3>

                      {/* Content Preview Snippet */}
                      <p className="text-xs text-[#615060] leading-relaxed line-clamp-2 mt-1.5">
                        {story.content_preview || story.content.slice(0, 110)}
                      </p>
                    </div>

                    {/* Metadata Footer */}
                    <div className="mt-4 pt-3 border-t border-[#EFE8DF] flex items-center justify-between text-xs text-[#7A6C79]">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3 text-[#A697A5]" />
                        <span>{readingTime} min • {wordCount} words</span>
                      </span>
                      <span className="flex items-center gap-1 font-mono text-[11px]">
                        <Calendar className="h-3 w-3 text-[#A697A5]" />
                        <span>{new Date(story.created_at).toLocaleDateString()}</span>
                      </span>
                    </div>
                  </article>
                );
              })}
            </div>
          )}

          {/* Individual Delete Confirmation Modal */}
          {storyToDelete && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#2B1B2A]/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
              <div className="w-full max-w-md rounded-3xl border border-[#E8DFD5] bg-white p-7 shadow-xl space-y-4 text-left">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-2xl bg-[#FFF5F3] border border-rose-200 flex items-center justify-center text-rose-500 shrink-0">
                    <Trash2 className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-serif text-base font-bold text-[#2B1B2A]">
                      Remove from collection?
                    </h3>
                    <p className="text-xs text-[#7A6C79]">This action cannot be undone.</p>
                  </div>
                </div>

                <p className="text-xs text-[#554553] leading-relaxed">
                  Are you sure you want to remove{' '}
                  <span className="font-serif font-bold text-[#2B1B2A]">"{storyToDelete.title}"</span> from your story collection?
                </p>

                {deleteError && (
                  <div className="rounded-xl border border-rose-200 bg-[#FFF5F3] p-2.5 text-xs text-rose-700">
                    {deleteError}
                  </div>
                )}

                <div className="flex items-center justify-end gap-2.5 pt-2">
                  <button
                    type="button"
                    onClick={cancelDelete}
                    disabled={isDeleting}
                    className="rounded-2xl border border-[#E8DFD5] bg-[#FCFBF9] px-4 py-2 text-xs font-medium text-[#554553] hover:bg-[#F5EFEB] hover:text-[#2B1B2A] transition-colors cursor-pointer"
                  >
                    Keep story
                  </button>
                  <button
                    type="button"
                    onClick={executeDelete}
                    disabled={isDeleting}
                    className="inline-flex items-center gap-1.5 rounded-2xl bg-rose-600 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-700 transition-colors cursor-pointer disabled:opacity-50"
                  >
                    {isDeleting && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                    <span>{isDeleting ? 'Removing...' : 'Remove story'}</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Bulk Delete Selected Confirmation Modal */}
          {showBulkDeleteModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#2B1B2A]/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
              <div className="w-full max-w-md rounded-3xl border border-[#E8DFD5] bg-white p-7 shadow-xl space-y-4 text-left">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-2xl bg-[#FFF5F3] border border-rose-200 flex items-center justify-center text-rose-500 shrink-0">
                    <Trash2 className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-serif text-base font-bold text-[#2B1B2A]">
                      Delete {selectedIds.size} {selectedIds.size === 1 ? 'story' : 'stories'}?
                    </h3>
                    <p className="text-xs text-[#7A6C79]">These stories will be permanently removed.</p>
                  </div>
                </div>

                <p className="text-xs text-[#554553] leading-relaxed">
                  Are you sure you want to permanently delete the <span className="font-bold text-[#2B1B2A]">{selectedIds.size}</span> selected {selectedIds.size === 1 ? 'story' : 'stories'}? This action cannot be reversed.
                </p>

                {deleteError && (
                  <div className="rounded-xl border border-rose-200 bg-[#FFF5F3] p-2.5 text-xs text-rose-700">
                    {deleteError}
                  </div>
                )}

                <div className="flex items-center justify-end gap-2.5 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowBulkDeleteModal(false)}
                    disabled={isDeleting}
                    className="rounded-2xl border border-[#E8DFD5] bg-[#FCFBF9] px-4 py-2 text-xs font-medium text-[#554553] hover:bg-[#F5EFEB] hover:text-[#2B1B2A] transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={executeBulkDelete}
                    disabled={isDeleting}
                    className="inline-flex items-center gap-1.5 rounded-2xl bg-rose-600 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-700 transition-colors cursor-pointer disabled:opacity-50"
                  >
                    {isDeleting && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                    <span>{isDeleting ? 'Deleting...' : `Delete ${selectedIds.size} ${selectedIds.size === 1 ? 'story' : 'stories'}`}</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Clear All Stories Confirmation Modal */}
          {showClearAllModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#2B1B2A]/50 backdrop-blur-xs p-4 animate-in fade-in duration-150">
              <div className="w-full max-w-md rounded-3xl border border-rose-300 bg-white p-7 shadow-2xl space-y-4 text-left">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-2xl bg-rose-100 border border-rose-300 flex items-center justify-center text-rose-600 shrink-0">
                    <AlertTriangle className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-serif text-base font-bold text-rose-900">
                      Clear Entire Story Collection?
                    </h3>
                    <p className="text-xs text-rose-600 font-semibold">Danger: Permanent Action</p>
                  </div>
                </div>

                <p className="text-xs text-[#554553] leading-relaxed">
                  This will permanently delete all <span className="font-bold text-[#2B1B2A]">{stories.length}</span> saved stories in your library. Once cleared, they cannot be recovered.
                </p>

                <div className="space-y-1.5 pt-1">
                  <label htmlFor="clear-all-input" className="text-[11px] font-semibold text-[#554553] block">
                    To confirm, please type <span className="font-mono text-rose-700 font-bold">DELETE ALL</span> below:
                  </label>
                  <input
                    id="clear-all-input"
                    type="text"
                    value={clearAllConfirmText}
                    onChange={(e) => setClearAllConfirmText(e.target.value)}
                    placeholder="Type DELETE ALL to confirm"
                    className="w-full rounded-xl border border-[#E8DFD5] px-3.5 py-2 text-xs font-mono focus:border-rose-500 focus:outline-none"
                  />
                </div>

                {deleteError && (
                  <div className="rounded-xl border border-rose-200 bg-[#FFF5F3] p-2.5 text-xs text-rose-700">
                    {deleteError}
                  </div>
                )}

                <div className="flex items-center justify-end gap-2.5 pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowClearAllModal(false);
                      setClearAllConfirmText('');
                    }}
                    disabled={isDeleting}
                    className="rounded-2xl border border-[#E8DFD5] bg-[#FCFBF9] px-4 py-2 text-xs font-medium text-[#554553] hover:bg-[#F5EFEB] hover:text-[#2B1B2A] transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={executeClearAll}
                    disabled={isDeleting || clearAllConfirmText.trim() !== 'DELETE ALL'}
                    className="inline-flex items-center gap-1.5 rounded-2xl bg-rose-700 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-800 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shadow-xs"
                  >
                    {isDeleting && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                    <span>{isDeleting ? 'Clearing...' : 'Permanently Clear All'}</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
