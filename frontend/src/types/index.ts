/**
 * Types and taxonomy for StorySpark AI
 */

export const ALLOWED_GENRES = [
  'Fantasy',
  'Adventure',
  'Mystery',
  'Comedy',
  'Romance',
  'Science Fiction',
  'Inspirational',
  'Fiction',
] as const;

export type Genre = (typeof ALLOWED_GENRES)[number];

export const ALLOWED_MOODS = [
  'Happy',
  'Emotional',
  'Mysterious',
  'Exciting',
  'Funny',
  'Peaceful',
  'Suspenseful',
] as const;

export type Mood = (typeof ALLOWED_MOODS)[number];

export const ALLOWED_LENGTHS = [
  'Short',
  'Medium',
  'Long',
] as const;

export type StoryLength = (typeof ALLOWED_LENGTHS)[number];

export interface LengthOption {
  value: StoryLength;
  label: string;
  targetRange: string;
  description: string;
}

export const LENGTH_OPTIONS: LengthOption[] = [
  {
    value: 'Short',
    label: 'Short',
    targetRange: '150–200 words',
    description: 'Quick, punchy flash fiction.',
  },
  {
    value: 'Medium',
    label: 'Medium',
    targetRange: '250–350 words',
    description: 'Balanced story with developed scenes.',
  },
  {
    value: 'Long',
    label: 'Long',
    targetRange: '450–550 words',
    description: 'Rich narrative with deep atmosphere.',
  },
];

export interface SuggestedPrompt {
  id: string;
  label: string;
  prompt: string;
  genre: Genre;
  mood: Mood;
}

export const SUGGESTED_PROMPTS: SuggestedPrompt[] = [
  {
    id: 'forgotten-letter',
    label: 'A forgotten letter',
    prompt: 'A forgotten letter reveals a family secret.',
    genre: 'Mystery',
    mood: 'Mysterious',
  },
  {
    id: 'tiny-bird',
    label: 'A tiny bird',
    prompt: 'A tiny bird discovers a world beyond its garden.',
    genre: 'Adventure',
    mood: 'Peaceful',
  },
  {
    id: 'mysterious-photograph',
    label: 'A mysterious photograph',
    prompt: 'A mysterious photograph leads to an unexpected adventure.',
    genre: 'Adventure',
    mood: 'Exciting',
  },
];

export interface GenerateStoryRequest {
  prompt?: string;
  image_base64?: string;
  genre: string;
  mood: string;
  length: string;
}

export interface Story {
  id: number;
  title: string;
  content: string;
  prompt: string | null;
  image_filename: string | null;
  genre: string;
  mood: string;
  length: string;
  created_at: string;
  content_preview?: string;
}

export interface StoryDeleteResponse {
  message: string;
  id: number;
}

export interface BulkDeleteStoriesResponse {
  message: string;
  deleted_count: number;
  deleted_ids: number[];
}

export interface ClearAllStoriesResponse {
  message: string;
  deleted_count: number;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  auth_provider: string;
  created_at: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string | null;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface MessageResponse {
  message: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<User>;
  register: (payload: RegisterPayload) => Promise<User>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<User | null>;
}

export interface HealthResponse {
  status: string;
  message: string;
  timestamp: string;
}

export type ConnectionStatus = 'checking' | 'connected' | 'disconnected';

export interface BackendConnectionState {
  status: ConnectionStatus;
  data: HealthResponse | null;
  errorMessage: string | null;
  lastChecked: Date | null;
}
