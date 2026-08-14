import type { PropsWithChildren } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function ProtectedRoute({ children }: PropsWithChildren) {
  const { isAuthenticated, isCheckingAuth } = useAuth();
  if (isCheckingAuth) return <div className="min-h-screen bg-bg" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
