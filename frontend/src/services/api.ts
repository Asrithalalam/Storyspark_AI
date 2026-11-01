import type {
  BulkDeleteStoriesResponse,
  ClearAllStoriesResponse,
  GenerateStoryRequest,
  HealthResponse,
  LoginPayload,
  MessageResponse,
  RegisterPayload,
  Story,
  User,
} from '../types';

// API base URL configured via Vite environment variable
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

/**
 * Custom application error with user-friendly message and status code
 */
export class ApiError extends Error {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
  }
}

/**
 * Standard request helper with user-friendly error wrapping
 */
async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  try {
    const response = await fetch(url, {
      credentials: 'include',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!response.ok) {
      let friendlyMessage = "We couldn't process your request. Please try again.";

      try {
        const errorData = await response.json();
        if (response.status === 413) {
          friendlyMessage = 'Your image is too large. Please upload an image smaller than 5 MB.';
        } else if (response.status === 429) {
          friendlyMessage = "We're experiencing high demand right now. Please wait a moment and try again.";
        } else if (
          typeof errorData?.detail === 'string' &&
          errorData.detail.length < 180 &&
          !errorData.detail.includes('Traceback') &&
          !errorData.detail.includes('Exception') &&
          !errorData.detail.includes('500') &&
          !errorData.detail.includes('Internal')
        ) {
          friendlyMessage = errorData.detail;
        } else if (Array.isArray(errorData?.detail) && errorData.detail.length > 0) {
          const firstErr = errorData.detail[0];
          friendlyMessage = typeof firstErr?.msg === 'string' ? firstErr.msg : 'Invalid input provided.';
        } else if (response.status === 401) {
          friendlyMessage = 'Invalid email or password.';
        } else if (response.status === 409) {
          friendlyMessage = 'An account with this email already exists.';
        } else if (response.status === 503) {
          friendlyMessage = 'The requested service is temporarily unavailable. Please try again shortly.';
        }
      } catch {
        if (response.status === 413) {
          friendlyMessage = 'Your image is too large. Please upload an image smaller than 5 MB.';
        } else if (response.status === 401) {
          friendlyMessage = 'Please sign in to continue.';
        } else if (response.status === 409) {
          friendlyMessage = 'An account with this email already exists.';
        } else if (response.status === 429) {
          friendlyMessage = "We're experiencing high demand right now. Please wait a moment and try again.";
        } else {
          friendlyMessage = "We couldn't process your request. Please try again.";
        }
      }

      throw new ApiError(friendlyMessage, response.status);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Network / connectivity errors - friendly and non-technical
    throw new ApiError(
      "We couldn't reach the server. Please check your connection and try again.",
      0
    );
  }
}

/**
 * API Service for StorySpark AI
 */
export const api = {
  /**
   * Check backend health status (Preserved from Phase 2)
   */
  async checkHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/api/health');
  },

  /**
   * Generate a story with Gemma 4 and save it to SQLite (Phase 5)
   */
  async generateStory(payload: GenerateStoryRequest): Promise<Story> {
    return request<Story>('/api/stories/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Retrieve saved stories from SQLite database (Phase 3 & Navigation)
   */
  async getStories(skip = 0, limit = 100): Promise<Story[]> {
    return request<Story[]>(`/api/stories?skip=${skip}&limit=${limit}`);
  },

  /**
   * Retrieve a single story by ID
   */
  async getStoryById(id: number): Promise<Story> {
    return request<Story>(`/api/stories/${id}`);
  },

  /**
   * Permanently delete a story from SQLite storage by ID
   */
  async deleteStory(id: number): Promise<{ message: string; id: number }> {
    return request<{ message: string; id: number }>(`/api/stories/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Bulk delete multiple stories transactionally by their IDs
   */
  async bulkDeleteStories(storyIds: number[]): Promise<BulkDeleteStoriesResponse> {
    return request<BulkDeleteStoriesResponse>('/api/stories/bulk-delete', {
      method: 'POST',
      body: JSON.stringify({ story_ids: storyIds }),
    });
  },

  /**
   * Transactionally clear all stories from the collection
   */
  async clearAllStories(): Promise<ClearAllStoriesResponse> {
    return request<ClearAllStoriesResponse>('/api/stories/clear-all', {
      method: 'POST',
    });
  },

  // ==========================================================================
  // Authentication & Session Endpoints
  // ==========================================================================

  /**
   * Register a new user with email, password, and optional full name.
   * On success, sets HttpOnly session cookie and returns user profile.
   */
  async register(payload: RegisterPayload): Promise<User> {
    return request<User>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Authenticate user with email and password.
   * On success, sets HttpOnly session cookie and returns user profile.
   */
  async login(payload: LoginPayload): Promise<User> {
    return request<User>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Sign out the current user and instruct the browser to clear the session cookie.
   */
  async logout(): Promise<MessageResponse> {
    return request<MessageResponse>('/api/auth/logout', {
      method: 'POST',
    });
  },

  /**
   * Fetch the currently authenticated user's profile from the session cookie.
   * Throws ApiError with status 401 if unauthenticated.
   */
  async getCurrentUser(): Promise<User> {
    return request<User>('/api/auth/me', {
      method: 'GET',
    });
  },
};
