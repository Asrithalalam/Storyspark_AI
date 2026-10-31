/**
 * Types for StorySpark AI
 */

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
