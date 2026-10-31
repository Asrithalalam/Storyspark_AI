import { useState, useEffect, useCallback } from 'react';
import { api, ApiError } from '../services/api';
import type { BackendConnectionState } from '../types';

export function useBackendHealth() {
  const [state, setState] = useState<BackendConnectionState>({
    status: 'checking',
    data: null,
    errorMessage: null,
    lastChecked: null,
  });

  const checkConnection = useCallback(async () => {
    setState((prev) => ({ ...prev, status: 'checking', errorMessage: null }));

    try {
      const data = await api.checkHealth();
      setState({
        status: 'connected',
        data,
        errorMessage: null,
        lastChecked: new Date(),
      });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : 'Unable to connect to the backend server.';
      setState({
        status: 'disconnected',
        data: null,
        errorMessage: message,
        lastChecked: new Date(),
      });
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    async function initialCheck() {
      try {
        const data = await api.checkHealth();
        if (isMounted) {
          setState({
            status: 'connected',
            data,
            errorMessage: null,
            lastChecked: new Date(),
          });
        }
      } catch (err) {
        if (isMounted) {
          const message =
            err instanceof ApiError
              ? err.message
              : 'Unable to connect to the backend server.';
          setState({
            status: 'disconnected',
            data: null,
            errorMessage: message,
            lastChecked: new Date(),
          });
        }
      }
    }

    void initialCheck();

    return () => {
      isMounted = false;
    };
  }, []);

  return {
    ...state,
    isChecking: state.status === 'checking',
    refresh: checkConnection,
  };
}
