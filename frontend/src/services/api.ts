import type { HealthResponse } from '../types';

// API base URL configured via Vite environment variable
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

/**
 * Custom application error with user-friendly message
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
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!response.ok) {
      let friendlyMessage = 'Unable to complete the request. Please try again.';
      try {
        const errorData = await response.json();
        if (errorData?.detail) {
          friendlyMessage = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // Fall back to status-based message if response is not JSON
        if (response.status === 404) {
          friendlyMessage = 'The requested resource was not found.';
        } else if (response.status >= 500) {
          friendlyMessage = 'The server encountered an error. Please try again later.';
        }
      }

      throw new ApiError(friendlyMessage, response.status);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Network / connectivity errors
    throw new ApiError(
      'Could not reach the backend server. Please verify that the server is running.',
      0
    );
  }
}

/**
 * API Service for StorySpark AI
 */
export const api = {
  /**
   * Check backend health status
   */
  async checkHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/api/health');
  },
};
