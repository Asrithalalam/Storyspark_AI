import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Feather, Sparkles } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex flex-1 min-h-[60vh] flex-col items-center justify-center p-6 text-center">
        <div className="relative mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#C85E45] to-[#8E7C9D] text-white shadow-md shadow-[#C85E45]/20 ring-1 ring-white/60 animate-pulse">
          <Feather className="h-8 w-8 animate-bounce text-white" />
          <div className="absolute -top-1 -right-1 text-amber-300">
            <Sparkles className="h-4 w-4" />
          </div>
        </div>
        <h3 className="font-serif text-lg font-bold text-[#2B1B2A]">Opening StorySpark AI...</h3>
        <p className="mt-1 font-serif text-xs italic text-[#7D6B8D]">
          Verifying your storyteller credentials...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login preserving the attempted route in state
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
