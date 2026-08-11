import type { PropsWithChildren } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function ProtectedRoute({ children }: PropsWithChildren) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
