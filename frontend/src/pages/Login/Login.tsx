import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { Field, Input } from "../../components/ui";
import { useAuth } from "../../hooks/useAuth";

export function Login() {
  const { isAuthenticated, login, isLoggingIn, loginError } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@fretesystem.com");
  const [password, setPassword] = useState("");

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await login({ email, password });
    navigate("/dashboard");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg text-text-primary">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 p-6 rounded-lg bg-surface border border-border">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-7 h-7 rounded flex items-center justify-center text-sm font-semibold bg-state-info text-bg">F</div>
          <span className="font-semibold text-sm">frete-system</span>
        </div>
        <Field label="E-mail">
          <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </Field>
        <Field label="Senha">
          <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </Field>
        {loginError && <p className="text-xs text-state-error">{loginError.message}</p>}
        <button
          type="submit"
          disabled={isLoggingIn}
          className="w-full h-9 rounded text-sm font-medium bg-state-info text-white disabled:opacity-60"
        >
          {isLoggingIn ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
